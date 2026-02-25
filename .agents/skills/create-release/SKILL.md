---
name: create-release
description: Standard process for creating a new release of tailrelay-startos.
---

# Create Release Skill

This skill documents the exact step-by-step process for creating a new release for the `tailrelay-startos` project. The user or an agent should follow these instructions to ensure releases are created uniformly.

## Process

1. **Identify the New Version Number**
   - Determine the correct semantic version number (e.g., `v0.5.0`) based on the changes being released.

2. **Update Versions**
   - Modify the `version:` field in `manifest.yaml` to the new version without the `v` prefix (e.g., `version: 0.5.0`).
   - Modify the `FROM` image tag in the `Dockerfile` to use the new upstream image version with the `v` prefix (e.g., `FROM sudocarlos/tailrelay:v0.5.0`).

3. **Commit the Changes**
   - Stage the changes to `manifest.yaml` (and any other release-related files like `CHANGELOG.md` if applicable).
   - Create a commit using the standard release message format: `chore(release): vX.Y.Z` (e.g., `chore(release): v0.5.0`).

4. **Tag the Release**
   - Create an annotated or lightweight git tag for the same version: `git tag vX.Y.Z` (e.g., `git tag v0.5.0`).

5. **Push and Trigger Actions**
   - Push the commit to the main branch: `git push origin main`.
   - Push the new tag to the upstream repository: `git push origin vX.Y.Z`.
   - Ensure the `.github/workflows/releaseService.yml` action is triggered. This action automatically builds the `.s9pk` packages for `arm64` and `amd64`, generates checksums and a summary from the manifest `release-notes`, and publishes the GitHub release.
