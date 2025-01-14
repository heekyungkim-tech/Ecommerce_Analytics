import pandas as pd

# CSV 데이터를 로드하는 함수
def load_data(raw_path):
    olist_customer = pd.read_csv(raw_path + 'olist_customers_dataset.csv')
    olist_geolocation = pd.read_csv(raw_path + 'olist_geolocation_dataset.csv')
    olist_orders = pd.read_csv(raw_path + 'olist_orders_dataset.csv')
    olist_order_items = pd.read_csv(raw_path + 'olist_order_items_dataset.csv')
    olist_sellers = pd.read_csv(raw_path + 'olist_sellers_dataset.csv')
    olist_products = pd.read_csv(raw_path + 'olist_products_dataset.csv')
    product_category_translation = pd.read_csv(raw_path + 'product_category_name_translation.csv')
    olist_reviews = pd.read_csv(raw_path + 'olist_order_reviews_dataset.csv')

    # 데이터 병합
    df_orders = olist_orders.merge(olist_customer, how='left', on='customer_id')
    df_order_items = olist_order_items.merge(olist_sellers, how='left', on='seller_id')
    df_orders_items = df_orders.merge(df_order_items, how='left', on='order_id')
    
    # 제품 관련 정보 병합 (product_id 기준)
    olist_products = olist_products.merge(product_category_translation, how='left', on='product_category_name')
    df_orders_items = df_orders_items.merge(olist_products[['product_id', 'product_category_name_english']], how='left', on='product_id')
    
    # 날짜 타입 변환
    timestamp_cols = ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_estimated_delivery_date']
    for col in timestamp_cols:
        df_orders_items[col] = pd.to_datetime(df_orders_items[col])

    # 지리 정보 병합 (seller, customer 위치)
    geo_group = olist_geolocation.groupby('geolocation_zip_code_prefix', as_index=False)[['geolocation_lat', 'geolocation_lng']].mean()
    df_orders_items = df_orders_items.merge(geo_group, how='left', left_on='seller_zip_code_prefix', right_on='geolocation_zip_code_prefix')
    df_orders_items.rename(columns={'geolocation_lat': 'seller_lat', 'geolocation_lng': 'seller_lng'}, inplace=True)
    df_orders_items = df_orders_items.merge(geo_group, how='left', left_on='customer_zip_code_prefix', right_on='geolocation_zip_code_prefix')
    df_orders_items.rename(columns={'geolocation_lat': 'customer_lat', 'geolocation_lng': 'customer_lng'}, inplace=True)

    # 연도, 월 추출
    df_orders_items['order_purchase_year'] = df_orders_items['order_purchase_timestamp'].dt.year
    df_orders_items['order_purchase_month'] = df_orders_items['order_purchase_timestamp'].dt.month
    df_orders_items['order_purchase_year_month'] = df_orders_items['order_purchase_timestamp'].dt.strftime('%Y%m')

    return df_orders_items

# RFM 분석을 위한 함수
def calculate_rfm(df_orders_items):
    snapshot_date = df_orders_items['order_purchase_timestamp'].max()

    rfm_df = df_orders_items.groupby('customer_id').agg({
        'order_purchase_timestamp': lambda x: (snapshot_date - x.max()).days,  # Recency
        'order_id': 'nunique',  # Frequency
        'price': 'sum'  # Monetary
    }).reset_index()

    rfm_df.columns = ['customer_id', 'Recency', 'Frequency', 'Monetary']

    # RFM 점수 계산
    rfm_df['R'] = pd.qcut(rfm_df['Recency'].rank(method='first'), 5, labels=[5, 4, 3, 2, 1])
    rfm_df['F'] = pd.qcut(rfm_df['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
    rfm_df['M'] = pd.qcut(rfm_df['Monetary'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])

    return rfm_df

# 고객 세그먼트를 구분하는 함수
def segment_customer(rfm_df):
    def segment(row):
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

    rfm_df['Segment'] = rfm_df.apply(segment, axis=1)
    return rfm_df