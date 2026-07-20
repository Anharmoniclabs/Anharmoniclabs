# Anharmonic Labs web laboratory

The repository-level `index.html`, `assets/`, and `.nojekyll` files form the
GitHub Pages application. It is a dependency-free static application: HTML,
CSS, SVG, and JavaScript modules.

The browser simulator intentionally contains only standard statevector
operations. Do not place research operator constructors, native libraries,
private coefficients, service credentials, or unpublished experiment data in
those browser assets. Everything under the Pages source is public.

## Run locally

From the repository root:

```bash
python -m http.server 8000 --directory .
```

Then open `http://localhost:8000`.

Run the browser-core tests with:

```bash
node --test anharmonic-labs/tests/web/*.test.mjs
```

## Publish

GitHub Pages is configured to deploy directly from the publishing branch root.
There is no custom Pages workflow. The default project URL is:

```text
https://anharmoniclabs.github.io/Anharmoniclabs/
```

No `CNAME` is included because a custom domain has not been selected. Add one
only after the domain is owned and its DNS records have been configured.
