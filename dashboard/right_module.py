# 오른쪽 모듈
import streamlit as st

def display_summary(df_orders_items, seller_id_input):
    # 간단한 더미 데이터 출력 (예시)
    st.subheader("판매자 데이터 기반 위치 분석")
    st.metric(label="판매 금액", value="23%", delta="3% 증가")
    st.write("AI Insight: 판매자는 지역적으로 집중된 고객 기반을 가지고 있습니다.")