# Anharmonic Labs web laboratory

This directory is the complete artifact published to GitHub Pages. It is a
dependency-free static application: HTML, CSS, SVG, and JavaScript modules.

The browser simulator intentionally contains only standard statevector
operations. Do not place research operator constructors, native libraries,
private coefficients, service credentials, or unpublished experiment data in
this directory. Everything under `site/` is downloadable by every visitor.

## Run locally

From `anharmonic-labs/`:

```bash
python -m http.server 8000 --directory site
```

Then open `http://localhost:8000`.

Run the browser-core tests with:

```bash
node --test tests/web/*.test.mjs
```

## Publish

The repository workflow `.github/workflows/pages.yml` tests the simulator,
checks the public artifact for protected implementation terminology, and
deploys only this directory. In the GitHub repository settings, choose
**GitHub Actions** as the Pages source. The default project URL will be:

```text
https://lm-79.github.io/Anharmoniclabs/
```

No `CNAME` is included because a custom domain has not been selected. Add one
only after the domain is owned and its DNS records have been configured.
