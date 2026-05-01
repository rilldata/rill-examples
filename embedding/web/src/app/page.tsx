const Home = () => {
  return (
    <div className="max-w-3xl p-6 bg-white rounded-lg">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">Rill Embedding Examples</h2>
      <p className="text-gray-600 mb-4">
        This site shows working examples of embedding Rill dashboards into a web app. Use the sidebar to browse the examples by topic; each page is a self-contained demo with the iframe request that powers it.
      </p>
      <p className="text-gray-600 mb-6">
        For deeper context, see:
      </p>
      <ul className="space-y-2 mb-6">
        <li>
          <a
            href="https://docs.rilldata.com/developers/embed/dashboards"
            target="_blank"
            rel="noopener noreferrer"
            className="text-indigo-600 underline hover:text-indigo-800"
          >
            Embedding documentation <span aria-hidden="true">↗</span>
          </a>
        </li>
        <li>
          <a
            href="https://github.com/rilldata/rill-examples/tree/main/embedding/web"
            target="_blank"
            rel="noopener noreferrer"
            className="text-indigo-600 underline hover:text-indigo-800"
          >
            Source code on GitHub <span aria-hidden="true">↗</span>
          </a>
        </li>
      </ul>
    </div>
  );
};

export default Home;
