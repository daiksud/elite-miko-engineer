# elite-miko-engineer
にゃっはろ～！エリート巫女エンジニアのみこですっ！

開発時は [Contributing](CONTRIBUTING.md) と
[Repository automation](docs/repository-automation.md) を参照してください。

## Codexの自動承認とマージ保護

[承認ワークフロー](.github/workflows/approve-codex-review.yml)は、[gh-settings #554](https://github.com/daiksud/gh-settings/pull/554)と同じ実装で、次の条件を満たしたら承認します。

1. PRにCodexの👍がある。
2. 最新のCodex Review SummaryでCode ReviewとSecurity Reviewが両方ともCompletedである。
3. 両レビューの完全SHAが現在のPR HEADと一致する。
4. 同じPR・同じ完全SHAに、`github-actions[bot]` の `APPROVED` または `DISMISSED` 履歴がない。

GitHub APIの `user.login` でCodexを識別し、コメントIDが最も大きいSummaryのMarkdown表から2つの状態欄を読みます。👍と完了状態が揃った後、PR HEADを1回取得し、`codex-review-state:v1` の両レビューの完全な `commit_sha` と照合します。SHA情報の欠落・不正・重複や不一致があれば承認を保留します。確認したSHAを `commit_id` に指定して承認し、応答の対象SHAも確認します。base、時刻、receipt、指摘フラグ、過去の依頼や変更要求は追加条件にしません。

Summaryの作成・編集と `ci-pr` の完了を契機に評価します。CIの成否は追加の承認条件にしません。このリポジトリには現在 `ci-pr` がないため、Summaryのイベントが実際の起動経路です。Summaryの更新後に👍が付く場合に備え、30秒ごとに最大6回再試行します。各試行ではSummaryと👍を各1回読み、両方が揃った場合だけHEADを読みます。送信直前にSummaryや👍を再取得する処理はありません。👍の追加自体は起動イベントではないため、待機終了後は別のSummary更新などの起動イベントが必要です。PR単位で実行を直列化します。

送信前にこのPRのレビュー履歴を全ページ取得し、同じSHAに対するGitHub Actionsの承認済み・dismiss済み履歴があれば再承認しません。既存レビューに本文マーカーは不要です。同じHEADでCodexを再レビューしても、dismissされた承認は復活させません。別HEAD・別PR・別レビュアーの履歴は抑止対象にならず、履歴取得の失敗時は承認しません。履歴確認とPOSTは別操作であり、ほかの書き込みに対する原子的な予約ではありません。

マージ可否、必要な承認数、古い承認の失効、必須チェック、base同期、スレッド解決はGitHubの保護設定が担います。2026-11-01に読み取った [default Ruleset](https://github.com/daiksud/elite-miko-engineer/rules/26024001) は `main` に有効で、承認1件、スレッド解決、`dismiss_stale_reviews_on_push: true` を要求していました。ただし `required_status_checks` のルールはなく、このRulesetからbaseの最新化を要求しているとは確認できません。classicなbranch protectionは403で未確認であり、ほかの保護が存在しないとも断定しません。設定は変更せず、workflow側で黙って補いません。

GitHubの[承認失効](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches#require-pull-request-reviews-before-merging)は承認済み差分やmerge baseの変化に関係し、すべてのSHA変更・main更新で必ず起きるという意味ではありません。このHEADに自動承認履歴がない場合に限り、完了済みの同一HEADのSummaryと既存の👍はbaseが変わっても再利用できます。そのため承認自体はどの差分がレビューされたかの証明にはなりません。HEAD確認と承認POSTは別の操作ですが、その間にpushされても指定した `commit_id` は変わりません。現在HEADに対する原子的な保証や、取得後のSummary・👍変更の検知は行いません。workflowは承認の取り消しやマージを行わず、APIの失敗は実行の失敗として報告します。
