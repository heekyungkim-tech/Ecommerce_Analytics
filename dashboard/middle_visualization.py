# 중앙 지도, 배송 시각화 모듈
import folium
from streamlit_folium import st_folium
import streamlit as st
from folium.plugins import AntPath

def display_map(df_orders_items, seller_id_input):
    st.subheader("판매자의 판매 및 배송 경로 지도")
    
    # 판매자의 데이터를 필터링
    seller_data = df_orders_items[df_orders_items['seller_id'] == seller_id_input]

    # 판매자 위치 추출
    seller_lat = seller_data['seller_lat'].dropna().unique()
    seller_lng = seller_data['seller_lng'].dropna().unique()

    if len(seller_lat) == 0 or len(seller_lng) == 0:
        st.write("판매자의 위치 정보가 없습니다.")
    else:
        seller_location = [seller_lat[0], seller_lng[0]]
        customer_lats = seller_data['customer_lat'].dropna().values
        customer_lngs = seller_data['customer_lng'].dropna().values

        # 지도 생성
        map_center = [seller_lat[0], seller_lng[0]]
        map1 = folium.Map(location=map_center, zoom_start=5)

        # 판매자 마커 추가
        folium.Marker(location=seller_location, popup="판매자 위치", icon=folium.Icon(color='red')).add_to(map1)

        # 고객 위치와 경로 추가
        for cust_lat, cust_lng in zip(customer_lats, customer_lngs):
            customer_location = [cust_lat, cust_lng]
            folium.CircleMarker(location=customer_location, radius=2, color='blue', fill=True).add_to(map1)
            AntPath(locations=[seller_location, customer_location], color='green', weight=1, delay=1000).add_to(map1)

        # 지도 출력
        st_folium(map1, width=700, height=500)