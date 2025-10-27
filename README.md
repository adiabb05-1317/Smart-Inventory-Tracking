# Smart Inventory Tracking API

A FastAPI-based inventory management system for electronic stores with PostgreSQL database and connection pooling.

## Features

- Complete CRUD operations for product management
- Low stock monitoring and alerts
- Product restocking functionality
- Connection pooling for optimal database performance
- Swagger UI documentation
- CORS enabled for cross-origin requests

## Prerequisites

- Python 3.10+
- Docker and Docker Compose
- [uv](https://github.com/astral-sh/uv) package manager

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

### 1. Start PostgreSQL Database

```bash
docker-compose up -d
```

This will start a PostgreSQL container with:
- Username: `kubo_user`
- Password: `password`
- Database: `inventory_db`
- Port: `5432`

### 2. Run Database Migrations

Connect to the database and execute the migrations:

```bash
docker exec -i inventory_db psql -U kubo_user -d inventory_db < src/db/migrations.sql
```

### 3. Install Dependencies

Using uv package manager:

```bash
uv pip install -e .
```

Or using pip:

```bash
pip install -e .
```

### 4. Run the Application

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

- `GET /products` - Get all products
- `GET /products?low_stock=true` - Get products with low stock
- `GET /products/low-stock` - Get products below reorder level
- `GET /products/{id}` - Get a specific product
- `POST /products` - Create a new product
- `PUT /products/{id}` - Update a product
- `DELETE /products/{id}` - Delete a product
- `POST /products/{id}/restock` - Add stock to a product

## Example API Calls

### Get All Products

```bash
curl -X GET "http://localhost:8000/products"
```

### Get Low Stock Products

```bash
curl -X GET "http://localhost:8000/products/low-stock"
```

### Get Single Product

```bash
curl -X GET "http://localhost:8000/products/1"
```

### Create New Product

```bash
curl -X POST "http://localhost:8000/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AirPods Pro 2",
    "category": "Audio",
    "price": 249.99,
    "stock_quantity": 35,
    "reorder_level": 20
  }'
```

### Update Product

```bash
curl -X PUT "http://localhost:8000/products/1" \
  -H "Content-Type: application/json" \
  -d '{
    "price": 899.99,
    "stock_quantity": 55
  }'
```

### Restock Product

```bash
curl -X POST "http://localhost:8000/products/1/restock" \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": 50
  }'
```

### Delete Product

```bash
curl -X DELETE "http://localhost:8000/products/1"
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
| last_restocked | TIMESTAMP    | Last restock timestamp              |
| created_at     | TIMESTAMP    | Creation timestamp                  |
| updated_at     | TIMESTAMP    | Last update timestamp               |

### Indexes

- `idx_products_name` on `name`
- `idx_products_category` on `category`
- `idx_products_stock_quantity` on `stock_quantity`

## Development

### Check Database Connection

```bash
docker exec -it inventory_db psql -U kubo_user -d inventory_db
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
- **psycopg2** - PostgreSQL adapter for Python
- **Pydantic** - Data validation using Python type hints
- **aiohttp** - Asynchronous HTTP client/server
- **uvicorn** - ASGI server implementation

## License

MIT

