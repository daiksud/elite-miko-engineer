# Repository automation

## Managed labels

[The settings declaration](../.github/settings.yml) manages these ten labels
by repository-specific ID: `accessibility`, `bug`, `documentation`, `duplicate`,
`enhancement`, `good first issue`, `help wanted`, `invalid`, `question`, and
`wontfix`. Unlisted labels, including `ci` and any Dependabot labels, coexist.
Do not delete them or remove their existing Issue/PR assignments. Removing a
label from the declaration does not delete it remotely.

The [Labeler workflow](../.github/workflows/labeler.yml) synchronizes only
`documentation`. Its [path rule](../.github/labeler.yml) matches when every
changed file is documentation; `sync-labels: true` removes that label when the
rule stops matching. Other labels are outside its configuration. It reads
trusted base-branch configuration and does not check out or execute PR code
in its write-capable `pull_request_target` job.

Issue Forms assign `bug` or `enhancement`. This repository currently has no
Dependabot configuration. If introduced, omit explicit `labels` overrides so
Dependabot can use its defaults. Labels do not classify release notes; the
[contribution guidelines](../CONTRIBUTING.md) own commit classification.

## Settings application

There is no automatic settings-apply workflow. Maintainers review and apply
labels locally using a GitHub identity authorized to manage repository labels.
Use [gh-settings v0.26.0](https://github.com/daiksud/gh-settings/releases/tag/v0.26.0)
and verify the platform binary against that release's `SHA256SUMS` before
using credentials. The Darwin arm64 SHA-256 is
`3c1e76c64a2573f9fdc67e118f69193b9f3c2e8ff57745c36f433987907862c2`;
the source commit is `276f971a6816c29f7814394e93388410ca3263f8`.
A version string alone does not authenticate an executable.

The existing full manifest includes Rulesets and other administrative settings.
Do not apply the full manifest for label maintenance. Its Ruleset parameters
also require compatibility review before a full live plan can be relied on.
Use this isolated procedure:

1. Create a temporary clone of this repository and retain its GitHub origin.
2. Replace only the temporary clone's `.github/settings.yml` with
   `schemaVersion: 1` and `settings.labels`, copied from the maintained
   manifest, including all ten label IDs, names, colors, and descriptions.
   Include no repository, Ruleset, Actions, environment, or security fields.
3. Run the verified CLI's `validate` and `plan` from that clone. Review every
   reported difference and confirm it concerns only the intended labels.
4. If differences are intended, run `apply` from that same isolated clone.
   If the plan has no differences, no apply is needed.
5. Copy any new label IDs written back by the CLI into the maintained manifest.
   Inspect live IDs and assignments, then run `plan` again to confirm no drift.

Apply is not atomic: after an error, inspect live state and re-plan before
retrying. Never substitute a full-manifest apply for this procedure. Settings
validation alone does not establish live state or enforcement.

## Validation and merge

Run `actionlint` for workflow edits and parse changed YAML. Validate proposed
PR messages with the same PRLint tools:

```sh
commitlint_path=$(mise exec npm:@commitlint/cli -- which commitlint)
printf '%s\n\n%s\n' "$PR_TITLE" "$PR_BODY" |
  mise exec bun npm:@commitlint/cli -- bun run --bun --no-install "$commitlint_path" --strict
```

Review the documentation-only and mixed-file cases against Labeler's rule.
New Labeler configuration takes effect from the trusted base branch after
merge; its first PR run cannot demonstrate the new base-branch behavior.

The existing Codex approval workflow and repository protections govern review
and merge eligibility; see [README](../README.md#codexの自動承認とマージ保護).
PRLint is an independent check, not a new protection setting. Verify live
GitHub merge eligibility and checks before merging. Do not change permissions,
security settings, or protections to complete delivery.
