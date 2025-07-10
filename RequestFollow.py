from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

app = Flask(__name__)

# 환경 변수에서 Jira 및 Slack 설정 로드
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
JIRA_EMAIL = os.environ["JIRA_EMAIL"]
JIRA_API_TOKEN = os.environ["JIRA_API_TOKEN"]
JIRA_DOMAIN = os.environ["JIRA_DOMAIN"]  # 예: yourteam.atlassian.net
JIRA_PROJECT_KEY = os.environ["JIRA_PROJECT_KEY"]  # 예: MSW
JIRA_ISSUE_TYPE = "Request"  # 정확한 이슈 타입 이름 필요 (예: Task, Service Request 등)

@app.route("/slack/request-create", methods=["POST"])
def create_issue():
    text = request.form.get('text')
    user = request.form.get('user_name')

    print("슬랙으로부터 요청 수신됨")
    print(f"입력된 내용: {text}")
    print(f"사용자 이름: {user}")

    try:
        response = requests.post(
            f"https://{JIRA_DOMAIN}/rest/api/2/issue",
            auth=(JIRA_EMAIL, JIRA_API_TOKEN),
            headers={"Content-Type": "application/json"},
            json={
                "fields": {
                    "project": {"key": JIRA_PROJECT_KEY},
                    "summary": f"[Slack 요청] {text}",
                    "description": f"Slack 사용자 {user}의 요청",
                    "issuetype": {"name": JIRA_ISSUE_TYPE},
                    "reporter": {"name": "huinkim"}  # 필요시 제거
                }
            },
            verify=False
        )

        print(f"Jira 응답 코드: {response.status_code}")
        print(f"Jira 응답 본문: {response.text}")

        if response.status_code == 201:
            issue_key = response.json()["key"]
            issue_url = f"https://{JIRA_DOMAIN}/browse/{issue_key}"
            return {
                "response_type": "in_channel",
                "text": f":white_check_mark: Jira 이슈가 생성되었습니다: <{issue_url}|{issue_key}>"
            }
        else:
            return {
                "response_type": "ephemeral",
                "text": f":x: 이슈 생성 실패\n{response.status_code} - {response.text}"
            }

    except Exception as e:
        return {
            "response_type": "ephemeral",
            "text": f":x: 서버 오류 발생: {str(e)}"
        }
