# login.py
import streamlit as st

def login_screen():
    """
    판매자 ID를 입력받는 로그인 화면을 구현하는 함수
    """
    seller_id_input = st.text_input("판매자 ID를 입력하세요:")

    if not seller_id_input:
        st.warning("판매자 ID를 입력해 주세요.")  # 이 메시지는 한 번만 출력됩니다.
    
    return seller_id_input