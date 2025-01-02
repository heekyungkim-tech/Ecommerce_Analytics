import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostRegressor
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt

# 판매량 집계 및 데이터 전처리 함수
def process_sales_data(data):
    # 월별 판매량 집계
    data['month_period'] = data['order_purchase_timestamp'].dt.to_period('M')
    monthly_sales = data.groupby(['seller_id', 'product_category_name', 'month_period', 'year', 'month'])['price'].sum().reset_index()
    monthly_sales.rename(columns={'price': 'monthly_sales'}, inplace=True)
    monthly_sales['previous_month_sales'] = monthly_sales.groupby(['seller_id', 'product_category_name'])['monthly_sales'].shift(1)
    monthly_sales = monthly_sales.dropna()

    # 판매량 기준으로 필터링 (1000 이상인 카테고리만 포함)
    category_sales_total = monthly_sales.groupby('product_category_name')['monthly_sales'].sum()
    major_categories = category_sales_total[category_sales_total >= 1000].index
    filtered_sales = monthly_sales[monthly_sales['product_category_name'].isin(major_categories)]

    # 데이터 정규화
    X = filtered_sales[['previous_month_sales', 'year', 'month']]
    y = filtered_sales['monthly_sales']
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 데이터 분할
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
    
    return X_train, X_test, y_train, y_test, filtered_sales

# 모델 학습 및 예측 함수
def train_and_predict(X_train, X_test, y_train, y_test):
    # 각 모델 정의 및 학습
    xgb_model = xgb.XGBRegressor(objective='reg:squarederror', learning_rate=0.1, max_depth=3, n_estimators=200, random_state=42)
    xgb_model.fit(X_train, y_train)
    y_pred_xgb = xgb_model.predict(X_test)

    lgb_model = lgb.LGBMRegressor(objective='regression', learning_rate=0.1, max_depth=3, n_estimators=200, random_state=42)
    lgb_model.fit(X_train, y_train)
    y_pred_lgb = lgb_model.predict(X_test)

    catboost_model = CatBoostRegressor(learning_rate=0.1, depth=3, iterations=200, random_state=42, verbose=0)
    catboost_model.fit(X_train, y_train)
    y_pred_catboost = catboost_model.predict(X_test)

    # DNN 모델 정의 및 학습
    dnn_model = Sequential([
        Dense(64, input_shape=(X_train.shape[1],), activation='relu'),
        Dropout(0.3),
        Dense(32, activation='relu'),
        Dropout(0.3),
        Dense(1)
    ])
    dnn_model.compile(optimizer=Adam(learning_rate=0.01), loss='mse')
    dnn_model.fit(X_train, y_train, epochs=50, batch_size=32, verbose=1)
    y_pred_dnn = dnn_model.predict(X_test).flatten()

    # 앙상블 예측
    y_pred_ensemble = (y_pred_xgb + y_pred_lgb + y_pred_catboost + y_pred_dnn) / 4
    rmse_ensemble = np.sqrt(mean_squared_error(y_test, y_pred_ensemble))
    
    return y_pred_ensemble, rmse_ensemble

# 예측 summary 출력 함수
def display_sales_summary(filtered_sales, y_pred_ensemble, rmse_ensemble, seller_id):
    # seller_id에 해당하는 데이터 필터링
    filtered_sales_seller = filtered_sales[filtered_sales['seller_id'] == seller_id]
    if filtered_sales_seller.empty:
        return f"No data available for seller_id: {seller_id}"
    
    # 예측 및 시각화 데이터 준비
    predicted_sales_by_category = filtered_sales_seller.groupby('product_category_name')['monthly_sales'].sum().reset_index()
    predicted_sales_by_category.columns = ['Product Category', 'Predicted Sales (USD)']
    predicted_sales_by_category = predicted_sales_by_category.sort_values(by='Predicted Sales (USD)', ascending=False)
    predicted_sales_by_category['Sales Ratio'] = predicted_sales_by_category['Predicted Sales (USD)'] / predicted_sales_by_category['Predicted Sales (USD)'].sum()
    total_predicted_sales = predicted_sales_by_category['Predicted Sales (USD)'].sum()

    # 시각화 (상위 10개 카테고리 + 기타)
    top_categories = predicted_sales_by_category.head(10)
    other_sales = predicted_sales_by_category['Predicted Sales (USD)'].iloc[10:].sum()
    other_row = pd.DataFrame({'Product Category': ['Other'], 'Predicted Sales (USD)': [other_sales], 'Sales Ratio': [other_sales / predicted_sales_by_category['Predicted Sales (USD)'].sum()]})
    top_categories = pd.concat([top_categories, other_row], ignore_index=True)

    # 결과를 플롯 대신 텍스트 형태로 반환
    summary = f"Total Predicted Sales: ${total_predicted_sales:.2f} | Ensemble RMSE: {rmse_ensemble:.2f} USD\n"
    for index, row in top_categories.iterrows():
        summary += f"{row['Product Category']}: ${row['Predicted Sales (USD)']:.2f} ({row['Sales Ratio']*100:.1f}%)\n"

    return summary