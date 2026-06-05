import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# 1. 페이지 기본 설정 & 다크 블루 테마 (FIRE-GATE 스타일)
st.set_page_config(page_title="VR Rebalancing Manager", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    body { background-color: #0f172a; }
    .app-title { font-size: 2.2rem; font-weight: 800; background: linear-gradient(90deg, #38bdf8, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .app-subtitle { color: #94a3b8; font-size: 1rem; margin-bottom: 2rem; }
    .metric-card { background: linear-gradient(145deg, #1e293b, #0f172a); border: 1px solid #334155; border-radius: 16px; padding: 24px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3); margin-bottom: 15px; }
    .metric-label { font-size: 0.85rem; color: #94a3b8; font-weight: 600; letter-spacing: 0.05em; margin-bottom: 8px; }
    .metric-value { font-size: 1.8rem; color: #f8fafc; font-weight: 700; }
    .signal-box-buy { background-color: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; border-radius: 12px; padding: 16px; text-align: center; color: #fca5a5; font-weight: bold; font-size: 1.2rem; }
    .signal-box-sell { background-color: rgba(59, 130, 246, 0.15); border: 1px solid #3b82f6; border-radius: 12px; padding: 16px; text-align: center; color: #93c5fd; font-weight: bold; font-size: 1.2rem; }
    .signal-box-hold { background-color: rgba(148, 163, 184, 0.15); border: 1px solid #94a3b8; border-radius: 12px; padding: 16px; text-align: center; color: #cbd5e1; font-weight: bold; font-size: 1.2rem; }
    </style>
""", unsafe_allow_html=True)

# 2. 구글 시트 연결 설정 (보안이 강화된 금고 방식)
@st.cache_resource
def connect_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # 깃허브 파일 대신 스트림릿 비밀 금고(Secrets)에서 암호를 꺼내옵니다.
    key_dict = json.loads(st.secrets["gcp_json"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
    client = gspread.authorize(creds)
    
    # 공유해주신 시트 URL
    sheet_url = "https://docs.google.com/spreadsheets/d/11TjvYyQ8gXWSHMgm5qnfTbTJXRMO8xN3GIOCaQhtz_0"
    sh = client.open_by_url(sheet_url)
    return sh.worksheet("적립식")

try:
    worksheet = connect_google_sheet()
except Exception as e:
    st.error("구글 시트 연동 에러가 발생했습니다. Streamlit Secrets 설정이나 구글 시트 공유 권한을 확인해주세요.")
    st.stop()

# 3. 실시간 데이터 매핑 (현재 스크린샷 기준 220주차 진행 행인 '119행' 타겟팅)
target_row = 119 

try:
    current_week = worksheet.cell(target_row, 2).value     # B열: 주차 (Week)
    v_target_val = worksheet.cell(target_row, 5).value     # E열: V Target
    stock_qty = worksheet.cell(target_row, 8).value        # H열: 잔고 수량
    current_price = worksheet.cell(target_row, 9).value    # I열: 마감 종가
    portfolio_val = worksheet.cell(target_row, 10).value   # J열: 마감 평가금
    trade_action = worksheet.cell(target_row, 11).value    # K열: 필요 거래 (Hold/Buy/Sell)
    trade_amount = worksheet.cell(target_row, 12).value    # L열: 필요 거래액
except Exception as e:
    current_week, v_target_val, portfolio_val, trade_action, trade_amount, current_price, stock_qty = "Error", "0", "0", "HOLD", "0", "0", "0"

# 4. 메인 화면 그리기
st.markdown('<div class="app-title">VR REBALANCING MANAGER</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">내 구글 시트(VR 5.0.4)와 실시간 연동되는 모바일 현황판</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-label">현재 진행 주차</div><div class="metric-value">{current_week}</div><div style="color:#38bdf8; font-size:0.85rem; margin-top:5px;">시트 B열 연동</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><div class="metric-label">V Target (E열)</div><div class="metric-value">${v_target_val}</div><div style="color:#94a3b8; font-size:0.85rem; margin-top:5px;">목표 가치</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><div class="metric-label">마감 평가금 (J열)</div><div class="metric-value">${portfolio_val}</div><div style="color:#94a3b8; font-size:0.85rem; margin-top:5px;">현재 계좌 상태</div></div>', unsafe_allow_html=True)
with col4:
    if "BUY" in str(trade_action).upper():
        status_html = f'<div class="signal-box-buy">🚨 {trade_action} (${trade_amount})</div>'
    elif "SELL" in str(trade_action).upper():
        status_html = f'<div class="signal-box-sell">💰 {trade_action} (${trade_amount})</div>'
    else:
        status_html = f'<div class="signal-box-hold">💤 {trade_action}</div>'
    st.markdown(f'<div class="metric-card" style="padding:18px 24px;"><div class="metric-label">이번 기수 추천 주문 (K, L열)</div>{status_html}</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📊 상세 현황판", "📝 목요일 마감 데이터 입력"])

with tab1:
    sub1, sub2 = st.columns(2)
    sub1.info(f"📉 **입력된 마감 종가 (I열)**: ${current_price}")
    sub2.success(f"🧱 **현재 잔고 수량 (H열)**: {stock_qty} 개")

with tab2:
    st.subheader(f"📝 {current_week} 마감 데이터 입력 폼")
    with st.form("input_form"):
        new_price = st.number_input("이번 주 마감 종가 입력 (I열 업데이트, $)", min_value=0.0, format="%.2f")
        new_deposit = st.number_input("이번 주 적립금 입력 (N열 업데이트, $)", min_value=0.0, format="%.2f")
        submit_btn = st.form_submit_button("🔥 구글 시트에 실시간 반영하기")
        
        if submit_btn:
            # 사용자가 폼에 입력한 값을 각각 9번째 열(I열)과 14번째 열(N열)에 덮어씁니다.
            worksheet.update_cell(target_row, 9, new_price)   
            worksheet.update_cell(target_row, 14, new_deposit) 
            st.success(f"✅ 구글 시트 {current_week} 업데이트 완료! (앱 화면을 새로고침하면 수식이 반영된 결과가 나타납니다)")
            st.balloons()
