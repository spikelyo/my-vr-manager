import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# 1. 모바일 최적화 페이지 설정
st.set_page_config(page_title="VR Manager", layout="centered")

# 2. 구글 시트 연결 (보안 금고 방식)
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
    
    # ⚠️ 현재 데이터를 읽어올 행 번호 (220주차 기준 = 119행)
    target_row = 119
    
    # ⚠️ 정확한 열(Column) 번호를 직접 지정하여 데이터를 가져옵니다. (데이터 꼬임 방지)
    week = worksheet.cell(target_row, 2).value       # B열(2) : 주차
    v_target = worksheet.cell(target_row, 5).value   # E열(5) : V Target
    eval_val = worksheet.cell(target_row, 10).value  # J열(10): 마감 평가금
    action = worksheet.cell(target_row, 11).value    # K열(11): 필요 거래 (Hold/Buy/Sell)
    trade_amt = worksheet.cell(target_row, 12).value # L열(12): 필요 거래액

    # 빈칸일 경우를 대비한 기본값 처리
    week = week if week else "N/A"
    v_target = v_target if v_target else "0"
    eval_val = eval_val if eval_val else "0"
    action = action if action else "Hold"
    trade_amt = trade_amt if trade_amt else "0"

    # 모바일용 UI 화면 구성
    st.title("📈 VR 실력공식")
    st.subheader(f"현재 주차: {week}")
    
    # 카드형 데이터 표시
    col1, col2 = st.columns(2)
    col1.metric("V Target", f"${v_target}")
    col2.metric("평가금", f"${eval_val}")
    
    st.info(f"💰 이번 주 액션: **{action}** (${trade_amt})")
    
    # 마감 데이터 입력 폼 (모바일에서 쓰기 편하게 숨김 처리)
    with st.expander("📝 이번 주 데이터 입력하기"):
        with st.form("input_form"):
            new_price = st.number_input("이번 주 마감 종가 (I열, $)", format="%.2f")
            new_deposit = st.number_input("이번 주 적립금 (N열, $)", format="%.2f")
            submit = st.form_submit_button("시트에 반영")
            
            if submit:
                worksheet.update_cell(target_row, 9, new_price)    # I열(9)에 종가 입력
                worksheet.update_cell(target_row, 14, new_deposit) # N열(14)에 적립금 입력
                st.success("✅ 구글 시트에 완벽하게 반영되었습니다! (새로고침을 눌러주세요)")

except Exception as e:
    st.error(f"연동 실패 또는 에러 발생: {e}")
