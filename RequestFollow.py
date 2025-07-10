from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
JIRA_EMAIL = os.environ["JIRA_EMAIL"]       # Atlassian 계정 이메일
JIRA_API_TOKEN = os.environ["JIRA_API_TOKEN"]  # Atlassian API 토큰
JIRA_DOMAIN = os.environ["JIRA_DOMAIN"]     # 예: yourdomain.atlassian.net
JIRA_PROJECT_KEY = os.environ["JIRA_PROJECT_KEY"]  # 프로젝트 키, 예: TEST

app = Flask(__name__)

@app.route('/slack/request-create', methods=['POST'])
def create_issue():
    return "✅ 요청 잘 받았어요!", 200

if __name__ == '__main__':
    app.run(port=5000, host="0.0.0.0")
