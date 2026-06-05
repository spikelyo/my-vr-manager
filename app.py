import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# 1. 모바일 최적화 페이지 설정
st.set_page_config(page_title="VR Manager", layout="centered")

# 2. 구글 시트 연결 (기존 시크릿 방식 유지)
@st.cache_resource
def connect_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    key_dict = json.loads(st.secrets["gcp_json"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
    client = gspread.authorize(creds)
    sheet_url = "https://docs.google.com/spreadsheets/d/11TjvYyQ8gXWSHMgm5qnfTbTJXRMO8xN3GIOCaQhtz_0"
    sh = client.open_by_url(sheet_url)
    return sh.worksheet("적립식")

# 3. 데이터 로드 및 UI (아이폰용 디자인)
try:
    worksheet = connect_google_sheet()
    target_row = 119
    
    # 시트 데이터 가져오기
    data = worksheet.row_values(target_row)
    # B:2, E:5, H:8, I:9, J:10, K:11, L:12
    week = data[1]
    v_target = data[4]
    balance = data[7]
    price = data[8]
    eval_val = data[9]
    action = data[10]
    trade_amt = data[11]

    # 모바일용 UI
    st.title("📈 VR 실력공식")
    st.subheader(f"현재 주차: {week}")
    
    # 카드형 데이터 표시
    col1, col2 = st.columns(2)
    col1.metric("V Target", f"${v_target}")
    col2.metric("평가금", f"${eval_val}")
    
    st.info(f"💰 이번 주 액션: **{action}** (${trade_amt})")
    
    # 마감 데이터 입력 폼 (모바일에서 쓰기 편하게)
    with st.expander("📝 이번 주 데이터 입력하기"):
        with st.form("input_form"):
            new_price = st.number_input("마감 종가 ($)", format="%.2f")
            new_deposit = st.number_input("적립금 ($)", format="%.2f")
            submit = st.form_submit_button("시트에 반영")
            
            if submit:
                worksheet.update_cell(target_row, 9, new_price)
                worksheet.update_cell(target_row, 14, new_deposit)
                st.success("반영 완료! 새로고침하세요.")

except Exception as e:
    st.error(f"연동 실패: {e}")
