# Contributing

Use the [Issue forms](.github/ISSUE_TEMPLATE) for bugs and feature requests.
Bug reports receive `bug`; feature requests receive `enhancement`. Blank issues
remain available for other work. Check existing issues and PRs before starting.

## Pull requests and squash commits

Use Conventional Commits for PR titles: `type(scope): description`, with an
optional scope and a type chosen from `feat`, `fix`, `perf`, `revert`, `docs`,
`refactor`, `style`, `test`, `build`, `ci`, or `chore`. Choose the type from the
final diff and its user impact. Repository automation changes normally use
`ci`, `build`, or `chore`.

The [PR template](.github/pull_request_template.md) records why the change is
needed, its resulting behavior, and observed verification. Write the title and
body in English as the final squash commit message, so essential context is
available in Git history. Remove template comments and temporary notes before
merging. Use `Closes #123` only when the PR completes that issue.

[PRLint](.github/workflows/prlint.yml) validates the title, a blank line, and
the body together with the unmodified `@commitlint/config-conventional`
preset. It checks syntax, not whether the chosen type describes the change.
Dependabot-authored PRs skip PRLint.

Resolve actionable review findings and threads, obtain the required eligible
approval, and pass relevant checks on the final HEAD before a normal squash
merge. Do not bypass protections or approve a PR without explicit permission
for that PR. Capture the reviewed title, body, and HEAD together; pass that
message explicitly when merging with an expected-head SHA guard. Review later
message edits before using them. Verify the resulting commit message and its
checks after merging. Merging does not authorize a release.

Labels are triage metadata. They do not determine the Conventional Commit
type, version, or release-note category. If release automation is added, use
the committed squash message for classification rather than label names.

## Repository automation

See [Repository automation](docs/repository-automation.md) for label ownership,
the settings application path, and validation. Keep external Actions pinned
to full commit SHAs with version comments. There is currently no product
build or release workflow.
