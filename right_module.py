import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.manifold import MDS
import plotly.graph_objects as go
import plotly.graph_objs as go
from scipy.interpolate import griddata

# 카테고리 분석 및 전처리 함수
def preprocess_category(df_orders_items):
    # NaN 값 제거
    df_orders_items = df_orders_items.dropna(subset=['product_category_name_english'])
    
    # 카테고리 벡터화 (TF-IDF)
    categories = df_orders_items['product_category_name_english'].unique()
    vectorizer = TfidfVectorizer()
    category_vectors = vectorizer.fit_transform(categories).toarray()

    # 카테고리별 평균 값 계산
    category_features = df_orders_items.groupby('product_category_name_english')[['price', 'freight_value']].mean().reset_index()

    # 스케일링
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(category_features.iloc[:, 1:])

    # 결합된 벡터 반환
    combined_vectors = np.hstack([category_vectors, scaled_features])
    
    return combined_vectors, category_features, vectorizer, scaler

# 셀러 분석 함수
def seller_analysis(df_orders_items, seller_id_input, vectorizer, scaler):
    # 특정 셀러의 데이터 추출
    seller_data = df_orders_items[df_orders_items['seller_id'] == seller_id_input]
    seller_categories = seller_data['product_category_name_english'].unique()
    seller_category_text = ' '.join(seller_categories)

    # 셀러의 TF-IDF 벡터 생성
    seller_vector = vectorizer.transform([seller_category_text]).toarray()

    # 셀러의 특성 평균 계산
    seller_features = seller_data[['price', 'freight_value']].mean().values

    # 스케일링
    seller_scaled_features = scaler.transform([seller_features])

    # 결합된 셀러 벡터 반환
    return np.hstack([seller_vector, seller_scaled_features]), seller_data

# 유사도 계산 및 차원 축소
def calculate_similarity(combined_vectors):
    similarity_matrix = cosine_similarity(combined_vectors)
    mds = MDS(n_components=2, dissimilarity="precomputed", random_state=0)
    return mds.fit_transform(1 - similarity_matrix)

# 3D 시각화 함수
def create_3d_contour_plot(coords_df, seller_point):
    # 좌표 데이터
    x = coords_df['x']
    y = coords_df['y']
    z = coords_df['z']

    # 그리드를 만들기 위한 보간 (griddata 사용)
    xi = np.linspace(min(x), max(x), 100)  # x에 대한 보간 그리드
    yi = np.linspace(min(y), max(y), 100)  # y에 대한 보간 그리드
    xi, yi = np.meshgrid(xi, yi)

    # 보간된 z값을 계산하여 그리드 형태로 변환
    zi = griddata((x, y), z, (xi, yi), method='cubic')

    fig = go.Figure()

    # 3D Surface 플롯 추가
    fig.add_trace(go.Surface(
        z=zi,  # 보간된 z 값
        x=xi,
        y=yi,
        colorscale='Viridis',
        opacity=0.8
    ))

    # 셀러 포인트 강조
    fig.add_trace(go.Scatter3d(
        x=seller_point['x'], y=seller_point['y'], z=seller_point['z'],
        mode='markers+text',
        marker=dict(size=10, color='red', symbol='circle'),
        text=['Seller'],
        textposition='top center'
    ))

    # 3D 레이아웃 설정 (격자선, 축 레이블, 숫자 제거)
    fig.update_layout(
        scene=dict(
            xaxis=dict(showgrid=False, zeroline=False, showbackground=False, showticklabels=False),  # X축 숫자 및 격자 제거
            yaxis=dict(showgrid=False, zeroline=False, showbackground=False, showticklabels=False),  # Y축 숫자 및 격자 제거
            zaxis=dict(showgrid=False, zeroline=False, showbackground=False, showticklabels=False),  # Z축 숫자 및 격자 제거
        ),
        margin=dict(l=0, r=0, b=0, t=30)
    )

    # HTML로 반환
    return fig.to_html(full_html=False)


# 전체 분석 및 요약
def display_summary(df_orders_items, seller_id_input):
    # 카테고리 분석
    combined_vectors, category_features, vectorizer, scaler = preprocess_category(df_orders_items)
    
    # 셀러 분석
    seller_combined_vector, seller_data = seller_analysis(df_orders_items, seller_id_input, vectorizer, scaler)

    # 셀러 벡터 결합
    combined_vectors_with_seller = np.vstack([combined_vectors, seller_combined_vector])

    # 유사도 계산 및 차원 축소
    category_coords_with_seller = calculate_similarity(combined_vectors_with_seller)

    # 좌표 데이터프레임 생성
    labels = list(category_features['product_category_name_english']) + ['Seller']
    coords_df = pd.DataFrame({
        'label': labels,
        'x': category_coords_with_seller[:, 0],
        'y': category_coords_with_seller[:, 1]
    })

    # 카테고리별 매출 계산
    category_sales = df_orders_items.groupby('product_category_name_english')['price'].sum().reset_index()
    category_sales.rename(columns={'price': 'z'}, inplace=True)

    # 셀러 매출 계산
    seller_sales = seller_data['price'].sum()
    seller_z = np.log1p(seller_sales)

    # z 값 추가
    z_values = list(np.log1p(category_sales['z'])) + [seller_z]
    coords_df['z'] = z_values

    # 셀러 위치 추출
    seller_point = coords_df[coords_df['label'] == 'Seller']

    # 3D 플롯 생성
    plot_html = create_3d_contour_plot(coords_df, seller_point)
    
    return plot_html