import pandas as pd

# 판매자와 고객의 위치를 시각화하는 함수
def display_map(df_orders_items, seller_id_input):
    # 판매자의 데이터를 필터링
    seller_data = df_orders_items[df_orders_items['seller_id'] == seller_id_input]

    # 판매자 위치 추출
    seller_lat = seller_data['seller_lat'].dropna().unique()
    seller_lng = seller_data['seller_lng'].dropna().unique()

    if len(seller_lat) == 0 or len(seller_lng) == 0:
        return None, None
    else:
        # 판매자 위치 설정
        seller_location = {'lat': seller_lat[0], 'lng': seller_lng[0]}
        customer_locations = []

        # 고객의 위치 데이터 추출
        customer_lats = seller_data['customer_lat'].dropna().values
        customer_lngs = seller_data['customer_lng'].dropna().values

        # 고객의 위도와 경도를 딕셔너리 형태로 저장
        for cust_lat, cust_lng in zip(customer_lats, customer_lngs):
            customer_locations.append({'lat': cust_lat, 'lng': cust_lng})

        return seller_location, customer_locations