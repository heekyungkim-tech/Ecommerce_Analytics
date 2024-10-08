#왼쪽 모듈. rfm기반 하이라키

import pandas as pd
import streamlit as st

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