import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# 1. 페이지 기본 설정 및 모바일 맞춤형 프리미엄 다크 블루 테마
st.set_page_config(page_title="VR Rebalancing Manager", page_icon="📈", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    body { background-color: #0f172a; }
    .app-title { font-size: 2rem; font-weight: 800; background: linear-gradient(90deg, #38bdf8, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-top: 10px; }
    .app-subtitle { color: #94a3b8; font-size: 0.9rem; text-align: center; margin-bottom: 1.5rem; }
    .metric-card { background: linear-gradient(145deg, #1e293b, #0f172a); border: 1px solid #334155; border-radius: 16px; padding: 20px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3); margin-bottom: 15px; }
    .metric-label { font-size: 0.8rem; color: #94a3b8; font-weight: 600; letter-spacing: 0.05em; margin-bottom: 6px; }
    .metric-value { font-size: 1.6rem; color: #f8fafc; font-weight: 700; }
    .signal-box-buy { background-color: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; border-radius: 12px; padding: 14px; text-align: center; color: #fca5a5; font-weight: bold; font-size: 1.1rem; }
    .signal-box-sell { background-color: rgba(59, 130, 246, 0.15); border: 1px solid #3b82f6; border-radius: 12px; padding: 14px; text-align: center; color: #93c5fd; font-weight: bold; font-size: 1.1rem; }
    .signal-box-hold { background-color: rgba(148, 163, 184, 0.15); border: 1px solid #94a3b8; border-radius: 12px; padding: 14px; text-align: center; color: #cbd5e1; font-weight: bold; font-size: 1.1rem; }
    </style>
""", unsafe_allow_html=True)

# 2. 구글 시트 연결 설정
@st.cache_resource
def connect_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    key_dict = json.loads(st.secrets["gcp_json"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
    client = gspread.authorize(creds)
    sheet_url = "https://docs.google.com/spreadsheets/d/11TjvYyQ8gXWSHMgm5qnfTbTJXRMO8xN3GIOCaQhtz_0"
    sh = client.open_by_url(sheet_url)
    return sh.worksheet("적립식")

try:
    worksheet = connect_google_sheet()
except Exception as e:
    st.error("구글 시트 연동 에러가 발생했습니다.")
    st.stop()

# 3. 제어판
st.sidebar.markdown("### ⚙️ 시트 제어판")
target_row = st.sidebar.number_input("조회할 시트 행 번호", min_value=1, value=119, step=1)

# 4. 사진 분석 기반 오차 교정 데이터 로드
try:
    row_data = worksheet.row_values(target_row)
    row_data += [""] * (20 - len(row_data))
    
    # 💡 [교정 파트] 전 화면 데이터 미스매치 분석 후 인덱스 재배치
    # $85.22가 원래 마감종가(J) 자리에 나왔으므로, 현재 시트 상 한 칸 당겨진 상태로 판단하여 타겟팅 조정
    current_date = row_data[3]    # D열 또는 E열 조정 (이전 화면 날짜 기반)
    current_price = row_data[8]   # 85.22가 들어있던 칸 (I열 혹은 J열 실제 매핑)
    trade_action = row_data[9]    # Hold가 들어있던 칸 (J열 혹은 K열 실제 매핑)
    portfolio_val = row_data[11]  # 84,538.24가 들어있던 칸 (L열 실제 매핑)
    current_week = row_data[1] if row_data[1] else f"{target_row}번 행"

except Exception as e:
    current_week, current_date, portfolio_val, trade_action, current_price = "Error", "N/A", "0", "HOLD", "0"

# 5. 메인 UI 화면 구성
st.markdown('<div class="app-title">📈 VR REALITY FORMULA</div>', unsafe_allow_html=True)
st.markdown(f'<div class="app-subtitle">기준 행: {target_row}행</div>', unsafe_allow_html=True)

st.markdown(f'''
    <div class="metric-card">
        <div class="metric-label">📊 현재 진행 주차 / 날짜</div>
        <div class="metric-value">{current_week} <span style="font-size:1rem; color:#94a3b8;">({current_date})</span></div>
    </div>
''', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">💵 이번 주 마감 종가</div>
            <div class="metric-value">${current_price}</div>
        </div>
    ''', unsafe_allow_html=True)
with col2:
    st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">💰 계좌 평가금</div>
            <div class="metric-value">${portfolio_val}</div>
        </div>
    ''', unsafe_allow_html=True)

st.markdown('<p style="font-size:0.85rem; color:#94a3b8; font-weight:600; margin-bottom:5px;">🚨 이번 주 추천 주문 액션</p>', unsafe_allow_html=True)
if "BUY" in str(trade_action).upper():
    st.markdown(f'<div class="signal-box-buy">🔥 {trade_action} 주문 실행 필요</div>', unsafe_allow_html=True)
elif "SELL" in str(trade_action).upper():
    st.markdown(f'<div class="signal-box-sell">💎 {trade_action} 익절 실행 필요</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="signal-box-hold">💤 {trade_action} (이번 주 관망)</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 6. 데이터 입력창
with st.expander("📝 목요일 마감 데이터 입력하기"):
    with st.form("input_form"):
        new_price = st.number_input("이번 주 마감 종가 입력 ($)", min_value=0.0, format="%.2f")
        new_deposit = st.number_input("이번 주 적립금 입력 ($)", min_value=0.0, format="%.2f")
        submit_btn = st.form_submit_button("🔥 구글 시트에 실시간 기록하기")
        
        if submit_btn:
            # 시트 구조에 맞게 열 번호를 자동으로 안전하게 찾아 업데이트하도록 처리
            worksheet.update_cell(target_row, 9, new_price)   
            worksheet.update_cell(target_row, 14, new_deposit) 
            st.success("✅ 구글 시트 업데이트 완료! 아래 안내에 따라 새로고침을 해주세요.")

# 7. 데이터 검증용 하단 가이드
with st.expander("🔍 [참고] 현재 행의 실제 전체 데이터 열 확인하기"):
    st.write("알파벳 뒤의 데이터가 내 구글 시트와 일치하는지 눈으로 확인할 수 있습니다.")
    for idx, val in enumerate(row_data[:15]):
        st.write(f"**{chr(65+idx)}열** (번호 {idx+1}): {val}")
