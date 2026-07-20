# Anharmonic Labs web laboratory

The repository-level `/docs` directory is the complete artifact published to
GitHub Pages. It is a dependency-free static application: HTML, CSS, SVG, and
JavaScript modules.

The browser simulator intentionally contains only standard statevector
operations. Do not place research operator constructors, native libraries,
private coefficients, service credentials, or unpublished experiment data in
that directory. Everything under the Pages source is downloadable by every
visitor.

## Run locally

From the repository root:

```bash
python -m http.server 8000 --directory docs
```

Then open `http://localhost:8000`.

Run the browser-core tests with:

```bash
node --test anharmonic-labs/tests/web/*.test.mjs
```

## Publish

GitHub Pages is configured to deploy directly from `/docs` on the publishing
branch. There is no custom Pages workflow. The default project URL is:

```text
https://anharmoniclabs.github.io/Anharmoniclabs/
```

No `CNAME` is included because a custom domain has not been selected. Add one
only after the domain is owned and its DNS records have been configured.
