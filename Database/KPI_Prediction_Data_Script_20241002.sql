CREATE TABLE customer (
    Customer_id VARCHAR(255) PRIMARY KEY,   -- 고객 고유 ID, 기본 키로 설정
    Customer_unique_id VARCHAR(255) NOT NULL,  -- 유니크한 ID
    Customer_zipcode_prefix INT NOT NULL,   -- 우편번호 접두어
    Customer_city VARCHAR(255) NOT NULL,    -- 고객 도시
    Customer_state VARCHAR(255) NOT NULL    -- 고객 주
);

CREATE TABLE sellers (
    Seller_id VARCHAR(255) NOT NULL PRIMARY KEY,
    Seller_city VARCHAR(255),
    Seller_state VARCHAR(255),
    Seller_zipcode_prefix INT
);

CREATE TABLE locations (
    Geolocation_zipcode_prefix INT NOT NULL PRIMARY KEY,
    Geolocation_lat FLOAT NOT NULL,
    Geolocation_lng FLOAT NOT NULL,
    Geolocation_city VARCHAR(255),
    Geolocation_state VARCHAR(255)
);

CREATE TABLE orders (
    Order_id VARCHAR(255) PRIMARY KEY,          -- 주문 ID, 기본 키로 설정
    Customer_id VARCHAR(255),                   -- 고객 ID (customer 테이블과 연결됨)
    Order_status VARCHAR(255) NOT NULL,         -- 주문 상태
    Order_purchase_timestamp VARCHAR(255) NOT NULL,  -- 주문 시간
    Order_delivered_carrier_date VARCHAR(255),  -- 운송사가 배송 완료한 날짜
    Order_delivered_customer_date VARCHAR(255), -- 고객에게 배송된 날짜
    Order_estimated_delivery_date VARCHAR(255), -- 예상 배송 날짜
    FOREIGN KEY (Customer_id) REFERENCES customer(Customer_id)  -- 외래 키, customer 테이블과 연결
);

CREATE TABLE payment (
    Payment_id INT AUTO_INCREMENT PRIMARY KEY,  -- 자동 증가하는 결제 ID (기본 키)
    Order_id VARCHAR(255) NOT NULL,             -- 주문 ID (orders 테이블과 연결됨)
    Payment_type VARCHAR(255) NOT NULL,         -- 결제 타입 (예: 카드, 현금)
    Payment_sequential INT NOT NULL,            -- 결제 순서 (분할 결제 시 순서)
    Payment_installments INT NOT NULL,          -- 할부 수
    Payment_value DECIMAL(10, 2) NOT NULL,      -- 결제 금액
    FOREIGN KEY (Order_id) REFERENCES orders(Order_id) -- 외래 키, orders 테이블과 연결
);

CREATE TABLE product (
    Product_id VARCHAR(255) PRIMARY KEY,        -- 제품 ID (기본 키)
    Product_category_name VARCHAR(255) NOT NULL, -- 제품 카테고리명
    Product_weight_g DECIMAL(10, 2),            -- 제품 무게 (그램 단위)
    Product_length_cm DECIMAL(10, 2),           -- 제품 길이 (센티미터 단위)
    Product_height_cm DECIMAL(10, 2),           -- 제품 높이 (센티미터 단위)
    Product_width_cm DECIMAL(10, 2)             -- 제품 너비 (센티미터 단위)
);

CREATE TABLE reviews (
    Review_id VARCHAR(255) PRIMARY KEY,         -- 리뷰 ID (기본 키)
    Order_id VARCHAR(255) NOT NULL,             -- 주문 ID (orders 테이블과 연결됨)
    Review_score INT NOT NULL,                  -- 리뷰 점수 (예: 1~5점)
    Review_creation_date DATETIME NOT NULL,     -- 리뷰 생성 날짜
    Review_answer_timestamp DATETIME,           -- 리뷰 답변 시간
    FOREIGN KEY (Order_id) REFERENCES orders(Order_id) -- 외래 키, orders 테이블과 연결
);

CREATE TABLE order_item (
    Order_item_id INT NOT NULL PRIMARY KEY,
    Price FLOAT NOT NULL,
    Freight_value FLOAT NOT NULL,
    Order_id VARCHAR(255) NOT NULL,
    Product_id VARCHAR(255) NOT NULL,
    Seller_id VARCHAR(255) NOT NULL,
    
    -- Foreign Key constraints
    FOREIGN KEY (Order_id) REFERENCES orders(Order_id),
    FOREIGN KEY (Product_id) REFERENCES product(Product_id),
    FOREIGN KEY (Seller_id) REFERENCES sellers(Seller_id)
);

-- Geolocation_zipcode_prefix와 외래 키로 연결
ALTER TABLE customer
ADD CONSTRAINT fk_customer_zipcode
FOREIGN KEY (Customer_zipcode_prefix)
REFERENCES locations(Geolocation_zipcode_prefix);

ALTER TABLE sellers
ADD CONSTRAINT fk_seller_zipcode
FOREIGN KEY (Seller_zipcode_prefix)
REFERENCES locations(Geolocation_zipcode_prefix);





