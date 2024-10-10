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
    #st.plotly_chart(fig, use_container_width=True)

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
    
    # 고객 등급별 특성 정보
    cluster_characteristics = {
        "VIP": "최근 자주 구매, 높은 금액 소비",
        "프리미엄": "구매 빈도는 낮지만 고가 구매",
        "이탈위험": "최근 구매 이력 없음, 낮은 구매 빈도",
        "일반": "중간 정도의 구매 빈도와 소비액",
        "신규": "최근 구매 시작, 낮은 빈도 및 소비 금액"
    }
    
    # 데이터프레임에 고객등급 레이블링 칼럼 생성
    seller_customers_rfm['Customer_Rank'] = seller_customers_rfm['Cluster'].map(cluster_labels)
    
    # 클러스터별 고객 등급 분포 데이터 생성
    distribution_df = pd.DataFrame({
        "Customer_Rank": cluster_counts.index.map(cluster_labels),
        "Count": cluster_counts.values,
        "Characteristics": cluster_counts.index.map(lambda x: cluster_characteristics[cluster_labels[x]])
    })

    # 파이 차트 생성 (hover_data에 Characteristics 추가)
    fig = px.pie(distribution_df, values='Count', names='Customer_Rank', 
                title="고객 등급별 분포", color_discrete_sequence=px.colors.qualitative.Set3,
                hover_data={'Characteristics': True})

    # Streamlit에서 파이 차트 표시
    st.plotly_chart(fig, use_container_width=True)

    # 고객 등급별 분포 표시
    with st.container():
        columns = st.columns(len(cluster_counts))  # 클러스터 수만큼 컬럼 생성
        for idx, (cluster, count) in enumerate(cluster_counts.items()):
            with columns[idx]:
                # 클러스터 번호에 따라 등급명을 label로 표시
                st.metric(label=cluster_labels.get(cluster, f"Cluster {cluster}"), value=f"{count}명")

    # 고객 등급에 따른 추천 전략 데이터
    customer_strategies = {
        "VIP 고객": {
            "추천 전략": ["VIP 전용 혜택 제공", "리워드 프로그램 강화", "맞춤형 추천 상품 제공"]
        },
        "프리미엄 고객": {
            "추천 전략": ["고가 상품 추천", "특별 이벤트 및 혜택 제공", "추가 구매 유도 캠페인"]
        },
        "이탈위험 고객": {
            "추천 전략": ["리마인드 마케팅", "특별 할인 및 재참여 프로모션", "맞춤형 캠페인 제공"]
        },
        "일반 고객": {
            "추천 전략": ["정기적인 마케팅 캠페인 참여", "적당한 보상 프로그램", "구매 빈도 증가 유도"]
        },
        "신규 고객": {
            "추천 전략": ["초기 리텐션 강화", "신규 고객 혜택 제공", "맞춤형 추천 상품 제안"]
        }
    }

    # 고객 등급 선택
    selected_rank = st.selectbox("고객 등급:", list(customer_strategies.keys()))

    # 선택된 고객 등급의 추천 전략을 리스트로 표시
    if selected_rank != "선택하세요":
        st.write(f"**{selected_rank}의 추천 전략**")
        strategies = customer_strategies[selected_rank]["추천 전략"]
        for strategy in strategies:
            st.write(f"- {strategy}")

    # Display cluster details in a table
    st.write("**고객별 RFM 정보 및 등급 분포도**")
    st.dataframe(seller_customers_rfm[['customer_id', 'Recency', 'Frequency', 'Monetary', 'Cluster','Customer_Rank']], use_container_width=True)
    