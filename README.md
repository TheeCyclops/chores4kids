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
- not the place where routine day-to-day feature work starts

## Source of Truth

The editable working source lives in the main `MagicMirror` project under:

- `MagicMirror/home-assistant/vendor/chores4kids/`

This GitHub repo is the **published release copy** of that working tree.

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
3. Home Assistant updates through HACS.
4. The bundled card resource stays aligned with the installed backend version.

Typical card resource path after HACS install:

- `/hacsfiles/chores4kids/chores4kids-card.js`

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
