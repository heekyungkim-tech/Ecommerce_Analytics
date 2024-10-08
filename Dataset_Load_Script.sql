SHOW VARIABLES LIKE 'local_infile';
set global local_infile=true;

LOAD DATA LOCAL INFILE '/Users/heekyungkim/KPMG_Project/dataset/locations.csv'
INTO TABLE locations
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(Geolocation_zipcode_prefix, Geolocation_lat, Geolocation_lng, Geolocation_city, Geolocation_state);

LOAD DATA LOCAL INFILE '/Users/heekyungkim/KPMG_Project/dataset/sellers.csv'
INTO TABLE sellers
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(Seller_id, Seller_city, Seller_state, Seller_zipcode_prefix);

LOAD DATA LOCAL INFILE '/Users/heekyungkim/KPMG_Project/dataset/customers.csv'
INTO TABLE customer
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(Customer_id, Customer_unique_id, Customer_zipcode_prefix, Customer_city, Customer_state);


LOAD DATA LOCAL INFILE '/Users/heekyungkim/KPMG_Project/dataset/order_items.csv'
INTO TABLE order_item
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(Order_item_id, Price, Freight_value, Order_id, Product_id, Seller_id);

LOAD DATA LOCAL INFILE '/Users/heekyungkim/KPMG_Project/dataset/orders.csv'
INTO TABLE orders
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(Order_id, Customer_id, Order_status, Order_purchase_timestamp, Order_delivered_carrier_date, Order_delivered_customer_date, Order_estimated_delivery_date);

LOAD DATA LOCAL INFILE '/Users/heekyungkim/KPMG_Project/dataset/payments.csv'
INTO TABLE payment
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(Payment_id, Order_id, Payment_type, Payment_sequential, Payment_installments, Payment_value);

LOAD DATA LOCAL INFILE '/Users/heekyungkim/KPMG_Project/dataset/products.csv'
INTO TABLE product
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(Product_id, Product_category_name, Product_weight_g, Product_length_cm, Product_height_cm, Product_width_cm);

LOAD DATA LOCAL INFILE '/Users/heekyungkim/KPMG_Project/dataset/reviews.csv'
INTO TABLE reviews
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(Review_id, Order_id, Review_score, Review_creation_date, Review_answer_timestamp);



