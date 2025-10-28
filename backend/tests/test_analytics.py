import pytest
from decimal import Decimal
from src.services.analytics_service import AnalyticsService
from unittest.mock import MagicMock


@pytest.fixture
def mock_db_manager():
    """Mock database manager for testing."""
    return MagicMock()


@pytest.fixture
def analytics_service(mock_db_manager):
    """Create AnalyticsService instance with mocked db_manager."""
    return AnalyticsService(mock_db_manager)


def test_sales_trends_calculation(analytics_service, mock_db_manager):
    """Test sales trends calculation."""
    # Mock sales data
    mock_data = [
        (1, "iPhone", "Smartphones", 50, Decimal("49999.50")),
        (2, "Samsung", "Smartphones", 30, Decimal("26999.70"))
    ]
    mock_category_data = [
        ("Smartphones", 80, Decimal("76999.20"))
    ]
    
    mock_db_manager.fetch_all.side_effect = [mock_data, mock_category_data]
    
    result = analytics_service.calculate_sales_trends(7)
    
    assert result["period"] == "7d"
    assert result["total_units"] == 80
    assert result["total_revenue"] > 76000
    assert len(result["top_products"]) == 2
    assert len(result["categories"]) == 1


def test_demand_forecast_accuracy(analytics_service, mock_db_manager):
    """Test demand forecasting calculation."""
    # Mock product data: id, name, stock_quantity, reorder_level
    mock_product = (1, "iPhone", 45, 15)
    # Mock sales data: total_sold
    mock_sales = (35,)
    
    mock_db_manager.fetch_one.side_effect = [mock_product, mock_sales]
    
    result = analytics_service.forecast_demand(1)
    
    assert result["product_id"] == 1
    assert result["product_name"] == "iPhone"
    assert result["current_stock"] == 45
    assert result["avg_daily_sales"] == 5.0  # 35 / 7
    assert result["estimated_days_until_stockout"] == 9.0  # 45 / 5
    assert result["recommended_reorder_quantity"] == 0  # Stock above reorder level


def test_demand_forecast_low_stock(analytics_service, mock_db_manager):
    """Test demand forecast for low stock product."""
    # Mock product with low stock
    mock_product = (1, "iPhone", 5, 15)
    mock_sales = (35,)
    
    mock_db_manager.fetch_one.side_effect = [mock_product, mock_sales]
    
    result = analytics_service.forecast_demand(1)
    
    assert result["current_stock"] < result["reorder_level"]
    assert result["recommended_reorder_quantity"] > 0


def test_urgency_score_calculation(analytics_service, mock_db_manager):
    """Test urgency score calculation for restock."""
    # Mock low stock products
    mock_data = [
        (1, "iPhone", "Smartphones", 5, 15, 35),  # Critical - very low stock
        (2, "Samsung", "Smartphones", 10, 20, 14)  # High - below reorder level
    ]
    
    mock_db_manager.fetch_all.return_value = mock_data
    
    result = analytics_service.get_restock_urgency()
    
    assert len(result) == 2
    # First product should have CRITICAL action
    assert result[0]["action"] in ["CRITICAL", "HIGH"]
    # Products sorted by urgency (descending)
    assert result[0]["urgency_score"] >= result[1]["urgency_score"]


def test_inventory_turnover_calculation(analytics_service, mock_db_manager):
    """Test inventory turnover ratio calculation."""
    # Mock product data with sales
    mock_data = [
        (1, "iPhone", "Smartphones", 50, 100),  # turnover = 2.0
        (2, "Samsung", "Smartphones", 100, 30)  # turnover = 0.3 (slow-moving)
    ]
    
    mock_db_manager.fetch_all.return_value = mock_data
    
    result = analytics_service.calculate_inventory_turnover()
    
    assert result["category"] == "All"
    assert result["average_turnover_ratio"] > 0
    # Should identify slow-moving products (turnover < 1.0)
    slow_moving = result["slow_moving_products"]
    assert len(slow_moving) > 0
    assert all(p["turnover_ratio"] < 1.0 for p in slow_moving)


def test_top_performers_ranking(analytics_service, mock_db_manager):
    """Test top performers ranking by revenue."""
    mock_data = [
        (1, "MacBook", "Laptops", 12, 50, Decimal("124999.50")),
        (2, "iPhone", "Smartphones", 45, 100, Decimal("99999.00")),
        (3, "iPad", "Tablets", 30, 75, Decimal("44999.25"))
    ]
    
    mock_db_manager.fetch_all.return_value = mock_data
    
    result = analytics_service.get_top_performers(limit=3)
    
    assert len(result) == 3
    # Should be sorted by revenue (descending)
    assert result[0]["revenue"] >= result[1]["revenue"]
    assert result[1]["revenue"] >= result[2]["revenue"]
    # MacBook should be first (highest revenue)
    assert result[0]["product_name"] == "MacBook"


def test_forecast_product_not_found(analytics_service, mock_db_manager):
    """Test forecast for non-existent product."""
    mock_db_manager.fetch_one.return_value = None
    
    with pytest.raises(ValueError) as exc_info:
        analytics_service.forecast_demand(999)
    
    assert "not found" in str(exc_info.value)


def test_turnover_with_category_filter(analytics_service, mock_db_manager):
    """Test inventory turnover with category filtering."""
    mock_data = [
        (1, "iPhone", "Smartphones", 50, 100),
        (2, "Samsung", "Smartphones", 45, 90)
    ]
    
    mock_db_manager.fetch_all.return_value = mock_data
    
    result = analytics_service.calculate_inventory_turnover(category="Smartphones")
    
    assert result["category"] == "Smartphones"
    assert result["period"] == "30 days"
    # Both products have good turnover (>1.0)
    assert len(result["slow_moving_products"]) == 0


def test_urgency_zero_sales(analytics_service, mock_db_manager):
    """Test urgency calculation for products with zero sales."""
    # Mock product with no recent sales
    mock_data = [
        (1, "Old Product", "Legacy", 5, 15, 0)  # No sales in last 7 days
    ]
    
    mock_db_manager.fetch_all.return_value = mock_data
    
    result = analytics_service.get_restock_urgency()
    
    assert len(result) == 1
    # With zero sales, urgency based on stock deficit only
    assert result[0]["avg_daily_sales"] == 0.0
    assert result[0]["days_until_stockout"] is None

