from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
JIRA_EMAIL = os.environ["JIRA_EMAIL"]
JIRA_API_TOKEN = os.environ["JIRA_API_TOKEN"]
JIRA_DOMAIN = os.environ["JIRA_DOMAIN"]
JIRA_PROJECT_KEY = os.environ["JIRA_PROJECT_KEY"]
JIRA_ISSUE_TYPE = "Request"  # 정확한 이슈 타입 이름인지 확인 필요

@app.route("/slack/request-create", methods=["POST"])
def create_issue():
    text = request.form.get('text')
    user = request.form.get('user_name')

    try:
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
            },
            verify=False  
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
    except Exception as e:
        return jsonify(
            response_type="ephemeral",
            text=f":x: 서버 오류: {str(e)}"
        )
