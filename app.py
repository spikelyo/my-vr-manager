import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

st.set_page_config(page_title="VR Rebalancing", layout="wide")

# 스트림릿 Secrets에서 키를 가져오도록 수정된 함수
@st.cache_resource
def connect_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # 여기서 st.secrets["gcp_json"]을 호출합니다.
    # 이 키 이름이 스트림릿 설정의 Secrets 탭에 정확히 gcp_json으로 있어야 합니다.
    creds_dict = json.loads(st.secrets["gcp_json"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    sheet_url = "https://docs.google.com/spreadsheets/d/11TjvYyQ8gXWSHMgm5qnfTbTJXRMO8xN3GIOCaQhtz_0"
    sh = client.open_by_url(sheet_url)
    return sh.worksheet("적립식")

# 앱 실행
try:
    worksheet = connect_google_sheet()
    target_row = 119
    # 데이터 로드
    val = worksheet.cell(target_row, 5).value
    st.write(f"현재 V Target 값: {val}")
except Exception as e:
    st.error(f"연동 에러 발생: {e}")
