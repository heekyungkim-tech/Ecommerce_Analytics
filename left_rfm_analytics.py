import pandas as pd
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from data_processing import calculate_rfm

# 클러스터 이름 매핑 (0: VIP, 1: 프리미엄, 2: 이탈위험, 3: 일반, 4: 신규)
cluster_labels = {0: 'VIP', 1: '프리미엄', 2: '이탈위험', 3: '일반', 4: '신규'}

# RFM 분석을 수행하고 K-means 클러스터링을 적용하는 함수
def display_rfm_analysis(df_orders_items, seller_id):
    # 전체 고객 기준 RFM 계산
    rfm_df = calculate_rfm(df_orders_items)

    # K-means를 사용하여 클러스터링 수행
    scaler = StandardScaler()
    rfm_normalized = scaler.fit_transform(rfm_df[['Recency', 'Frequency', 'Monetary']])

    # 클러스터 수 5개로 설정
    kmeans = KMeans(n_clusters=5, random_state=42)
    rfm_df['Cluster'] = kmeans.fit_predict(rfm_normalized)

    # 클러스터 이름 매핑
    rfm_df['Cluster_Label'] = rfm_df['Cluster'].map(cluster_labels)

    # 특정 seller_id에 해당하는 고객 필터링
    seller_customers_rfm = rfm_df[rfm_df['customer_id'].isin(df_orders_items[df_orders_items['seller_id'] == seller_id]['customer_id'])]

    # 전체 고객 수와 해당 seller의 고객 수
    total_customers = len(rfm_df)
    seller_customers = len(seller_customers_rfm)

    # 각 클러스터별 전체 고객 수 계산
    cluster_counts = rfm_df['Cluster_Label'].value_counts().sort_index()

    # 각 클러스터에서 특정 seller의 고객 수 계산
    seller_cluster_counts = seller_customers_rfm['Cluster_Label'].value_counts().sort_index()

    # 전체 클러스터에서 seller가 차지하는 비율 계산
    cluster_ratios = seller_cluster_counts / cluster_counts

    # 기본 계층형 삼각형 구조 생성
    fig = go.Figure()

    # 클러스터 계층 추가
    fig.add_trace(go.Funnel(
        y=cluster_counts.index,
        x=cluster_counts.values,
        textinfo="value+percent total",
        marker={"color": ['royalblue', 'orange', 'green', 'red', 'lightgrey']}
    ))

    # 특정 seller 고객 비율 강조 (상대적인 포션으로 표현)
    fig.add_trace(go.Funnel(
        y=cluster_ratios.index,
        x=(cluster_ratios.values * cluster_counts.values),
        textinfo="value+percent total",
        marker={"color": ['blue', 'darkorange', 'darkgreen', 'darkred', 'darkgrey']}
    ))

    # HTML로 반환
    return fig.to_html(full_html=False)

# RFM 분석을 수행하고 파이 차트로 시각화하는 함수
def display_rfm_pie_chart(df_orders_items, seller_id):
    # 전체 고객 기준 RFM 계산
    rfm_df = calculate_rfm(df_orders_items)

    # K-means를 사용하여 클러스터링 수행
    scaler = StandardScaler()
    rfm_normalized = scaler.fit_transform(rfm_df[['Recency', 'Frequency', 'Monetary']])

    # 클러스터 수 5개로 설정
    kmeans = KMeans(n_clusters=5, random_state=42)
    rfm_df['Cluster'] = kmeans.fit_predict(rfm_normalized)

    # 클러스터 이름 매핑
    rfm_df['Cluster_Label'] = rfm_df['Cluster'].map(cluster_labels)

    # 특정 seller_id에 해당하는 주문 데이터 필터링
    seller_orders = df_orders_items[df_orders_items['seller_id'] == seller_id]

    # 해당 판매자의 고객 ID 목록
    seller_customer_ids = seller_orders['customer_id'].unique()

    # 해당 판매자의 고객들에 대한 RFM 데이터 필터링
    seller_customers_rfm = rfm_df[rfm_df['customer_id'].isin(seller_customer_ids)]

    # 각 클러스터별 고객 수 계산
    cluster_counts = seller_customers_rfm['Cluster_Label'].value_counts().sort_index()

    # 파이 차트 생성
    labels = cluster_counts.index
    values = cluster_counts.values

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.4)])
    fig.update_traces(textinfo='percent+label')

    # 레이아웃 업데이트 (옵션)
    fig.update_layout(title_text='클러스터별 고객 분포')

    # HTML로 반환
    return fig.to_html(full_html=False)

# 등급별 고객 리스트를 반환하는 함수
def get_customers_by_segment(df_orders_items, seller_id):
    # 전체 고객 기준 RFM 계산
    rfm_df = calculate_rfm(df_orders_items)

    # K-means를 사용하여 클러스터링 수행
    scaler = StandardScaler()
    rfm_normalized = scaler.fit_transform(rfm_df[['Recency', 'Frequency', 'Monetary']])

    # 클러스터 수 5개로 설정
    kmeans = KMeans(n_clusters=5, random_state=42)
    rfm_df['Cluster'] = kmeans.fit_predict(rfm_normalized)

    # 클러스터 이름 매핑 (0: VIP, 1: 프리미엄, 2: 이탈위험, 3: 일반, 4: 신규)
    rfm_df['Segment'] = rfm_df['Cluster'].map(cluster_labels)

    # 특정 seller_id에 해당하는 주문 데이터 필터링
    seller_orders = df_orders_items[df_orders_items['seller_id'] == seller_id]

    # 해당 판매자의 고객 ID 목록
    seller_customer_ids = seller_orders['customer_id'].unique()

    # 해당 판매자의 고객들에 대한 RFM 데이터 필터링
    seller_customers_rfm = rfm_df[rfm_df['customer_id'].isin(seller_customer_ids)]

    # 등급별로 고객 리스트를 딕셔너리로 반환
    segments = seller_customers_rfm['Segment'].unique()
    customers_by_segment = {}
    for segment in segments:
        customers_in_segment = seller_customers_rfm[seller_customers_rfm['Segment'] == segment]
        customers_by_segment[segment] = customers_in_segment

    return customers_by_segment

# 클러스터별 추천 전략을 반환하는 함수
def get_customer_strategies():
    customer_strategies = {
        'VIP': [
            "VIP 전용 혜택 제공 및 독점 상품 제안",
            "맞춤형 리워드 프로그램 강화",
            "개인 맞춤형 추천 상품 제공"
        ],
        '프리미엄': [
            "충성 고객 혜택 제공",
            "정기적인 감사 이벤트 초대",
            "추천 상품 및 서비스 업셀링"
        ],
        '이탈위험': [
            "고가 상품 추천",
            "프리미엄 멤버십 제공",
            "특별 이벤트 초대"
        ],
        '일반': [
            "재참여 유도 메시지 전송",
            "할인 쿠폰 제공",
            "맞춤형 재참여 캠페인"
        ],
        '신규': [
            "일반 마케팅 캠페인 참여 유도",
            "포인트 적립 제공",
            "구매 빈도 증가를 위한 프로모션"
        ]
    }
    return customer_strategies