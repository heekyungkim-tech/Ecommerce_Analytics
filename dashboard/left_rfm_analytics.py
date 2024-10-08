#왼쪽 모듈. rfm기반 하이라키

import pandas as pd
import streamlit as st
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# RFM 분석 결과를 출력하는 함수
def display_rfm_analysis(df_orders_items, seller_id_input):
    snapshot_date = df_orders_items['order_purchase_timestamp'].max()

    # RFM 계산
    rfm_df = df_orders_items.groupby('customer_id').agg({
        'order_purchase_timestamp': lambda x: (snapshot_date - x.max()).days,
        'order_id': 'nunique',
        'price': 'sum'
    }).reset_index()

    rfm_df.columns = ['customer_id', 'Recency', 'Frequency', 'Monetary']

    rfm_df['R'] = pd.qcut(rfm_df['Recency'].rank(method='first'), 5, labels=[5, 4, 3, 2, 1])
    rfm_df['F'] = pd.qcut(rfm_df['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
    rfm_df['M'] = pd.qcut(rfm_df['Monetary'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])

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

    rfm_df['Segment'] = rfm_df.apply(segment_customer, axis=1)

    # 특정 seller_id와 연관된 고객만 필터링
    seller_customers_rfm = rfm_df[rfm_df['customer_id'].isin(df_orders_items[df_orders_items['seller_id'] == seller_id_input]['customer_id'])]

    # RFM 분석 결과 출력
    st.subheader("RFM Analysis")
    st.dataframe(seller_customers_rfm)
    
# RFM Analysis with K-means     
def display_rfm_analysis2(df_orders_items, seller_id_input):
    snapshot_date = df_orders_items['order_purchase_timestamp'].max()

    # RFM 계산 for customers associated with the given seller_id
    rfm_df = df_orders_items.groupby('customer_id').agg({
        'order_purchase_timestamp': lambda x: (snapshot_date - x.max()).days,
        'order_id': 'nunique',
        'price': 'sum'
    }).reset_index()

    rfm_df.columns = ['customer_id', 'Recency', 'Frequency', 'Monetary']

    # Normalize RFM data for clustering
    scaler = StandardScaler()
    rfm_normalized = scaler.fit_transform(rfm_df[['Recency', 'Frequency', 'Monetary']])

    # Apply K-means clustering
    kmeans = KMeans(n_clusters=4, random_state=42) # Adjust n_clusters as needed
    rfm_df['Cluster'] = kmeans.fit_predict(rfm_normalized)

    # Display clustering result with Plotly
    fig = px.scatter_3d(rfm_df, x='Recency', y='Frequency', z='Monetary', 
                        color='Cluster', title=f"K-means 고객 세분화 클러스터링",
                        labels={'Recency': 'Recency', 'Frequency': 'Frequency', 'Monetary': 'Monetary'})

    
    # 특정 seller_id와 연관된 고객만 필터링
    seller_customers_rfm = rfm_df[rfm_df['customer_id'].isin(df_orders_items[df_orders_items['seller_id'] == seller_id_input]['customer_id'])]

    # show the plot 
    st.plotly_chart(fig, use_container_width=True)

    # 클러스터별 고객 수 계산
    cluster_counts = seller_customers_rfm['Cluster'].value_counts().sort_index()
    
    # 클러스터별 고객 등급 정의
    cluster_labels = {
        0: "VIP",
        1: "프리미엄",
        2: "이탈위험",
        3: "일반",
        4: "신규"
    }
    
    # 데이터프레임에 고객등급 레이블링 칼럼 생성
    seller_customers_rfm['Customer_Rank'] = seller_customers_rfm['Cluster'].map(cluster_labels)
    
    with st.container():
        columns = st.columns(len(cluster_counts))  # 클러스터 수만큼 컬럼 생성
        for idx, (cluster, count) in enumerate(cluster_counts.items()):
            with columns[idx]:
                # 클러스터 번호에 따라 등급명을 label로 표시
                st.metric(label=cluster_labels.get(cluster, f"Cluster {cluster}"), value=f"{count}명")

    # Display cluster details in a table
    st.write("**고객별 RFM 정보 및 등급 분포도**")
    st.dataframe(seller_customers_rfm[['customer_id', 'Recency', 'Frequency', 'Monetary', 'Cluster','Customer_Rank']], use_container_width=True)
    