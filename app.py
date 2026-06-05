import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import pandas as pd
from datetime import datetime

# 1. 모바일 프리미엄 다크 테마 및 UI 레이아웃 설정
st.set_page_config(page_title="VR Master Dashboard", page_icon="⚡", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    body { background-color: #0f172a; }
    .app-title { font-size: 1.8rem; font-weight: 800; background: linear-gradient(90deg, #38bdf8, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-top: 10px; }
    .app-subtitle { color: #94a3b8; font-size: 0.9rem; text-align: center; margin-bottom: 1.5rem; }
    .metric-card { background: linear-gradient(145deg, #1e293b, #0f172a); border: 1px solid #334155; border-radius: 16px; padding: 18px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3); margin-bottom: 12px; }
    .metric-label { font-size: 0.8rem; color: #94a3b8; font-weight: 600; letter-spacing: 0.05em; margin-bottom: 4px; }
    .metric-value { font-size: 1.6rem; color: #f8fafc; font-weight: 700; }
    .section-title { font-size: 1.2rem; font-weight: 700; color: #38bdf8; margin-top: 25px; margin-bottom: 12px; border-left: 4px solid #3b82f6; padding-left: 8px; }
    
    /* 추천 액션 및 밸류 밴드 통합 스타일 변환 */
    .signal-container-buy { background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(239, 68, 68, 0.05)); border: 1px solid #ef4444; border-radius: 16px; padding: 18px; color: #fca5a5; margin-bottom: 15px; }
    .signal-container-sell { background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(59, 130, 246, 0.05)); border: 1px solid #3b82f6; border-radius: 16px; padding: 18px; color: #93c5fd; margin-bottom: 15px; }
    .signal-container-hold { background: linear-gradient(135deg, rgba(148, 163, 184, 0.15), rgba(148, 163, 184, 0.03)); border: 1px solid #64748b; border-radius: 16px; padding: 18px; color: #cbd5e1; margin-bottom: 15px; }
    .signal-header { font-size: 1.3rem; font-weight: 800; margin-bottom: 8px; display: flex; align-items: center; gap: 6px; }
    .signal-meta { font-size: 0.85rem; color: #94a3b8; line-height: 1.5; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 8px; margin-top: 4px; }
    </style>
""", unsafe_allow_html=True)

# 2. 구글 시트 보안 파이프라인 연동
sheet_url = "https://docs.google.com/spreadsheets/d/11TjvYyQ8gXWSHMgm5qnfTbTJXRMO8xN3GIOCaQhtz_0"

@st.cache_resource
def connect_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    key_dict = json.loads(st.secrets["gcp_json"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
    client = gspread.authorize(creds)
    sh = client.open_by_url(sheet_url)
    return sh

try:
    sh = connect_google_sheet()
    acc_sheet = sh.worksheet("적립식")
    order_sheet = sh.worksheet("주문")
except Exception as e:
    st.error("구글 시트 연동에 실패했습니다. Streamlit Secrets 설정을 점검하세요.")
    st.stop()

# 3. 사이드바 주차 검색 시스템 (기본값 설정: 220주차)
st.sidebar.markdown("### 📅 주차 관리 패널")
search_week = st.sidebar.text_input("조회할 주차 입력", value="220주차")

# 4. 실시간 데이터 파싱 및 매핑
try:
    # '적립식' 탭 데이터 정밀 매핑 (실제 구글 시트 배치 구조 반영)
    weeks_col = acc_sheet.col_values(3)
    
    if search_week in weeks_col:
        target_row = weeks_col.index(search_week) + 1
        row_vals = acc_sheet.row_values(target_row)
        row_vals += [""] * (20 - len(row_vals))
        
        # 컬럼 인덱스 매핑 (C열 기준 순서 매칭)
        v_target = row_vals[5]       # F열: V Target
        v_min = row_vals[6]          # G열: V min
        v_max = row_vals[7]          # H열: V max
        qty_balance = row_vals[8]    # I열: 잔고 수량 (정확히 992주 연동)
        current_price = row_vals[9]  # J열: 현재가 ($85.22)
        eval_val = row_vals[10]      # K열: 마감 평가금
        action = row_vals[11]        # L열: 필요 거래
        pool_val = row_vals[15]      # P열: 현금 Pool
    else:
        st.error(f"시트 내에서 '{search_week}' 데이터를 조회할 수 없습니다.")
        st.stop()

    # '주문' 탭 지정가 대기 테이블 파싱 (I10:K35 범위 자동 로드)
    raw_orders = order_sheet.get("I10:K35")
    if raw_orders and len(raw_orders) > 1:
        # 데이터가 존재할 경우 테이블 데이터프레임 빌드
        df_orders = pd.DataFrame(raw_orders[1:], columns=["순번", "예약 매수단가 ($)", "예약 매도단가 ($)"])
    else:
        df_orders = pd.DataFrame()

except Exception as e:
    st.error(f"시트 데이터를 읽어오는 중 에러 발생: {e}")
    st.stop()

# 5. 메인 UI 화면 구성
st.markdown(f'<div class="app-title">💎 VR {search_week} 실시간 매니저</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">적립식 실력공식 지표 & 예약 주문 단가 시스템</div>', unsafe_allow_html=True)

# 🚨 요구사항 반영: 추천 액션 박스 내부에 Vmin, Vmax, V Target 통합 바인딩
action_upper = str(action).upper()
if "BUY" in action_upper:
    st.markdown(f'''
        <div class="signal-container-buy">
            <div class="signal-header">🔴 추천 액션: {action} 신호 발생</div>
            <div class="signal-meta">
                • <b>현재 V 목표 (V Target):</b> ${v_target}<br>
                • <b>안전 하한선 (V min):</b> ${v_min} (현재가 미달 시 분할매수 권장)<br>
                • <b>안전 상한선 (V max):</b> ${v_max}
            </div>
        </div>
    ''', unsafe_allow_html=True)
elif "SELL" in action_upper:
    st.markdown(f'''
        <div class="signal-container-sell">
            <div class="signal-header">🔵 추천 액션: {action} 신호 발생</div>
            <div class="signal-meta">
                • <b>현재 V 목표 (V Target):</b> ${v_target}<br>
                • <b>안전 하한선 (V min):</b> ${v_min}<br>
                • <b>안전 상한선 (V max):</b> ${v_max} (현재가 초과 시 분할매도 권장)
            </div>
        </div>
    ''', unsafe_allow_html=True)
else:
    st.markdown(f'''
        <div class="signal-container-hold">
            <div class="signal-header">⚪ 추천 액션: {action} (포지션 유지)</div>
            <div class="signal-meta">
                • <b>현재 밸류 목표 (V Target):</b> ${v_target}<br>
                • <b>안전 밸류 밴드 범위:</b> ${v_min} ~ ${v_max}<br>
                • <b>가이드:</b> 이번 주차는 무리한 시장가 매매 없이 아래 지정가 단가표대로 예약 주문만 걸어두세요.
            </div>
        </div>
    ''', unsafe_allow_html=True)

# 기본 계좌 현황 지표 레이아웃 (잔고수량 오류 수정 완료)
col1, col2 = st.columns(2)
with col1:
    st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">💵 현재가 / 마감 종가 (J열)</div>
            <div class="metric-value">${current_price}</div>
        </div>
    ''', unsafe_allow_html=True)
with col2:
    st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">📦 실제 잔고 수량 (I열)</div>
            <div class="metric-value" style="color: #38bdf8;">{qty_balance} 주</div>
        </div>
    ''', unsafe_allow_html=True)

col3, col4 = st.columns(2)
with col3:
    st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">💰 마감 평가금 (K열)</div>
            <div class="metric-value">${eval_val}</div>
        </div>
    ''', unsafe_allow_html=True)
with col4:
    st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">🏦 계좌 현금 Pool (P열)</div>
            <div class="metric-value" style="color: #34d399;">${pool_val}</div>
        </div>
    ''', unsafe_allow_html=True)

# 6. 이번 주차 매수/매도 지정가 예약 단가표 섹션
st.markdown('<div class="section-title">📊 주문 탭 연동 이번 주 예약 주문 단가표</div>', unsafe_allow_html=True)
st.markdown('<p style="font-size:0.8rem; color:#94a3b8; margin-top:-5px; margin-bottom:10px;">구글 시트 주문 서식에 기재된 이번 주차의 예약 체결 대기 가격선입니다.</p>', unsafe_allow_html=True)

if not df_orders.empty:
    st.dataframe(df_orders, use_container_width=True, hide_index=True)
else:
    st.warning("⚠️ '주문' 탭의 지정가 범위(I10:K35)에 데이터가 없거나 로드되지 않았습니다. 시트의 해당 열을 채워주세요.")

# 7. 실제 주문 완료 기록 장치
st.markdown('<div class="section-title">📝 실제 주문 매도/매수 내역 기록 추가</div>', unsafe_allow_html=True)

with st.form("vr_final_log_form"):
    ticker = st.text_input("Ticker", value="TQQQ")
    trade_type = st.radio("거래 구분", ["매수", "매도"], horizontal=True)
    trade_qty = st.number_input("체결 수량 (주)", min_value=0, value=4, step=1)
    trade_price = st.number_input("체결 단가 ($)", min_value=0.0, value=0.0, format="%.2f")
    trade_fee = st.number_input("수수료 ($)", min_value=0.0, value=0.0, format="%.2f")
    
    submit_btn = st.form_submit_button("⚡ 구글 시트에 업데이트 전송")
    
    if submit_btn:
        try:
            record_worksheet = sh.worksheet("Record")
            today_str = datetime.now().strftime("%Y-%m-%d")
            total_amount = trade_qty * trade_price
            
            new_row = [today_str, search_week, ticker, trade_type, trade_qty, trade_price, total_amount, trade_fee]
            record_worksheet.append_row(new_row)
            
            st.success(f"🎉 {search_week} {trade_type} 내역 ({trade_qty}주 / ${trade_price})이 'Record' 탭에 정상 기록되었습니다!")
        except Exception as e:
            st.error(f"기록 실패: {e}\n시트 내부에 'Record' 탭이 명확히 존재하는지 점검해 보세요.")
