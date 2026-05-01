interface CodeWithSourceProps {
    title: string;
    code: string;
    sourceLabel: string;
    sourceUrl: string;
}

// Renders a labeled code block (e.g. JSON or YAML snippet) with a link to its
// source file on GitHub. Used on example pages to show the iframe request body
// or a Rill project YAML config alongside a pointer to the canonical source.
const CodeWithSource = ({ title, code, sourceLabel, sourceUrl }: CodeWithSourceProps) => (
    <section>
        <h3 className="text-sm font-semibold text-gray-700 mb-2">{title}</h3>
        <pre className="bg-gray-100 text-gray-800 p-3 rounded font-mono text-xs overflow-x-auto border border-gray-200">
{code}
        </pre>
        <p className="text-sm text-gray-600 mt-2">
            Source:{' '}
            <a
                href={sourceUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-indigo-600 underline hover:text-indigo-800"
            >
                {sourceLabel} <span aria-hidden="true">↗</span>
            </a>
        </p>
    </section>
);

export default CodeWithSource;
