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

-- Sample data: Electronic products
INSERT INTO products (name, category, price, stock_quantity, reorder_level, last_restocked)
VALUES 
    ('iPhone 15 Pro', 'Smartphones', 999.99, 45, 15, CURRENT_TIMESTAMP),
    ('Samsung Galaxy S24', 'Smartphones', 899.99, 8, 20, CURRENT_TIMESTAMP),
    ('MacBook Pro 16"', 'Laptops', 2499.99, 12, 10, CURRENT_TIMESTAMP),
    ('Sony WH-1000XM5', 'Audio', 349.99, 5, 15, CURRENT_TIMESTAMP),
    ('iPad Air', 'Tablets', 599.99, 30, 12, CURRENT_TIMESTAMP);

