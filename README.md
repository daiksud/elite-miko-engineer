# elite-miko-engineer
にゃっはろ～！エリート巫女エンジニアのみこですっ！

## Codexの自動承認とマージ保護

[承認ワークフロー](.github/workflows/approve-codex-review.yml)は、次の2条件を満たしたら承認します。

1. PRにCodexの👍がある。
2. 最新のCodex Review SummaryでCode ReviewとSecurity Reviewが両方ともCompletedである。

GitHub APIの `user.login` でCodexを識別し、コメントIDが最も大きいSummaryのMarkdown表にある2つの状態欄だけを確認します。HEAD、base、時刻、receipt、指摘フラグ、過去の依頼や変更要求は承認条件にしません。承認APIの対象コミットは `commit_id` を指定せずGitHubに任せます。構造化メタデータも不要です。送信直前にも同じ2条件だけを再確認し、コメント本文やリアクションIDが変わったこと自体は追加条件にしません。

Summaryの作成・編集と `ci-pr` の完了を契機に評価します。CIの成否は追加の承認条件にしません。このリポジトリには現在 `ci-pr` がないため、Summaryのイベントが実際の起動経路です。Summaryの更新後に👍が付く場合に備え、同じ2条件を30秒ごとに最大6回再確認します。👍の追加自体は起動イベントではないため、待機終了後は別のSummary更新などの起動イベントが必要です。PR単位で実行を直列化しますが、条件を満たすイベントが重なれば承認を複数回送信することがあります。

マージ可否、必要な承認数、古い承認の失効、必須チェック、base同期、スレッド解決はGitHubの保護設定が担います。2026-11-01に読み取った [default Ruleset](https://github.com/daiksud/elite-miko-engineer/rules/26024001) は `main` に有効で、承認1件、スレッド解決、`dismiss_stale_reviews_on_push: true` を要求していました。ただし `required_status_checks` のルールはなく、このRulesetからbaseの最新化を要求しているとは確認できません。classicなbranch protectionは403で未確認であり、ほかの保護が存在しないとも断定しません。設定は変更せず、workflow側で黙って補いません。

GitHubの[承認失効](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches#require-pull-request-reviews-before-merging)は承認済み差分やmerge baseの変化に関係し、すべてのSHA変更・main更新で必ず起きるという意味ではありません。完了済みSummaryと既存の👍を使ってコード・base変更後に新しい承認を発行できるため、承認自体は現在の差分がレビューされた証明にはなりません。これは2条件に絞った方針の制約です。workflowは承認の取り消しやマージを行わず、APIの失敗は実行の失敗として報告します。
