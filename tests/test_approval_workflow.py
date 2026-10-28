"""Run the actual approval Bash with isolated API fixtures; never send reviews.

Run with: python3 -m unittest discover -s tests -p 'test_*.py'
Requires Bash and jq, as does the Linux workflow.
"""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest


FAKE_GH = r'''
import json
import os
from pathlib import Path
import sys

root = Path(os.environ["FIXTURE_ROOT"])
scenario = os.environ["SCENARIO"]
args = sys.argv[1:]
head = "a" * 40
if args[:3] == ["api", "--method", "POST"]:
    assert args[3:] == ["repos/owner/repo/pulls/7/reviews", "-f", "event=APPROVE", "-f", "commit_id=" + head]
    if scenario == "post rejected":
        print(json.dumps({"message": "fixture rejected review", "errors": [{"field": "commit_id", "code": "invalid"}], "ignored": "dummy-not-a-token"}))
        sys.exit(42)
    if scenario == "post non-json":
        print("dummy-not-a-token unexpected proxy response")
        sys.exit(42)
    with (root / "approvals").open("a") as out:
        out.write("commit_id=" + head + "\n")
    sys.exit(0)
assert args[0] == "api"
endpoint = args[1]
if endpoint == "repos/owner/repo/pulls/7":
    second = (root / "pr-read").exists()
    state = "closed" if scenario == "closed" or (second and scenario == "closed during check") else "open"
    sha = "b" * 40 if second and scenario == "head changed" else head
    (root / "pr-read").touch()
    print(json.dumps({"state": state, "draft": os.environ["DRAFT"] == "true", "head": {"sha": sha}}))
elif endpoint == "repos/owner/repo/issues/comments/123":
    assert args[2:] == ["--jq", ".body"]
    print((root / "summary").read_text())
else:
    assert args[2:] == ["--paginate", "--slurp"]
    if endpoint == "repos/owner/repo/issues/7/comments?per_page=100":
        if scenario == "pagination failed":
            sys.exit(55)
        body = (root / "summary").read_text()
        pages = [[{"user": {"login": "someone"}, "body": body}]]
        if scenario != "no bot summary":
            pages.append([{"user": {"login": "chatgpt-codex-connector[bot]"}, "body": body}])
        print(json.dumps(pages))
    elif endpoint == "repos/owner/repo/issues/7/reactions?per_page=100":
        print(json.dumps([[{"user": {"login": "other"}, "content": "eyes"}], [{"user": {"login": "chatgpt-codex-connector[bot]"}, "content": "+1"}]]))
    elif endpoint == "repos/owner/repo/pulls/7/reviews?per_page=100":
        review = {"user": {"login": "github-actions[bot]"}, "state": "APPROVED", "commit_id": head}
        print(json.dumps([[review]] if scenario == "already approved" else [[], []]))
    else:
        raise AssertionError("unexpected API call: " + endpoint)
'''


@unittest.skipIf(os.name == "nt", "the approval workflow runs on Linux")
class CodexApprovalTest(unittest.TestCase):
    def test_draft_and_ready_review_eligibility(self):
        bash = shutil.which("bash")
        self.assertIsNotNone(bash, "Bash is required")
        self.assertIsNotNone(shutil.which("jq"), "jq is required")
        workflow = Path(__file__).resolve().parents[1] / ".github/workflows/approve-codex-review.yml"
        _, marker, block = workflow.read_text().partition("        run: |\n")
        self.assertTrue(marker, "missing approval script")
        script = textwrap.dedent(block)
        scenarios = (
            "approve", "comment event", "stale", "unresolved", "code incomplete",
            "security incomplete", "code stale", "security stale", "code findings",
            "security findings", "closed", "closed during check", "already approved",
            "head changed", "pagination failed", "no bot summary", "post rejected", "post non-json",
        )
        for draft in (False, True):
            for scenario in scenarios:
                with self.subTest(draft=draft, scenario=scenario), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    state = {}
                    for name in ("code", "security"):
                        state[name + "_review"] = {
                            "commit_sha": "b" * 40 if scenario in ("stale", name + " stale") else "a" * 40,
                            "status": "in_progress" if scenario == name + " incomplete" else "completed",
                            "has_unresolved_findings": scenario in ("unresolved", name + " findings"),
                        }
                    summary = "<!-- codex-pull-request-review-summary -->\n<!-- codex-review-state:v1 " + json.dumps(state) + " -->"
                    (root / "summary").write_text(summary)
                    (root / "workflow.sh").write_text(script)
                    gh = root / "gh"
                    gh.write_text("#!" + sys.executable + "\n" + textwrap.dedent(FAKE_GH))
                    gh.chmod(0o700)
                    env = {
                        "PATH": str(root) + os.pathsep + os.environ["PATH"],
                        "HOME": directory, "XDG_CONFIG_HOME": directory, "GH_CONFIG_DIR": directory,
                        "GH_TOKEN": "dummy-not-a-token", "GITHUB_REPOSITORY": "owner/repo", "PR_NUMBER": "7",
                        "COMMENT_ID": "123" if scenario == "comment event" else "",
                        "FIXTURE_ROOT": directory, "SCENARIO": scenario, "DRAFT": str(draft).lower(),
                    }
                    result = subprocess.run([bash, str(root / "workflow.sh")], env=env, text=True, capture_output=True, timeout=10)
                    output = result.stdout + result.stderr
                    expected_failure = scenario in ("pagination failed", "post rejected", "post non-json")
                    self.assertEqual(result.returncode != 0, expected_failure, output)
                    approvals = root / "approvals"
                    actual = approvals.read_text() if approvals.exists() else ""
                    expected = "commit_id=" + "a" * 40 + "\n" if scenario in ("approve", "comment event") else ""
                    self.assertEqual(actual, expected, output)
                    self.assertNotIn("dummy-not-a-token", output)
                    if scenario == "post rejected":
                        self.assertIn("fixture rejected review", output)
                        self.assertIn("commit_id", output)
                    if scenario == "post non-json":
                        self.assertIn("without a JSON validation response", output)


if __name__ == "__main__":
    unittest.main()
