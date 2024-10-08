# Import statements
import pandas as pd
import numpy as np
import plotly.express as px
import requests
import json
import folium
from folium.plugins import AntPath
import plotly.graph_objects as go

import streamlit as st
from streamlit_folium import st_folium

# Reading all the files
raw_path = '/Users/heekyungkim/KPMG_Project/archive/'  
olist_customer = pd.read_csv(raw_path + 'olist_customers_dataset.csv')
olist_geolocation = pd.read_csv(raw_path + 'olist_geolocation_dataset.csv')
olist_orders = pd.read_csv(raw_path + 'olist_orders_dataset.csv')
olist_order_items = pd.read_csv(raw_path + 'olist_order_items_dataset.csv')
olist_order_payments = pd.read_csv(raw_path + 'olist_order_payments_dataset.csv')
olist_order_reviews = pd.read_csv(raw_path + 'olist_order_reviews_dataset.csv')
olist_products = pd.read_csv(raw_path + 'olist_products_dataset.csv')
olist_sellers = pd.read_csv(raw_path + 'olist_sellers_dataset.csv')

# Merge datasets
df_orders = olist_orders.merge(olist_customer, how='left', on='customer_id')
df_order_items = olist_order_items.merge(olist_sellers, how='left', on='seller_id')
df_orders_items = df_orders.merge(df_order_items, how='left', on='order_id')

# Changing the data type for date columns
timestamp_cols = ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date',
                  'order_estimated_delivery_date']
for col in timestamp_cols:
    df_orders_items[col] = pd.to_datetime(df_orders_items[col])

# Extracting attributes for purchase date - Year and Month
df_orders_items['order_purchase_year'] = df_orders_items['order_purchase_timestamp'].dt.year
df_orders_items['order_purchase_month'] = df_orders_items['order_purchase_timestamp'].dt.month
df_orders_items['order_purchase_year_month'] = df_orders_items['order_purchase_timestamp'].dt.strftime('%Y%m')

# RFM 분석을 위한 기준 날짜 설정 (데이터 내 가장 최근 날짜로 설정)
snapshot_date = df_orders_items['order_purchase_timestamp'].max()

# RFM 계산
rfm_df = df_orders_items.groupby('customer_id').agg({
    'order_purchase_timestamp': lambda x: (snapshot_date - x.max()).days,  # Recency
    'order_id': 'nunique',                                                 # Frequency
    'price': 'sum'                                                         # Monetary
}).reset_index()

# 컬럼 이름 변경
rfm_df.columns = ['customer_id', 'Recency', 'Frequency', 'Monetary']

# RFM 점수를 rank로 계산하여 수동으로 1-5 점수로 매핑
rfm_df['R'] = pd.qcut(rfm_df['Recency'].rank(method='first'), 5, labels=[5, 4, 3, 2, 1])
rfm_df['F'] = pd.qcut(rfm_df['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
rfm_df['M'] = pd.qcut(rfm_df['Monetary'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])

# 고객 세분화 함수 정의
def segment_customer(row):
    if row['R'] >= 4 and row['F'] >= 4 and row['M'] >= 4:
        return 'Royal'
    elif row['R'] >= 4 and row['F'] >= 4 and row['M'] >= 3:
        return 'Loyal'
    elif row['R'] >= 4 and row['F'] <= 2 and row['M'] <= 2:
        return 'New'
    elif row['M'] >= 4 and row['R'] >= 3 and row['F'] >= 3:
        return 'Big Spender'
    elif row['R'] <= 2 and row['F'] >= 4 and row['M'] >= 4:
        return 'At Risk'
    else:
        return 'Others'

# 고객 세분화 적용
rfm_df['Segment'] = rfm_df.apply(segment_customer, axis=1)

# 특정 seller_id와 연관된 고객만 필터링하기 위해, 고객과 판매자 데이터를 병합
rfm_df= rfm_df.merge(df_orders_items[['customer_id', 'seller_id']], on='customer_id', how='left').drop_duplicates()

# Using the API to bring the region to the data
r = requests.get('https://servicodados.ibge.gov.br/api/v1/localidades/mesorregioes')
content = [c['UF'] for c in json.loads(r.text)]
br_info = pd.DataFrame(content)
br_info['nome_regiao'] = br_info['regiao'].apply(lambda x: x['nome'])
br_info.drop('regiao', axis=1, inplace=True)
br_info.drop_duplicates(inplace=True)

# Filtering geolocations within Brazilian map boundaries
geo_prep = olist_geolocation[
    (olist_geolocation.geolocation_lat <= 5.27438888) &
    (olist_geolocation.geolocation_lng >= -73.98283055) &
    (olist_geolocation.geolocation_lat >= -33.75116944) &
    (olist_geolocation.geolocation_lng <= -34.79314722)
]

# 지오로케이션 데이터를 우편번호별로 평균값으로 그룹화 (수정된 부분)
geo_group = geo_prep.groupby('geolocation_zip_code_prefix', as_index=False)[['geolocation_lat', 'geolocation_lng']].mean()

# 판매자 위치 정보 추가
df_orders_items = df_orders_items.merge(geo_group, how='left', left_on='seller_zip_code_prefix',
                                        right_on='geolocation_zip_code_prefix')
df_orders_items.rename(columns={'geolocation_lat': 'seller_lat', 'geolocation_lng': 'seller_lng'}, inplace=True)

# 고객 위치 정보 추가
df_orders_items = df_orders_items.merge(geo_group, how='left', left_on='customer_zip_code_prefix',
                                        right_on='geolocation_zip_code_prefix')
df_orders_items.rename(columns={'geolocation_lat': 'customer_lat', 'geolocation_lng': 'customer_lng'}, inplace=True)

# Streamlit 앱 시작
st.set_page_config(
    page_title="E-commerce KPI Dashboard",
    page_icon="✅",
    layout="wide",
)

# 로그인 화면 구현
seller_id_input = st.text_input("판매자 ID를 입력하세요:")

if seller_id_input:
    # 입력된 seller_id가 데이터에 있는지 확인
    if seller_id_input in df_orders_items['seller_id'].values:
        # 해당 판매자의 데이터 필터링
        seller_data = df_orders_items[df_orders_items['seller_id'] == seller_id_input]

        # 해당 판매자의 RFM 분석 데이터 필터링
        seller_customers_rfm = rfm_df[rfm_df['seller_id'] == seller_id_input]
        
        # 레이아웃 구성: 3개의 열로 구성
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("RFM Analysis")
            with st.container():
                col_1,col_2,col_3 = st.columns(3)
                with col_1:
                    st.metric(label="Recency", value=f"{seller_customers_rfm['Recency'].mean()} days", delta="K 증가")
                with col_2:
                    st.metric(label="Frequency", value=f"{seller_customers_rfm['Frequency'].mean():.2f}", delta="-K 감소")
                with col_3:
                    st.metric(label="Monetary", value=f"${seller_customers_rfm['Monetary'].mean():,.2f}", delta="- K 감소")
                
                st.subheader("RFM 점수 계산 (1-5 점수제)")        
                st.dataframe(data=seller_customers_rfm, use_container_width=True, height=300, hide_index=True)
                
                st.write("Royal 고객: R, F, M 모두 상위 점수 (R ≥ 4, F ≥ 4, M ≥ 4), 의미: 최근에 자주 구매하며, 높은 구매 금액을 기록한 최우수 고객.")
                st.write("Loyal 고객: R과 F가 높고, M이 중간 이상 (R ≥ 4, F ≥ 4, M ≥ 3), 의미: 최근에 자주 구매하지만, Royal 고객에 비해 구매 금액이 상대적으로 낮은 충성 고객.")
                st.write("New 고객: R이 높고, F와 M이 낮음 (R ≥ 4, F ≤ 2, M ≤ 2), 의미: 최근에 구매했지만, 구매 빈도와 구매 금액이 낮아 아직 충성도가 형성되지 않은 신규 고객.")
                st.write("Big Spender 고객: M이 높고, R과 F는 중간 이상 (M ≥ 4, R ≥ 3, F ≥ 3), 의미: 구매 금액이 크지만, 구매 빈도나 최근 구매 활동이 중간 수준인 고액 구매 고객.")
                st.write("At Risk 고객: R이 낮고, F와 M이 높음 (R ≤ 2, F ≥ 4, M ≥ 4), 의미: 이전에는 자주 큰 금액을 구매했으나, 최근 활동이 감소한 이탈 위험 고객.")
                st.write("Others: 위 기준에 해당하지 않는 고객, 의미: 다른 세그먼트의 기준에 포함되지 않는 고객들로, 특정 특징이 없는 일반 고객.")
                
        # Column 2: 지도 또는 주요 데이터 시각화
        with col2:
            
            # 판매자 위치 추출
            seller_lat = seller_data['seller_lat'].dropna().unique()
            seller_lng = seller_data['seller_lng'].dropna().unique()

            if len(seller_lat) == 0 or len(seller_lng) == 0:
                st.write("판매자의 위치 정보가 없습니다.")
            else:
                seller_location = [seller_lat[0], seller_lng[0]]
                # 고객 위치들 추출
                customer_lats = seller_data['customer_lat'].dropna().values
                customer_lngs = seller_data['customer_lng'].dropna().values
                customer_locations = list(zip(customer_lats, customer_lngs))

                # 지도 생성
                map_center = [seller_lat[0], seller_lng[0]]
                map1 = folium.Map(location=map_center, zoom_start=5)

                # 판매자 마커 추가
                folium.Marker(location=seller_location, popup="판매자 위치", icon=folium.Icon(color='red')).add_to(map1)

                # 각 주문에 대해 판매자 -> 고객으로의 경로 표시 (애니메이션)
                for cust_lat, cust_lng in zip(customer_lats, customer_lngs):
                    customer_location = [cust_lat, cust_lng]
                    # 고객 마커 추가
                    folium.CircleMarker(location=customer_location, radius=2, color='blue', fill=True).add_to(map1)
                    # 애니메이션 경로 추가
                    AntPath(locations=[seller_location, customer_location],
                            color='green',
                            weight=1,
                            delay=1000,
                            dash_array=[10, 20]).add_to(map1)

                # Streamlit에서 지도 출력
                st.subheader("판매자의 판매 및 배송 경로 지도")
                st_folium(map1, width=700, height=500)
        with col3:
            st.subheader("판매자데이터 기반 위치분석")
            st.metric(label="판매 금액", value="23%", delta="3% 증가")
            st.write("AI Insite")   
                
    else:
        st.error("판매자 ID를 찾을 수 없습니다. 다시 확인해주세요.")