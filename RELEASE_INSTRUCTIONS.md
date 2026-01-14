# Release Instructions for autowrap 0.26.5

This document describes how to create a new release of autowrap version 0.26.5.

## Prerequisites

- You must have write access to the OpenMS/autowrap repository
- The repository has GitHub Actions workflows configured for releases
- PyPI Trusted Publishing is configured for this repository

## Release Process

The release process is fully automated using GitHub Actions. Follow these steps:

### 1. Verify the Release is Ready

Before triggering the release, ensure:

- [x] `autowrap/version.py` contains the correct version: `0.26.5`
- [x] `CHANGELOG.md` contains the release notes for version 0.26.5
- [x] All tests pass on the main branch
- [x] The package builds successfully (verified locally with `python -m build`)

### 2. Trigger the Release Workflow

1. Go to the GitHub Actions tab: https://github.com/OpenMS/autowrap/actions
2. Select the "release autowrap" workflow from the left sidebar
3. Click "Run workflow" button on the right
4. In the dialog:
   - **version**: Leave empty (it will use 0.26.5 from `autowrap/version.py`)
   - **next_version**: Leave empty (it will auto-increment to 0.26.6)
   - Or specify custom values if needed
5. Click "Run workflow" to start the release

### 3. What Happens Automatically

The workflow will:

1. **Build the package**: Creates wheel and source distributions
2. **Publish to PyPI**: Uploads the package using Trusted Publishing (OIDC)
3. **Create GitHub Release**: Creates a release with tag `release/0.26.5`
   - Release notes from CHANGELOG.md will be included
4. **Prepare for next release**:
   - Appends CHANGELOG.md content to HISTORY.md
   - Resets CHANGELOG.md to `autowrap 0.26.6` (or custom next version)
   - Updates `autowrap/version.py` to 0.26.6
   - Commits these changes with message "New release cycle"

### 4. Verify the Release

After the workflow completes:

1. Check PyPI: https://pypi.org/project/autowrap/0.26.5/
2. Check GitHub Releases: https://github.com/OpenMS/autowrap/releases/tag/release/0.26.5
3. Verify the new commit "New release cycle" was created
4. Test installation: `pip install autowrap==0.26.5`

## Manual Release (Alternative)

If you need to release manually without the workflow:

```bash
# Ensure you're on the correct branch
git checkout master
git pull

# Verify version
python -c 'from autowrap.version import __version__; print(__version__)'

# Build the package
python -m pip install -U pip build
python -m build

# Upload to PyPI (requires API token or credentials)
python -m pip install twine
python -m twine upload dist/autowrap-0.26.5*

# Create git tag
git tag -a release/0.26.5 -m "Release 0.26.5"
git push origin release/0.26.5

# Prepare for next cycle (update version, CHANGELOG, HISTORY)
# ... (manual steps)
```

## Troubleshooting

- If the PyPI upload fails, check the Trusted Publishing configuration
- If the workflow fails, check the GitHub Actions logs for details
- For version conflicts, ensure `autowrap/version.py` has the correct version

## Version Information

- **Current Release**: 0.26.5
- **Next Version**: 0.26.6 (auto-incremented)
- **Tag Format**: `release/X.Y.Z`

## Files Modified for This Release

- `CHANGELOG.md`: Added release notes for 0.26.5
- `autowrap/version.py`: Already set to 0.26.5
