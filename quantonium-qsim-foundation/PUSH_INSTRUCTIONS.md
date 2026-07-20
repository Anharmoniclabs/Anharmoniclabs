# Push Instructions

The ChatGPT GitHub connection used to build this package is authenticated as `LMMinier`, while the target repository is owned by `LM-79`. GitHub rejected branch creation with HTTP 403 because the integration does not have write access to `LM-79/Nueronce`.

## Option A — reconnect the GitHub app

Install or reconnect the ChatGPT GitHub app for the `LM-79` account and grant it access to `LM-79/Nueronce`. Then ask ChatGPT to push the prepared foundation.

## Option B — push from the existing Codespace

Upload and extract this archive into the root of the Codespace, then run:

```bash
cd /workspaces/Nueronce
python -m pip install -e ".[dev,quantum]"
pytest -q
git add .
git commit -m "Build standalone QuantoniumOS quantum simulation foundation"
git push origin main
```
