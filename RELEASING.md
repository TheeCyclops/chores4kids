# Updating This Fork

This file is the **step-by-step release checklist** for this fork.

Repo:

- `C:\Users\alxwh\Documents\chores4kids`

GitHub remote:

- `https://github.com/theecyclops/chores4kids`

Home Assistant updates from **GitHub tags/releases through HACS**.

## Normal Update Flow

### 1. Make the code change

Edit the files you need in:

- `C:\Users\alxwh\Documents\chores4kids`

If you made the change somewhere else first, copy the changed file(s) into this repo before continuing.

### 2. Bump the version

Open:

- `custom_components/chores4kids/manifest.json`

Update:

- `"version": "0.1.3"`

to the next version, for example:

- `"version": "0.1.4"`

Rule:

- manifest version = `0.1.4`
- git tag = `v0.1.4`

Those should always match except the tag has the leading `v`.

### 3. Review what changed

From PowerShell:

```powershell
cd C:\Users\alxwh\Documents\chores4kids
git status
git diff
```

### 4. Commit the change

```powershell
git add .
git commit -m "Fix auto-assigned task times"
```

Use a message that matches the actual change.

### 5. Push the branch

```powershell
git push origin main
```

### 6. Create and push the tag

Example for version `0.1.4`:

```powershell
git tag v0.1.4
git push origin v0.1.4
```

### 7. Publish the GitHub release

In GitHub:

1. Open the repo.
2. Go to `Releases`.
3. Create or publish a release from the new tag.
4. Use the same version name as the tag.

Notes:

- HACS is much more reliable when there is an actual GitHub release for the tag.
- If the tag already exists, do not reuse it for a different code state. Bump the version and create a new tag instead.

### 8. Update in HACS

In Home Assistant:

1. Open HACS.
2. Open this `Chores4Kids` fork.
3. Click `Download` or `Update`.
4. Select the newest version if HACS asks.

If HACS does not immediately show the new version:

1. Refresh HACS.
2. Wait a minute and refresh again.
3. Confirm the manifest version and git tag match.
4. Confirm the GitHub release was published from the new tag.

### 9. Restart Home Assistant

After HACS finishes installing:

1. Restart Home Assistant.
2. Reload the dashboard/browser after HA comes back up.

### 10. Verify the change

For this fork, the minimum check after release is:

1. Open the Chores4Kids dashboard/card.
2. Confirm the new behavior is visible.
3. Confirm there are no missing entities or unavailable task sensors.

For timing-related fixes, also verify:

1. A repeated auto-assigned task appears at its configured time.
2. It does not fall back to the 5:00 PM, 6:00 PM, 7:00 PM pattern unless the task truly has no time set.

## Quick Command Example

Replace the version and commit message as needed:

```powershell
cd C:\Users\alxwh\Documents\chores4kids
git status
git add .
git commit -m "Fix auto-assigned task times"
git push origin main
git tag v0.1.4
git push origin v0.1.4
```

Then publish the GitHub release and update through HACS.

## Important Rules

- Do not edit an old tag after it has been released.
- Do not reuse a version number.
- Always bump `manifest.json` before tagging.
- Always restart Home Assistant after the HACS update.
- If HACS looks behind, verify the GitHub release exists before troubleshooting HA.

## If You Need to Make It Simpler

Use this exact checklist every time:

1. Edit code.
2. Bump `manifest.json`.
3. `git add .`
4. `git commit -m "..."`
5. `git push origin main`
6. `git tag vX.Y.Z`
7. `git push origin vX.Y.Z`
8. Publish GitHub release.
9. Update in HACS.
10. Restart HA.
