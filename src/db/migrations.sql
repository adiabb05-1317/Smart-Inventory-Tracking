-- Create products table for inventory tracking
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    reorder_level INTEGER NOT NULL DEFAULT 10 CHECK (reorder_level >= 0),
    last_restocked TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_stock_quantity ON products(stock_quantity);

-- Add new columns to products table
ALTER TABLE products ADD COLUMN IF NOT EXISTS supplier VARCHAR(100);
ALTER TABLE products ADD COLUMN IF NOT EXISTS warranty_months INTEGER DEFAULT 12;

-- Create additional indexes for filtering and sorting
CREATE INDEX IF NOT EXISTS idx_products_price ON products(price);

-- Sample data: Electronic products
INSERT INTO products (name, category, price, stock_quantity, reorder_level, last_restocked, supplier, warranty_months)
VALUES 
    ('iPhone 15 Pro', 'Smartphones', 999.99, 45, 15, CURRENT_TIMESTAMP, 'Apple Inc.', 12),
    ('Samsung Galaxy S24', 'Smartphones', 899.99, 8, 20, CURRENT_TIMESTAMP, 'Samsung Electronics', 24),
    ('MacBook Pro 16"', 'Laptops', 2499.99, 12, 10, CURRENT_TIMESTAMP, 'Apple Inc.', 12),
    ('Sony WH-1000XM5', 'Audio', 349.99, 5, 15, CURRENT_TIMESTAMP, 'Sony Corporation', 24),
    ('iPad Air', 'Tablets', 599.99, 30, 12, CURRENT_TIMESTAMP, 'Apple Inc.', 12);

-- Create sales_history table for tracking sales transactions
CREATE TABLE IF NOT EXISTS sales_history (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    quantity_sold INTEGER NOT NULL CHECK (quantity_sold > 0),
    sale_price DECIMAL(10, 2) NOT NULL,
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for sales_history performance
CREATE INDEX IF NOT EXISTS idx_sales_product_id ON sales_history(product_id);
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales_history(sale_date);

-- Add sample sales data for last 30 days with realistic patterns
INSERT INTO sales_history (product_id, quantity_sold, sale_price, sale_date) VALUES
    -- iPhone 15 Pro sales (product_id: 1) - high demand
    (1, 5, 999.99, CURRENT_TIMESTAMP - INTERVAL '1 day'),
    (1, 3, 999.99, CURRENT_TIMESTAMP - INTERVAL '2 days'),
    (1, 7, 999.99, CURRENT_TIMESTAMP - INTERVAL '4 days'),
    (1, 4, 999.99, CURRENT_TIMESTAMP - INTERVAL '6 days'),
    (1, 6, 999.99, CURRENT_TIMESTAMP - INTERVAL '8 days'),
    (1, 2, 999.99, CURRENT_TIMESTAMP - INTERVAL '10 days'),
    (1, 5, 999.99, CURRENT_TIMESTAMP - INTERVAL '15 days'),
    (1, 8, 999.99, CURRENT_TIMESTAMP - INTERVAL '20 days'),
    (1, 3, 999.99, CURRENT_TIMESTAMP - INTERVAL '25 days'),
    
    -- Samsung Galaxy S24 sales (product_id: 2) - very high recent demand
    (2, 10, 899.99, CURRENT_TIMESTAMP - INTERVAL '1 day'),
    (2, 8, 899.99, CURRENT_TIMESTAMP - INTERVAL '3 days'),
    (2, 12, 899.99, CURRENT_TIMESTAMP - INTERVAL '5 days'),
    (2, 6, 899.99, CURRENT_TIMESTAMP - INTERVAL '7 days'),
    (2, 9, 899.99, CURRENT_TIMESTAMP - INTERVAL '12 days'),
    (2, 7, 899.99, CURRENT_TIMESTAMP - INTERVAL '18 days'),
    (2, 11, 899.99, CURRENT_TIMESTAMP - INTERVAL '22 days'),
    (2, 5, 899.99, CURRENT_TIMESTAMP - INTERVAL '28 days'),
    
    -- MacBook Pro sales (product_id: 3) - steady demand
    (3, 2, 2499.99, CURRENT_TIMESTAMP - INTERVAL '2 days'),
    (3, 1, 2499.99, CURRENT_TIMESTAMP - INTERVAL '5 days'),
    (3, 3, 2499.99, CURRENT_TIMESTAMP - INTERVAL '9 days'),
    (3, 2, 2499.99, CURRENT_TIMESTAMP - INTERVAL '14 days'),
    (3, 1, 2499.99, CURRENT_TIMESTAMP - INTERVAL '19 days'),
    (3, 2, 2499.99, CURRENT_TIMESTAMP - INTERVAL '24 days'),
    (3, 1, 2499.99, CURRENT_TIMESTAMP - INTERVAL '29 days'),
    
    -- Sony WH-1000XM5 sales (product_id: 4) - moderate demand
    (4, 4, 349.99, CURRENT_TIMESTAMP - INTERVAL '1 day'),
    (4, 3, 349.99, CURRENT_TIMESTAMP - INTERVAL '4 days'),
    (4, 5, 349.99, CURRENT_TIMESTAMP - INTERVAL '8 days'),
    (4, 2, 349.99, CURRENT_TIMESTAMP - INTERVAL '13 days'),
    (4, 4, 349.99, CURRENT_TIMESTAMP - INTERVAL '17 days'),
    (4, 3, 349.99, CURRENT_TIMESTAMP - INTERVAL '23 days'),
    (4, 6, 349.99, CURRENT_TIMESTAMP - INTERVAL '27 days'),
    
    -- iPad Air sales (product_id: 5) - low to moderate demand
    (5, 2, 599.99, CURRENT_TIMESTAMP - INTERVAL '3 days'),
    (5, 3, 599.99, CURRENT_TIMESTAMP - INTERVAL '7 days'),
    (5, 1, 599.99, CURRENT_TIMESTAMP - INTERVAL '11 days'),
    (5, 2, 599.99, CURRENT_TIMESTAMP - INTERVAL '16 days'),
    (5, 4, 599.99, CURRENT_TIMESTAMP - INTERVAL '21 days'),
    (5, 1, 599.99, CURRENT_TIMESTAMP - INTERVAL '26 days');

