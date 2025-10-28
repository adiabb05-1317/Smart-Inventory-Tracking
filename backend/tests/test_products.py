import pytest
from decimal import Decimal
from src.services.product_service import ProductService
from unittest.mock import MagicMock


@pytest.fixture
def mock_db_manager():
    """Mock database manager for testing."""
    return MagicMock()


@pytest.fixture
def product_service(mock_db_manager):
    """Create ProductService instance with mocked db_manager."""
    return ProductService(mock_db_manager)


def test_create_product_success(product_service, mock_db_manager):
    """Test successful product creation."""
    products_data = [{
        "name": "Test Product",
        "category": "Electronics",
        "price": 99.99,
        "stock_quantity": 50,
        "reorder_level": 10,
        "supplier": "Test Supplier",
        "warranty_months": 12
    }]
    
    mock_db_manager.execute_query.return_value = None
    
    result = product_service.bulk_create_products(products_data)
    
    assert result["created_count"] == 1
    assert result["failed_count"] == 0
    assert len(result["failures"]) == 0


def test_bulk_upload_partial_failure(product_service, mock_db_manager):
    """Test bulk upload with some failures."""
    products_data = [
        {
            "name": "Product 1",
            "category": "Electronics",
            "price": 99.99,
            "stock_quantity": 50,
            "reorder_level": 10
        },
        {
            "name": "Product 2",
            "category": "Electronics",
            "price": 149.99,
            "stock_quantity": 30,
            "reorder_level": 15
        }
    ]
    
    # First call succeeds, second fails
    mock_db_manager.execute_query.side_effect = [None, Exception("Database error")]
    
    result = product_service.bulk_create_products(products_data)
    
    assert result["created_count"] == 1
    assert result["failed_count"] == 1
    assert len(result["failures"]) == 1
    assert result["failures"][0]["index"] == 1


def test_restock_updates_quantity(product_service, mock_db_manager):
    """Test that restock properly updates quantities."""
    restock_data = [
        {"product_id": 1, "quantity": 50},
        {"product_id": 2, "quantity": 30}
    ]
    
    # Mock product existence check
    mock_db_manager.fetch_one.side_effect = [(1,), (2,)]
    mock_db_manager.execute_query.return_value = None
    
    result = product_service.bulk_restock_products(restock_data)
    
    assert result["updated_count"] == 2
    assert len(result["errors"]) == 0


def test_record_sale_reduces_stock(product_service, mock_db_manager):
    """Test that recording a sale reduces stock quantity."""
    # Mock product data: id, stock_quantity, name
    mock_db_manager.fetch_one.side_effect = [
        (1, 50, "Test Product"),  # Get product
        (1,),  # Insert sale
        (45,)  # Update stock returns remaining
    ]
    
    result = product_service.record_sale(
        product_id=1,
        quantity=5,
        sale_price=Decimal("99.99")
    )
    
    assert result["sale_id"] == 1
    assert result["product_name"] == "Test Product"
    assert result["quantity_sold"] == 5
    assert result["remaining_stock"] == 45


def test_record_sale_insufficient_stock(product_service, mock_db_manager):
    """Test that sale fails with insufficient stock."""
    # Mock product with low stock
    mock_db_manager.fetch_one.return_value = (1, 3, "Test Product")
    
    with pytest.raises(ValueError) as exc_info:
        product_service.record_sale(
            product_id=1,
            quantity=5,
            sale_price=Decimal("99.99")
        )
    
    assert "Insufficient stock" in str(exc_info.value)


def test_get_product_not_found(product_service, mock_db_manager):
    """Test handling of non-existent product."""
    mock_db_manager.fetch_one.return_value = None
    
    with pytest.raises(ValueError) as exc_info:
        product_service.record_sale(
            product_id=999,
            quantity=5,
            sale_price=Decimal("99.99")
        )
    
    assert "not found" in str(exc_info.value)


def test_get_products_with_filters(product_service, mock_db_manager):
    """Test product filtering functionality."""
    mock_data = [
        (1, "iPhone", "Smartphones", Decimal("999.99"), 50, 15, None, None, None, "Apple", 12),
        (2, "Samsung", "Smartphones", Decimal("899.99"), 30, 20, None, None, None, "Samsung", 24)
    ]
    mock_db_manager.fetch_all.return_value = mock_data
    
    result = product_service.get_products_with_filters(
        category="Smartphones",
        price_max=Decimal("1000.00"),
        sort_by="price",
        order="asc"
    )
    
    assert len(result) == 2
    assert mock_db_manager.fetch_all.called


def test_bulk_restock_nonexistent_product(product_service, mock_db_manager):
    """Test bulk restock with non-existent product."""
    restock_data = [{"product_id": 999, "quantity": 50}]
    
    # Mock product not found
    mock_db_manager.fetch_one.return_value = None
    
    result = product_service.bulk_restock_products(restock_data)
    
    assert result["updated_count"] == 0
    assert len(result["errors"]) == 1
    assert "not found" in result["errors"][0]["error"]

