#!/usr/bin/env python3
"""Exercise deployed-style security rules in a temporary local Rill runtime.

Uses the exact security blocks in this project's metrics files and synthetic
rows. No cloud credentials, project writes, or external data downloads are used.
The unsigned attributes token is supported only by local Rill Developer.
"""
import base64
import json
from pathlib import Path
import re
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request

PROJECT = Path(__file__).resolve().parents[1]
ROWS = [
    ("Grocery Outlet", "damedetrefle.com", 10),
    ("Grocery Outlet", "news.example", 20),
    ("Chipotle", "damedetrefle.com", 30),
    ("Chipotle", "news.example", 40),
    ("O'Reilly", "quote's.example", 50),
    ("", "", 60),
]


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def token(attributes):
    def encode(value):
        return base64.urlsafe_b64encode(json.dumps(value).encode()).decode().rstrip("=")
    return encode({"alg": "none", "typ": "JWT"}) + "." + encode({"attr": attributes}) + "."


def security_block(path):
    match = re.search(r"(?ms)^security:\n.*?(?=^\S|\Z)", path.read_text())
    if not match:
        raise AssertionError(f"Missing security block: {path.name}")
    return match.group().rstrip() + "\n"


def sql_string(value):
    return "'" + value.replace("'", "''") + "'"


def main():
    if not shutil.which("rill"):
        raise SystemExit("Install the Rill CLI before running this check.")
    sources = sorted((PROJECT / "metrics").glob("*.yaml"))
    policies = {path.stem: security_block(path) for path in sources}
    with tempfile.TemporaryDirectory(prefix="embed-security-") as directory:
        fixture = Path(directory)
        features = re.search(r"(?ms)^features:\n.*?(?=^\S|\Z)", (PROJECT / "rill.yaml").read_text()).group()
        (fixture / "rill.yaml").write_text("compiler: rillv1\nolap_connector: duckdb\n" + features)
        values = ",\n".join("(" + sql_string(a) + ", " + sql_string(d) + ", " + str(n) + ")" for a, d, n in ROWS)
        (fixture / "fixture_data.sql").write_text(
            "-- @materialize: true\nSELECT *, current_timestamp AS __time, 5 AS imp_cnt, 1.5 AS bid_floor, 'bucket' AS bid_floor_bucket, 'auction' AS auction_type\n"
            "FROM (VALUES " + values + ") AS data(advertiser_name, app_site_domain, bid_cnt)\n"
        )
        for name, policy in policies.items():
            bids = name == "bids_metrics"
            fields = """dimensions:
  - name: sites_domain
    column: app_site_domain
  - name: advertiser_name
    column: advertiser_name
  - name: bid_floor_bucket
    column: bid_floor_bucket
  - name: auction_type
    column: auction_type
measures:
  - name: total_bids
    expression: sum(bid_cnt)
  - name: impressions
    expression: sum(imp_cnt)
  - name: win_rate
    expression: sum(imp_cnt) / sum(bid_cnt)
  - name: bids_7day_rolling_avg
    expression: avg(bid_cnt)
  - name: avg_bid_floor
    expression: avg(bid_floor)
""" if bids else """dimensions:
  - name: app_site_domain
    column: app_site_domain
measures:
  - name: requests
    expression: sum(bid_cnt)
"""
            (fixture / (name + ".yaml")).write_text("version: 1\ntype: metrics_view\nmodel: fixture_data\ntimeseries: __time\n" + policy + fields)
        port, grpc_port = free_port(), free_port()
        with (fixture / "runtime.log").open("w+") as log:
            runtime = subprocess.Popen([
                "rill", "start", str(fixture), "--no-open", "--no-ui", "--pull-env=false",
                "--port", str(port), "--port-grpc", str(grpc_port),
            ], stdout=log, stderr=subprocess.STDOUT)
            try:
                def query(name, attributes):
                    bids = name == "bids_metrics"
                    body = {"dimensions": [{"name": "advertiser_name"}, {"name": "sites_domain"}] if bids else [{"name": "app_site_domain"}],
                            "measures": [{"name": "total_bids" if bids else "requests"}], "limit": 100}
                    request = urllib.request.Request(
                        f"http://127.0.0.1:{port}/v1/instances/default/queries/metrics-views/{name}/aggregation",
                        data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "Authorization": "Bearer " + token(attributes)},
                    )
                    try:
                        with urllib.request.urlopen(request, timeout=10) as response:
                            return response.status, json.load(response)
                    except urllib.error.HTTPError as error:
                        return error.code, json.load(error)

                deadline = time.monotonic() + 90
                while True:
                    if runtime.poll() is not None:
                        log.seek(0)
                        raise AssertionError("Local runtime exited: " + log.read()[-6000:])
                    try:
                        ready = all(query(name, {"email": "viewer@example.com", "admin": False})[0] == 200 for name in policies)
                        if ready:
                            break
                    except (OSError, TimeoutError):
                        pass
                    if time.monotonic() > deadline:
                        log.seek(0)
                        raise AssertionError("Local runtime did not reconcile: " + log.read()[-6000:])
                    time.sleep(0.3)
                print("Local runtime ready; querying exact source security blocks.", flush=True)
                def resolved_flags(attributes):
                    request = urllib.request.Request(
                        f"http://127.0.0.1:{port}/v1/instances/default",
                        headers={"Authorization": "Bearer " + token(attributes)},
                    )
                    with urllib.request.urlopen(request, timeout=10) as response:
                        return json.load(response)["instance"]["featureFlags"]

                def camel(key):
                    head, *rest = key.split("_")
                    return head + "".join(part.title() for part in rest)

                # Every flag in rill.yaml must keep its fallback without an override and follow a signed boolean override.
                templates = dict(re.findall(r"""(?m)^  ([a-z_]+): '\{\{ if hasKey \.user "feature_\1" \}\}.*\{\{ else \}\}(.*)\{\{ end \}\}'$""", features))
                assert templates and len(templates) == len(re.findall(r"(?m)^  [a-z_]+:", features)), "Every feature flag must accept a signed override"
                fallback = {"true": (True, True), "false": (False, False), "{{ not .user.embed }}": (False, True), "{{ .user.embed }}": (True, False)}
                embed = {"email": "viewer@example.com", "admin": False, "embed": True}
                member = {"email": "viewer@example.com", "admin": False}
                checks = 0
                embedded, signed_in = resolved_flags(embed), resolved_flags(member)
                for key, value in templates.items():
                    expected_embed, expected_member = fallback[value]
                    assert embedded.get(camel(key)) is expected_embed, (key, "embed fallback", embedded.get(camel(key)))
                    assert signed_in.get(camel(key)) is expected_member, (key, "member fallback", signed_in.get(camel(key)))
                    checks += 2
                for enabled in (True, False):
                    overridden = resolved_flags({**embed, **{"feature_" + key: enabled for key in templates}})
                    for key in templates:
                        assert overridden.get(camel(key)) is enabled, (key, enabled, overridden.get(camel(key)))
                        checks += 1
                for raw, expected in (("true", True), ("false", False), ("1", False), ("true || true", False), ([True], False)):
                    assert resolved_flags({**embed, "feature_exports": raw}).get("exports") is expected, ("malformed override", raw)
                    checks += 1
                chat_off = resolved_flags({**embed, "feature_chat": False, "feature_dashboard_chat": True})
                assert chat_off.get("chat") is False and chat_off.get("dashboardChat") is False, "Rill must keep dashboard chat off when chat is off"
                assert embedded.get("dashboardChat") is True, "Embedded dashboard AI is not enabled"
                checks += 2
                print(f"Feature flags: {len(templates)} templated flags passed {checks} fallback and override checks.", flush=True)
                for name in policies:
                    bids = name == "bids_metrics"
                    cases = [
                        ("public baseline", {}, 6 if bids else 4),
                        ("allowed user domain", {"embed_security_mode": "user_domain", "domain": "rilldata.com"}, 6 if bids else 4),
                        ("denied user domain", {"embed_security_mode": "user_domain", "domain": "outside.example"}, None),
                        ("missing user domain", {"embed_security_mode": "user_domain"}, None),
                        ("advertiser", {"embed_security_mode": "advertiser", "advertiser_name": "Grocery Outlet"}, 2 if bids else None),
                        ("site domain", {"embed_security_mode": "site_domain", "domain": "damedetrefle.com"}, 2 if bids else 1),
                        ("combined", {"embed_security_mode": "advertiser_domain", "domain": "damedetrefle.com", "advertiser_name": "Grocery Outlet"}, 1 if bids else None),
                        ("missing advertiser", {"embed_security_mode": "advertiser"}, None),
                        ("empty advertiser", {"embed_security_mode": "advertiser", "advertiser_name": ""}, None),
                        ("wrong advertiser type", {"embed_security_mode": "advertiser", "advertiser_name": ["Grocery Outlet"]}, None),
                        ("missing site domain", {"embed_security_mode": "site_domain"}, None),
                        ("empty site domain", {"embed_security_mode": "site_domain", "domain": ""}, None),
                        ("wrong site domain type", {"embed_security_mode": "site_domain", "domain": 12}, None),
                        ("combined missing domain", {"embed_security_mode": "advertiser_domain", "advertiser_name": "Grocery Outlet"}, None),
                        ("combined missing advertiser", {"embed_security_mode": "advertiser_domain", "domain": "damedetrefle.com"}, None),
                        ("quoted advertiser", {"embed_security_mode": "advertiser", "advertiser_name": "O'Reilly"}, 1 if bids else None),
                        ("quoted domain", {"embed_security_mode": "site_domain", "domain": "quote's.example"}, 1),
                        ("advertiser SQL injection", {"embed_security_mode": "advertiser", "advertiser_name": "Grocery Outlet' OR 1=1 --"}, 0 if bids else None),
                        ("domain SQL injection", {"embed_security_mode": "site_domain", "domain": "damedetrefle.com' OR 1=1 --"}, 0),
                    ]
                    cases += [(f"invalid mode {mode!r}", {"embed_security_mode": mode}, None) for mode in ["", "unknown", None, False, 0, {}, []]]
                    for label, attrs, expected in cases:
                        attributes = {"email": "viewer@example.com", "admin": False, "embed": True, **attrs}
                        status, data = query(name, attributes)
                        if expected is None:
                            assert status in (403, 404), (name, label, status, data)
                        else:
                            assert status == 200, (name, label, status, data)
                            rows = data.get("data", [])
                            assert len(rows) == expected, (name, label, rows)
                            if label in ("advertiser", "combined"):
                                assert all(row["advertiser_name"] == "Grocery Outlet" for row in rows)
                            if label in ("site domain", "combined"):
                                assert all(row.get("sites_domain", row.get("app_site_domain")) == "damedetrefle.com" for row in rows)
                        checks += 1
                    print(f"{name}: {len(cases)} policy cases passed", flush=True)
                if "exclude:" in policies["bids_metrics"]:
                    status, _ = query("bids_metrics", {"email": "adam.kabak@rilldata.com", "admin": False, "embed": True})
                    assert status in (400, 403), ("Existing field restriction was lost", status)
                    checks += 1
                    print("Existing email-based field exclusion preserved.", flush=True)
                print(f"PASS: {checks} backend security and feature-flag checks.", flush=True)
            finally:
                runtime.terminate()
                try:
                    runtime.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    runtime.kill()
                    runtime.wait()


if __name__ == "__main__":
    main()
