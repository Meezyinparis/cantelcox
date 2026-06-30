CREATE DATABASE IF NOT EXISTS commerce_db;
USE commerce_db;

CREATE TABLE IF NOT EXISTS plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    monthly_price DECIMAL(10,2) NOT NULL,
    data_limit_gb INT,
    voice_minutes INT,
    sms_limit INT,
    active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS mobile_lines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    msisdn VARCHAR(20) NOT NULL UNIQUE,
    sim_number VARCHAR(50) NOT NULL UNIQUE,
    line_status VARCHAR(30) NOT NULL DEFAULT 'PENDING',
    plan_id INT,
    activated_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plan_id) REFERENCES plans(id)
);

CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    line_id INT NOT NULL,
    order_status VARCHAR(30) NOT NULL DEFAULT 'PENDING',
    idempotency_key VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (line_id) REFERENCES mobile_lines(id)
);

CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    plan_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES plans(id)
);

CREATE TABLE IF NOT EXISTS usage_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    line_id INT NOT NULL,
    voice_minutes_used INT DEFAULT 0,
    sms_used INT DEFAULT 0,
    data_used_gb DECIMAL(10,2) DEFAULT 0,
    usage_period VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (line_id) REFERENCES mobile_lines(id)
);

CREATE TABLE IF NOT EXISTS invoices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    line_id INT NOT NULL,
    billing_cycle VARCHAR(20) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    invoice_status VARCHAR(30) NOT NULL DEFAULT 'UNPAID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(customer_id, line_id, billing_cycle),
    FOREIGN KEY (line_id) REFERENCES mobile_lines(id)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id VARCHAR(100),
    actor_id VARCHAR(100),
    trace_id VARCHAR(100),
    payload JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO plans
(name, description, monthly_price, data_limit_gb, voice_minutes, sms_limit)
VALUES
('Basic 20', '20 Go', 35.00, 20, 500, 500),
('Unlimited', 'Illimité', 65.00, 9999, 9999, 9999);

INSERT INTO mobile_lines
(customer_id, msisdn, sim_number, line_status, plan_id, activated_at)
VALUES
(1, '5145550001', 'SIM000001', 'ACTIVE', 1, NOW()),
(2, '5145550002', 'SIM000002', 'ACTIVE', 2, NOW());

INSERT INTO orders
(customer_id, line_id, order_status, idempotency_key)
VALUES
(1, 1, 'COMPLETED', 'demo-order-001'),
(2, 2, 'PENDING', 'demo-order-002');

INSERT INTO order_items
(order_id, plan_id, quantity, unit_price)
VALUES
(1, 1, 1, 35.00),
(2, 2, 1, 65.00);

INSERT INTO usage_records
(line_id, voice_minutes_used, sms_used, data_used_gb, usage_period)
VALUES
(1, 120, 45, 8.60, '2026-06'),
(2, 540, 150, 25.40, '2026-06');

INSERT INTO invoices
(customer_id, line_id, billing_cycle, amount, invoice_status)
VALUES
(1, 1, '2026-06', 35.00, 'PAID'),
(2, 2, '2026-06', 65.00, 'UNPAID');