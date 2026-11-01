# elite-miko-engineer
にゃっはろ～！エリート巫女エンジニアのみこですっ！

## Codexの自動承認とマージ保護

[承認ワークフロー](.github/workflows/approve-codex-review.yml)は、現在のHEADに対する信頼できるCodexレビューを解釈し、そのコミットを承認します。BotとApp、コード・セキュリティレビューの完了、指摘、Codexの👍を確認します。セキュリティの指摘フラグがnullの場合は、同じHEADの種類別の最新の信頼できるreceiptと完全なSHAへの解決も必要です。送信直前に証跡、👍、open状態とHEADを再確認し、正確な `commit_id` で承認します。

同じHEADの完了結果と既存の👍は再利用できます。新しい依頼や時刻だけでは再レビューを要求しません。編集・再利用された証跡の時刻による検知や、レビュー対象baseの証明は行いません。workflowの成功には承認保留も含まれ、承認とマージ可能性は別です。

承認の失効や必須チェック、必要なbase同期はRulesetsの責務です。2026-11-01に読み取った [default Ruleset](https://github.com/daiksud/elite-miko-engineer/rules/26024001) は `main` に対して有効で、`dismiss_stale_reviews_on_push: true` でした。ただし、`required_status_checks` のルールはありません。このRulesetからbaseの最新化を要求しているとは確認できません。classicなbranch protectionは403で未確認であり、ほかの保護が存在しないとも断定しません。設定は変更せず、この不足の可能性を承認workflowで黙って補いません。

GitHubの[承認失効条件](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches#require-pull-request-reviews-before-merging)は、承認済み差分の変化やmerge baseから導入された変更に基づきます。HEADのSHA変更やmainの更新だけで必ず失効するという意味ではありません。[strictな必須チェック](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets#require-status-checks-to-pass-before-merging)によるbase最新化は別のマージ条件です。workflowはbase履歴を追跡せず、承認の取り消しやマージを行いません。実際のマージ判断では有効な保護とbypass権限を再確認してください。
