from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
JIRA_EMAIL = os.environ["JIRA_EMAIL"]       # Atlassian 계정 이메일
JIRA_API_TOKEN = os.environ["JIRA_API_TOKEN"]  # Atlassian API 토큰
JIRA_DOMAIN = os.environ["JIRA_DOMAIN"]     # 예: yourdomain.atlassian.net
JIRA_PROJECT_KEY = os.environ["JIRA_PROJECT_KEY"]  # 프로젝트 키, 예: TEST
JIRA_ISSUE_TYPE = "Request" # ← 정확히 이슈 타입 이름 확인 필요

@app.route("/slack/request-create", methods=["POST"])
def create_issue():
    text = request.form.get('text')
    user = request.form.get('user_name')

    # Jira 이슈 생성 요청
    response = requests.post(
        f"https://{JIRA_DOMAIN}/rest/api/3/issue",
        auth=(JIRA_EMAIL, JIRA_API_TOKEN),
        headers={"Content-Type": "application/json"},
        json={
            "fields": {
                "project": {"key": JIRA_PROJECT_KEY},
                "summary": f"[Slack 요청] {text}",
                "description": f"Slack에서 요청한 사용자: {user}",
                "issuetype": {"name": JIRA_ISSUE_TYPE}
            }
        }
    )

    if response.status_code == 201:
        issue_key = response.json()["key"]
        issue_url = f"https://{JIRA_DOMAIN}/browse/{issue_key}"
        return jsonify(
            response_type="in_channel",
            text=f":white_check_mark: Jira 이슈가 생성되었습니다: <{issue_url}|{issue_key}>"
        )
    else:
        return jsonify(
            response_type="ephemeral",
            text=f":x: 이슈 생성 실패\n{response.status_code} - {response.text}"
        )

response = requests.post(
    f"https://{JIRA_DOMAIN}/rest/api/3/issue",
    auth=(JIRA_EMAIL, JIRA_API_TOKEN),
    headers={"Content-Type": "application/json"},
    json={
        "fields": {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": f"[Slack 요청] {text}",
            "description": f"Slack 사용자 {user}의 요청",
            "issuetype": {"name": JIRA_ISSUE_TYPE}
        }
    }
    # verify=False  ← (보안상 권장 안되지만 임시 해결책)
)
