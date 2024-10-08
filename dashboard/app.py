# 메인 실행 모듈

import streamlit as st
from data_processing import load_data
from left_rfm_analytics import display_rfm_analysis
from middle_visualization import display_map
from right_module import display_summary
from login import login_screen

# 데이터 경로 설정
raw_path = './data/'

# 데이터 로드 및 전처리
df_orders_items = load_data(raw_path)

# Streamlit 앱 설정
st.set_page_config(page_title="E-commerce KPI Dashboard", page_icon="✅", layout="wide")

# 로그인 화면 호출
seller_id_input = login_screen()

# 로그인 성공 시
if seller_id_input:  # 로그인 화면에서 입력이 있을 때만 실행
    if seller_id_input in df_orders_items['seller_id'].values:
        # 로그인 성공 후 다음 화면으로 이동
        st.session_state['logged_in'] = True

        # 화면 레이아웃 설정
        col1, col2, col3 = st.columns(3)

        # 왼쪽: RFM 분석
        with col1:
            display_rfm_analysis(df_orders_items, seller_id_input)

        # 가운데: 판매자 위치 및 지도
        with col2:
            display_map(df_orders_items, seller_id_input)

        # 오른쪽: 추가적인 분석 요약
        with col3:
            display_summary(df_orders_items, seller_id_input)
    else:
        st.error("판매자 ID를 찾을 수 없습니다.")