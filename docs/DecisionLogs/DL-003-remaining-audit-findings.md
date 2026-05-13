# DL-003: Accept transitive dev-tooling audit findings

**Date:** 2026-05-13
**Status:** Accepted

## Context

After upgrading to Next.js 16.2.6 and React 19, `npm audit` reports 5 remaining
vulnerabilities — all transitive through eslint-config-next (glob CLI) and
postcss XSS. Neither is reachable from runtime code.

## Analysis

- glob CLI injection: requires invoking the `glob` binary with `-c/--cmd`.
  We use ESLint, which depends on glob as a library. The CLI is never invoked.
  Not exploitable.
- PostCSS unescaped `</style>` XSS: requires processing untrusted user-supplied
  CSS. We compile our own static CSS at build time. Not exploitable.

## Decision

Accept these findings. Re-check on every dependency upgrade; remove once
upstream maintainers publish fixes.

## Follow-ups

- [ ] Add a section to README explaining remaining audit findings
- [ ] Re-run `npm audit` weekly during the sprint