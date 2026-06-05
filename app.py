import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from datetime import datetime

# 1. 모바일 최적화 및 프리미엄 다크 테마 설정
st.set_page_config(page_title="VR Reality APP", page_icon="📈", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    body { background-color: #0f172a; }
    .app-title { font-size: 1.8rem; font-weight: 800; background: linear-gradient(90deg, #38bdf8, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-top: 10px; }
    .app-subtitle { color: #94a3b8; font-size: 0.9rem; text-align: center; margin-bottom: 1.5rem; }
    .metric-card { background: linear-gradient(145deg, #1e293b, #0f172a); border: 1px solid #334155; border-radius: 16px; padding: 18px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3); margin-bottom: 12px; }
    .metric-label { font-size: 0.8rem; color: #94a3b8; font-weight: 600; letter-spacing: 0.05em; margin-bottom: 4px; }
    .metric-value { font-size: 1.6rem; color: #f8fafc; font-weight: 700; }
    .section-title { font-size: 1.2rem; font-weight: 700; color: #38bdf8; margin-top: 20px; margin-bottom: 10px; border-left: 4px solid #3b82f6; padding-left: 8px; }
    
    /* 구글 시트 스타일의 서브 컴포넌트 */
    .form-container { background-color: #1e293b; border: 1px solid #475569; border-radius: 12px; padding: 20px; margin-top: 15px; }
    .signal-box-buy { background-color: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; border-radius: 12px; padding: 14px; text-align: center; color: #fca5a5; font-weight: bold; }
    .signal-box-sell { background-color: rgba(59, 130, 246, 0.15); border: 1px solid #3b82f6; border-radius: 12px; padding: 14px; text-align: center; color: #93c5fd; font-weight: bold; }
    .signal-box-hold { background-color: rgba(148, 163, 184, 0.12); border: 1px solid #475569; border-radius: 12px; padding: 14px; text-align: center; color: #94a3b8; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 2. 구글 시트 안전 연결
sheet_url = "https://docs.google.com/spreadsheets/d/11TjvYyQ8gXWSHMgm5qnfTbTJXRMO8xN3GIOCaQhtz_0"

@st.cache_resource
def connect_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    key_dict = json.loads(st.secrets["gcp_json"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
    client = gspread.authorize(creds)
    sh = client.open_by_url(sheet_url)
    return client, sh

try:
    client, sh = connect_google_sheet()
    worksheet = sh.worksheet("적립식")
except Exception as e:
    st.error("구글 시트 연동에 실패했습니다. 비밀 금고 설정을 확인하세요.")
    st.stop()

# 3. 사이드바 제어판 (행 번호 설정)
st.sidebar.markdown("### ⚙️ 시트 제어판")
target_row = st.sidebar.number_input("조회할 시트 행 번호", min_value=1, value=119, step=1)

# 4. 실시간 데이터 정밀 로드 (image_4.png 기준 매핑 완료)
try:
    # B(2):주차, E(5):V Target, F(6):V min, G(7):V max, H(8):잔고수량, I(9):현재가, J(10):평가금, K(11):필요거래
    week = worksheet.cell(target_row, 2).value        # 220주차
    v_target = worksheet.cell(target_row, 5).value    # 79,139.49
    v_min = worksheet.cell(target_row, 6).value       # 67,268.57
    v_max = worksheet.cell(target_row, 7).value       # 91,010.41
    qty_balance = worksheet.cell(target_row, 8).value # 992
    current_price = worksheet.cell(target_row, 9).value # 85.22
    eval_val = worksheet.cell(target_row, 10).value   # 84,538.24
    action = worksheet.cell(target_row, 11).value     # Hold
    
except Exception as e:
    st.error(f"데이터 로드 실패: {e}")
    st.stop()

# 5. 메인 대시보드 UI 출력
st.markdown('<div class="app-title">📈 VR REALITY DASHBOARD</div>', unsafe_allow_html=True)
st.markdown(f'<div class="app-subtitle">적립식 실력공식 — {week if week else f"{target_row}행"} 실시간 연동 중</div>', unsafe_allow_html=True)

# 상단 핵심 지표 카드 (현재가 및 평가금)
col1, col2 = st.columns(2)
with col1:
    st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">💵 현재가 / 마감 종가 (I열)</div>
            <div class="metric-value">${current_price}</div>
        </div>
    ''', unsafe_allow_html=True)
with col2:
    st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">💰 마감 평가금 (J열)</div>
            <div class="metric-value">${eval_val}</div>
        </div>
    ''', unsafe_allow_html=True)

# 밸류 타겟 및 수량 정보
st.markdown(f'''
    <div class="metric-card">
        <div class="metric-label">🎯 밸류 목표 (V Target) / 잔고 수량</div>
        <div class="metric-value" style="color: #38bdf8;">${v_target} <span style="font-size:1.1rem; color:#94a3b8;">({qty_balance} 주 보유)</span></div>
    </div>
''', unsafe_allow_html=True)

# 이번 주 매매 추천 신호 표시
st.markdown('<p style="font-size:0.85rem; color:#94a3b8; font-weight:600; margin-bottom:6px;">🚨 이번 주 수식 추천 액션 (K열)</p>', unsafe_allow_html=True)
action_upper = str(action).upper() if action else "HOLD"
if "BUY" in action_upper:
    st.markdown(f'<div class="signal-box-buy">🔥 {action} 신호 활성화</div>', unsafe_allow_html=True)
elif "SELL" in action_upper:
    st.markdown(f'<div class="signal-box-sell">💎 {action} 신호 활성화</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="signal-box-hold">💤 {action} (이번 주 추가 매매 없음)</div>', unsafe_allow_html=True)

# 6. 실제 주문 기록 입력 폼 (구글 시트 우측 APP 컴포넌트 완벽 재현)
st.markdown('<div class="section-title">📝 실제 주문 매도/매수 기록하기</div>', unsafe_allow_html=True)
st.markdown('<p style="font-size:0.8rem; color:#94a3b8; margin-top:-5px; margin-bottom:10px;">실제 체결된 내역을 입력하면 구글 시트의 Record 탭에 순서대로 기록됩니다.</p>', unsafe_allow_html=True)

with st.form("vr_order_form"):
    ticker = st.text_input("Ticker", value="TQQQ")
    
    # 매수 / 매도 선택 토글 버튼
    trade_type = st.radio("거래 구분", ["매수", "매도"], horizontal=True)
    
    # 수량, 거래액, 수수료 입력 칸
    trade_qty = st.number_input("거래 수량", min_value=0, value=0, step=1)
    trade_amt = st.number_input("거래액 ($)", min_value=0.0, value=0.0, format="%.2f")
    trade_fee = st.number_input("수수료 ($)", min_value=0.0, value=0.0, format="%.2f")
    
    # 제출 버튼
    submit_btn = st.form_submit_button("⚡ Update (구글 시트에 전송)")
    
    if submit_btn:
        try:
            # 구글 시트의 'Record' 탭을 열어서 하단에 한 행을 추가합니다.
            record_worksheet = sh.worksheet("Record")
            
            # 입력 데이터 구성 (날짜, 주차, 티커, 구분, 수량, 거래액, 수수료)
            today_date = datetime.now().strftime("%Y-%m-%d")
            new_row = [today_date, week, ticker, trade_type, trade_qty, trade_amt, trade_fee]
            
            # 시트에 기록 추가 실행
            record_worksheet.append_row(new_row)
            st.success(f"🎉 {week} {trade_type} 내역이 구글 시트 'Record' 탭에 정상적으로 기록되었습니다!")
            
        except Exception as e:
            st.error(f"시트 기록 중 오류가 발생했습니다: {e}\n구글 시트에 'Record' 이름의 탭이 존재하는지 확인해 주세요.")
