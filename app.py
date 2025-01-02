from flask import Flask, render_template, request, session, redirect, url_for
from data_processing import load_data
from left_rfm_analytics import display_rfm_analysis, display_rfm_pie_chart, get_customers_by_segment, get_customer_strategies
from middle_visualization import display_map
from right_module import display_summary
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 실제 환경에서는 안전한 키를 사용하세요.

# CSV 데이터 로드
df_orders_items = load_data('./data/')

# seller_id와 login_id 매핑 로드
df_seller_login = pd.read_csv('./data/olist_sellers_id.csv')
seller_login_dict = dict(zip(df_seller_login['login_id'], df_seller_login['seller_id']))

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_id = request.form.get('login_id')

        if login_id in seller_login_dict:
            seller_id = seller_login_dict[login_id]
            session['seller_id'] = seller_id
            session['login_id'] = login_id
            return redirect(url_for('dashboard'))
        else:
            return "유효하지 않은 로그인 ID입니다."

    return render_template('login.html')

# 컨텍스트 프로세서 추가
@app.context_processor
def inject_user():
    return dict(
        seller_id=session.get('seller_id'),
        login_id=session.get('login_id')
    )

# 대시보드 페이지
@app.route('/dashboard', methods=['GET'])
def dashboard():
    seller_id = session.get('seller_id')
    login_id = session.get('login_id')

    if not seller_id:
        return redirect(url_for('login'))

    # 특정 판매자 데이터 필터링
    seller_data = df_orders_items[df_orders_items['seller_id'] == seller_id]

    if seller_data.empty:
        return f"판매자 ID {seller_id}에 대한 데이터가 없습니다."

    # RFM 분석
    rfm_hierarchy_chart = display_rfm_analysis(df_orders_items, seller_id)
    rfm_pie_chart = display_rfm_pie_chart(df_orders_items, seller_id)

    # 지도 생성
    seller_location, customer_locations = display_map(df_orders_items, seller_id)
    if not seller_location:
        return f"판매자 ID {seller_id}에 대한 위치 정보가 없습니다."
    
    # 추가 분석
    plot_html = display_summary(df_orders_items, seller_id)

    return render_template('dashboard.html',
                           rfm_hierarchy_chart=rfm_hierarchy_chart,
                           rfm_pie_chart=rfm_pie_chart,
                           seller_location=seller_location,
                           customer_locations=customer_locations,
                           plot_html=plot_html)

@app.route('/customer_analysis', methods=['GET'])
def customer_analysis():
    seller_id = session.get('seller_id')
    login_id = session.get('login_id')

    if not seller_id:
        return redirect(url_for('login'))

    # 등급별 고객 리스트 가져오기
    customers_by_segment = get_customers_by_segment(df_orders_items, seller_id)

    # 고객 등급별 추천 전략 가져오기
    customer_strategies = get_customer_strategies()

    # 선택된 등급 (GET 파라미터에서 가져옴)
    selected_segment = request.args.get('segment', list(customers_by_segment.keys())[0])

    # 선택된 등급의 고객 리스트
    selected_customers = customers_by_segment.get(selected_segment, pd.DataFrame())

    # 테이블로 표시하기 위해 딕셔너리로 변환
    selected_customers = selected_customers.to_dict('records')

    # 파이 차트 생성
    pie_chart_html = display_rfm_pie_chart(df_orders_items, seller_id)

    return render_template(
        'customer_analysis.html',
        customers_by_segment=customers_by_segment,
        selected_segment=selected_segment,
        selected_customers=selected_customers,
        customer_strategies=customer_strategies,
        pie_chart_html=pie_chart_html
    )

# 배송 분석 페이지
@app.route('/delivery_analysis', methods=['GET'])
def delivery_analysis():
    seller_id = session.get('seller_id')
    login_id = session.get('login_id')

    if not seller_id:
        return redirect(url_for('login'))

    # 필요한 분석 수행 (생략 가능)
    return render_template('delivery_analysis.html')

# 판매자 분석 페이지
@app.route('/seller_analysis', methods=['GET'])
def seller_analysis():
    seller_id = session.get('seller_id')
    login_id = session.get('login_id')

    if not seller_id:
        return redirect(url_for('login'))

    # 필요한 분석 수행 (생략 가능)
    return render_template('seller_analysis.html')

if __name__ == '__main__':
    app.run(debug=True)