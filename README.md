# Smart Inventory Tracking API

A FastAPI-based inventory management system for electronic stores with PostgreSQL database and connection pooling.

## Features

### Core Features
- Complete CRUD operations for product management
- Low stock monitoring and alerts
- Product restocking functionality
- Connection pooling for optimal database performance
- Swagger UI documentation
- CORS enabled for cross-origin requests

### Advanced Features
- **Sales Analytics**: Track sales trends, revenue, and top performers
- **Demand Forecasting**: Predict stockouts using 7-day moving average
- **Inventory Turnover Analysis**: Identify slow-moving products
- **Restock Urgency Scoring**: Prioritize restocking based on demand patterns
- **Bulk Operations**: Upload and restock multiple products at once
- **Sales Transaction Recording**: Track sales history with stock validation
- **Advanced Filtering**: Filter products by category, price range, and stock status
- **In-Memory Caching**: 5-minute cache for analytics endpoints
- **Business Logic Layer**: Separate service layer for maintainability
- **Unit Testing**: Comprehensive pytest test suite

## Prerequisites

- Python 3.10+
- Docker and Docker Compose
- [uv](https://github.com/astral-sh/uv) package manager
- PostgreSQL client (optional, for direct database access)

## Project Structure

```
Smart-Inventory-Tracking/
├── main.py                      # FastAPI application entry point
├── src/
│   ├── db/
│   │   ├── db_manager.py       # Database manager with connection pooling
│   │   └── migrations.sql      # Database schema and sample data
│   └── routers/
│       └── products.py          # Products API endpoints
├── docker-compose.yml           # PostgreSQL container configuration
├── pyproject.toml              # Project dependencies
└── README.md                   # This file
```

## Setup Instructions

### 1. Configure Environment Variables

Copy the example environment file and customize as needed:

```bash
cp .env.example .env
```

Edit `.env` with your preferred configuration:

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=inventory_db
DB_USER=kubo_user
DB_PASSWORD=password
DB_MIN_CONNECTIONS=2
DB_MAX_CONNECTIONS=10

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# Cache Configuration (TTL in seconds)
CACHE_TTL_SECONDS=300

# CORS Configuration (comma-separated origins, or * for all)
CORS_ALLOW_ORIGINS=*
```

**Note:** The `.env` file is git-ignored for security. Never commit credentials to version control.

### 2. Start PostgreSQL Database

```bash
docker-compose up -d
```

This will start a PostgreSQL container with:
- Username: `kubo_user` (default, customizable via `DB_USER` in `.env`)
- Password: `password` (default, customizable via `DB_PASSWORD` in `.env`)
- Database: `inventory_db` (default, customizable via `DB_NAME` in `.env`)
- Port: `5432`

**Note:** The default credentials work for everyone running this project locally. Docker Compose creates an isolated containerized PostgreSQL instance, so these credentials are not tied to your system's PostgreSQL installation (if any). Users can customize these values by setting `DB_USER`, `DB_PASSWORD`, and `DB_NAME` in their `.env` file before running `docker-compose up`.

### 3. Run Database Migrations

Option 1 - Using the provided script:

```bash
./run_migrations.sh
```

Option 2 - Manual execution:

```bash
docker exec -i inventory_db psql -U kubo_user -d inventory_db < src/db/migrations.sql
```

### 4. Install Dependencies

Using uv package manager:

```bash
uv pip install -e .
```

Or using pip:

```bash
pip install -e .
```

### 5. Run the Application

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

## API Documentation

Once the application is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Root & Health

- `GET /` - API information
- `GET /health` - Health check

### Products

- `GET /products` - Get all products with filtering and sorting
  - Query params: `category`, `price_min`, `price_max`, `in_stock`, `sort_by`, `order`
- `GET /products/low-stock` - Get products below reorder level
- `GET /products/{id}` - Get a specific product
- `POST /products` - Create a new product
- `PUT /products/{id}` - Update a product
- `DELETE /products/{id}` - Delete a product
- `POST /products/{id}/restock` - Add stock to a product
- `POST /products/bulk-upload` - Bulk upload multiple products
- `PUT /products/bulk-restock` - Bulk restock multiple products
- `POST /products/sales` - Record a sales transaction

### Analytics

- `GET /analytics/sales-trends?period=7d` - Get sales trends (7d, 30d, 90d)
- `GET /analytics/demand-forecast/{id}` - Forecast demand for a product
- `GET /analytics/inventory-turnover?category=X` - Calculate turnover ratio
- `GET /analytics/top-performers?limit=5` - Get top products by revenue
- `GET /analytics/restock-urgency` - Get prioritized restock recommendations

## Example API Calls

### Product Operations

#### Get All Products with Filtering

```bash
curl -X GET "http://localhost:8000/products?category=Smartphones&price_max=1000&sort_by=price&order=asc"
```

#### Get Low Stock Products

```bash
curl -X GET "http://localhost:8000/products/low-stock"
```

#### Create New Product

```bash
curl -X POST "http://localhost:8000/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AirPods Pro 2",
    "category": "Audio",
    "price": 249.99,
    "stock_quantity": 35,
    "reorder_level": 20,
    "supplier": "Apple Inc.",
    "warranty_months": 12
  }'
```

#### Update Product

```bash
curl -X PUT "http://localhost:8000/products/1" \
  -H "Content-Type: application/json" \
  -d '{
    "price": 899.99,
    "stock_quantity": 55
  }'
```

#### Bulk Upload Products

```bash
curl -X POST "http://localhost:8000/products/bulk-upload" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "name": "Google Pixel 8",
      "category": "Smartphones",
      "price": 699.99,
      "stock_quantity": 25,
      "reorder_level": 15,
      "supplier": "Google LLC",
      "warranty_months": 24
    },
    {
      "name": "Dell XPS 15",
      "category": "Laptops",
      "price": 1899.99,
      "stock_quantity": 10,
      "reorder_level": 5,
      "supplier": "Dell Technologies",
      "warranty_months": 12
    }
  ]'
```

#### Bulk Restock Products

```bash
curl -X PUT "http://localhost:8000/products/bulk-restock" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"product_id": 1, "quantity": 50},
      {"product_id": 2, "quantity": 30},
      {"product_id": 3, "quantity": 20}
    ]
  }'
```

#### Record a Sale

```bash
curl -X POST "http://localhost:8000/products/sales" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "quantity_sold": 5,
    "sale_price": 999.99
  }'
```

### Analytics Operations

#### Get Sales Trends

```bash
# 7-day trends
curl -X GET "http://localhost:8000/analytics/sales-trends?period=7d"

# 30-day trends
curl -X GET "http://localhost:8000/analytics/sales-trends?period=30d"
```

#### Get Demand Forecast

```bash
curl -X GET "http://localhost:8000/analytics/demand-forecast/1"
```

#### Get Inventory Turnover

```bash
# All categories
curl -X GET "http://localhost:8000/analytics/inventory-turnover"

# Specific category
curl -X GET "http://localhost:8000/analytics/inventory-turnover?category=Smartphones"
```

#### Get Top Performers

```bash
curl -X GET "http://localhost:8000/analytics/top-performers?limit=10"
```

#### Get Restock Urgency

```bash
curl -X GET "http://localhost:8000/analytics/restock-urgency"
```

## Database Schema

### Products Table

| Column          | Type         | Description                        |
|----------------|--------------|-------------------------------------|
| id             | SERIAL       | Primary key                         |
| name           | VARCHAR(255) | Product name                        |
| category       | VARCHAR(100) | Product category                    |
| price          | DECIMAL      | Product price (>= 0)                |
| stock_quantity | INTEGER      | Current stock quantity (>= 0)       |
| reorder_level  | INTEGER      | Minimum stock before reorder (>= 0) |
| supplier       | VARCHAR(100) | Supplier name                       |
| warranty_months| INTEGER      | Warranty period in months           |
| last_restocked | TIMESTAMP    | Last restock timestamp              |
| created_at     | TIMESTAMP    | Creation timestamp                  |
| updated_at     | TIMESTAMP    | Last update timestamp               |

### Sales History Table

| Column        | Type      | Description                    |
|--------------|-----------|--------------------------------|
| id           | SERIAL    | Primary key                    |
| product_id   | INTEGER   | Foreign key to products        |
| quantity_sold| INTEGER   | Quantity sold (> 0)            |
| sale_price   | DECIMAL   | Price per unit at sale time    |
| sale_date    | TIMESTAMP | When the sale occurred         |
| created_at   | TIMESTAMP | Record creation timestamp      |

### Indexes

**Products:**
- `idx_products_name` on `name`
- `idx_products_category` on `category`
- `idx_products_stock_quantity` on `stock_quantity`
- `idx_products_price` on `price`

**Sales History:**
- `idx_sales_product_id` on `product_id`
- `idx_sales_date` on `sale_date`

## Business Logic & Forecasting

### Demand Forecasting Formula

The system uses a **7-day moving average** for demand forecasting:

```
avg_daily_sales = total_sales_last_7_days / 7
estimated_days_until_stockout = current_stock / avg_daily_sales
recommended_reorder_quantity = max((14 * avg_daily_sales) - current_stock, reorder_level)
```

**Strategy**: Maintain 14 days of inventory based on recent sales patterns.

### Inventory Turnover Calculation

```
turnover_ratio = total_units_sold_30d / current_stock_quantity
```

**Interpretation:**
- `turnover_ratio > 1.0`: Fast-moving product
- `turnover_ratio < 1.0`: Slow-moving product (flags for review)

### Restock Urgency Scoring

```
urgency_score = (reorder_level - current_stock) / avg_daily_sales
```

**Action Levels:**
- **CRITICAL**: Out of stock OR < 2 days until stockout
- **HIGH**: Stock < 50% of reorder level OR < 5 days until stockout
- **MEDIUM**: Below reorder level but not critical

## Testing

### Run Unit Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=html

# Run specific test file
pytest tests/test_products.py -v

# Run specific test
pytest tests/test_analytics.py::test_demand_forecast_accuracy -v
```

### Test Coverage

The test suite includes:
- **Product Service Tests**: CRUD operations, bulk operations, sales recording
- **Analytics Service Tests**: Sales trends, forecasting, turnover, urgency scoring
- **Edge Cases**: Insufficient stock, non-existent products, zero sales scenarios

## Development

### Install PostgreSQL Client (Optional)

If you want to connect directly to the database without using Docker exec:

**Using Homebrew (macOS):**

```bash
brew install postgresql@15
```

After installation, add to your PATH (add to ~/.zshrc or ~/.bash_profile):

```bash
export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
```

Then reload your shell:

```bash
source ~/.zshrc  # or source ~/.bash_profile
```

Verify installation:

```bash
psql --version
```

### Connect to Database

**Option 1 - Using Docker exec (no psql installation needed):**

```bash
docker exec -it inventory_db psql -U kubo_user -d inventory_db
```

**Option 2 - Direct connection (requires psql client):**

```bash
psql -h localhost -p 5432 -U kubo_user -d inventory_db
```

When prompted, enter password: `password`

Or with password in command (less secure):

```bash
PGPASSWORD=password psql -h localhost -p 5432 -U kubo_user -d inventory_db
```

### Useful Database Commands

Once connected to the database via psql:

```sql
-- List all databases
\l

-- List all tables in current database
\dt

-- Describe products table structure
\d products

-- View all table indexes
\di

-- View table with row counts
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    pg_stat_get_live_tuples(c.oid) AS row_count
FROM pg_tables t
JOIN pg_class c ON t.tablename = c.relname
WHERE schemaname = 'public';

-- Select all products
SELECT * FROM products;

-- Count products
SELECT COUNT(*) FROM products;

-- Find low stock products
SELECT name, stock_quantity, reorder_level 
FROM products 
WHERE stock_quantity < reorder_level;

-- Products by category
SELECT category, COUNT(*) as count, SUM(stock_quantity) as total_stock
FROM products 
GROUP BY category;

-- Exit psql
\q
```

### Quick Database Queries (One-liners)

```bash
# View all products
docker exec -it inventory_db psql -U kubo_user -d inventory_db -c "SELECT * FROM products;"

# Count total products
docker exec -it inventory_db psql -U kubo_user -d inventory_db -c "SELECT COUNT(*) FROM products;"

# Check low stock items
docker exec -it inventory_db psql -U kubo_user -d inventory_db -c "SELECT name, stock_quantity, reorder_level FROM products WHERE stock_quantity < reorder_level;"
```

### View Database Logs

```bash
docker logs inventory_db
```

### Stop Database

```bash
docker-compose down
```

### Stop Database and Remove Data

```bash
docker-compose down -v
```

## Technologies Used

- **FastAPI** - Modern web framework for building APIs
- **PostgreSQL** - Relational database
- **psycopg2** - PostgreSQL adapter for Python with connection pooling
- **Pydantic** - Data validation using Python type hints
- **aiohttp** - Asynchronous HTTP client/server
- **uvicorn** - ASGI server implementation
- **pytest** - Testing framework with coverage support

## Architecture

### Project Structure

```
Smart-Inventory-Tracking/
├── main.py                          # FastAPI app with lifespan management
├── .env.example                     # Environment variables template
├── src/
│   ├── db/
│   │   ├── db_manager.py           # Connection pooling & database operations
│   │   └── migrations.sql          # Schema definitions & sample data
│   ├── models/
│   │   ├── product.py              # Product Pydantic models
│   │   ├── sale.py                 # Sales Pydantic models
│   │   └── restock.py              # Restock Pydantic models
│   ├── services/
│   │   ├── product_service.py      # Product business logic
│   │   ├── analytics_service.py    # Analytics & forecasting logic
│   │   └── cache_service.py        # In-memory caching service
│   └── routers/
│       ├── products.py             # Product API endpoints
│       └── analytics.py            # Analytics API endpoints
├── tests/
│   ├── test_products.py            # Product service unit tests
│   └── test_analytics.py           # Analytics service unit tests
├── docker-compose.yml              # PostgreSQL container config
├── pyproject.toml                  # Dependencies (uv/pip)
└── README.md
```

### Design Principles

1. **Separation of Concerns**: Business logic in services, API routing separate
2. **Connection Pooling**: Efficient database connection management
3. **Caching Strategy**: 5-minute TTL for analytics, cleared on sales
4. **Validation**: Pydantic models for request/response validation
5. **Error Handling**: Proper HTTP status codes and error messages
6. **Testing**: Comprehensive unit tests with mocked dependencies

## License

MIT

