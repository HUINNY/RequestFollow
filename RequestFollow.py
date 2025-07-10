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
    text = request.form.get('text')  # 슬랙 커맨드 입력 내용
    user = request.form.get('user_name')  # 입력한 사용자

    try:
        # Jira API 호출
        response = requests.post(
            f"https://{JIRA_DOMAIN}/rest/api/2/issue", # ✅ On-prem 기준
            auth=(JIRA_EMAIL, JIRA_API_TOKEN),
            headers={"Content-Type": "application/json"},
            json={
                "fields": {
                    "project": {"key": JIRA_PROJECT_KEY},
                    "summary": f"[Slack 요청] {text}",
                    "description": f"Slack 사용자 {user}의 요청",
                    "issuetype": {"name": JIRA_ISSUE_TYPE},
                    "reporter": {"name": "huinkim"}  # ✅ Reporter 지정
                }
            },
            verify=False  # 인증서 오류 방지용 (보안상 개선 여지 있음)
        )

        # 성공 시 Slack에 이슈 링크 응답
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
            text=f":x: 서버 오류 발생: {str(e)}"
        )
