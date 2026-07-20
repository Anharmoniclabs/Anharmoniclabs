# Anharmonic Labs release checklist

Before publishing a release:

1. Build the native structured kernel in release and sanitizer configurations.
2. Run the complete Python test suite.
3. Run the reproducibility experiments and verify every SHA-256 sidecar.
4. Confirm that active package, workflow, and artifact names use the Anharmonic Labs identity.
5. Preserve the license and historical source lineage recorded in `LICENSE.md` and
   `docs/provenance.md`.
6. Review the working-tree diff, then commit and push through the repository's
   normal protected-branch workflow.

Renaming the hosted repository, package registry project, or organization is a
separate administrative action and should happen only after local consumers and
external links have been migrated.
