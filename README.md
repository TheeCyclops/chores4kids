# Chores4Kids Custom Fork

This repository is a **custom Home Assistant fork** of `Chores4Kids`.

It is **not** the stock upstream release repo.

This fork exists so Home Assistant can install and update a customized household version through **GitHub + HACS**, with the backend integration and Lovelace card kept on the same release.

## What This Repo Is

- the release source for this customized `Chores4Kids` install
- a custom fork with local changes for this household
- the repo Home Assistant should pull from in HACS

## What This Repo Is Not

- not the original upstream `qlerup/chores4kids` project
- not a generic public support repo for all users

## Source of Truth

This repository is the editable working source **and** the published release source.

- Local working copy: `C:\Users\alxwh\Documents\chores4kids`
- GitHub/HACS repository: `TheeCyclops/chores4kids`

Make routine code changes, commits, tags, and releases here. The old `MagicMirror/home-assistant/vendor/chores4kids/` checkout is not authoritative and must not be used for publishing.

Release/update steps for this fork are documented in:

- `RELEASING.md`

## Why This Fork Exists

This fork is used to keep a customized `Chores4Kids` deployment stable for this household, including:

- native task time fields
- custom admin card behavior
- release-aligned backend and card updates through HACS

## Install / Update Model

Home Assistant should use this repo as a **HACS custom repository**.

Expected flow:

1. A new version is prepared from the local working copy.
2. That version is published here as a tagged GitHub release.
3. Home Assistant updates the integration through HACS.
4. On setup, the integration copies its bundled card JavaScript to `/config/www/chores4kids-card.js` and registers it as a Lovelace resource.

Expected card resource:

- `/local/chores4kids-card.js?v=<cache-token>` (JavaScript module)

`/local/` is correct for this fork. The version query string is a cache-buster generated from the deployed file, so it will change after card updates. Do not add a second `/hacsfiles/chores4kids/chores4kids-card.js` resource.

## Upstream Credit

The original project is based on:

- `https://github.com/qlerup/chores4kids`

Upstream deserves credit for the base integration and card.

This fork only exists to maintain a customized household deployment and release path.

## Support Boundary

If something in this repo differs from upstream, that is expected.

This fork may include:

- custom UI changes
- custom service behavior
- household-specific deployment choices
- release timing that does not match upstream

## Maintainer Note

If you are looking at this repo on GitHub and wondering whether it is the official `Chores4Kids` project, it is not.

This is a custom fork and release source.

## Agent and maintenance context

Start with [AGENTS.md](AGENTS.md) and the [context index](notes/context/README.md). Current implementation, live verification gaps, recovery guidance, and release boundaries are recorded there.
