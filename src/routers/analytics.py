from fastapi import APIRouter, HTTPException, status, Request, Query
from typing import Optional
from src.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/sales-trends", summary="Get sales trends for specified period")
async def get_sales_trends(
    request: Request,
    period: str = Query("7d", description="Time period: 7d, 30d, or 90d")
):
    """
    Calculate sales trends including total revenue, units sold, and top products.
    
    **Parameters:**
    - **period**: Time period for analysis (7d, 30d, or 90d)
    
    **Returns:**
    - period: Selected time period
    - total_revenue: Total revenue in the period
    - total_units: Total units sold
    - top_products: List of products with sales data
    - categories: Category-wise breakdown
    
    **Example Response:**
    ```json
    {
        "period": "7d",
        "total_revenue": 45678.90,
        "total_units": 125,
        "top_products": [
            {
                "product_id": 1,
                "name": "iPhone 15 Pro",
                "category": "Smartphones",
                "units_sold": 50,
                "revenue": 49999.50
            }
        ],
        "categories": [
            {
                "category": "Smartphones",
                "units_sold": 75,
                "revenue": 67499.25
            }
        ]
    }
    ```
    """
    valid_periods = {"7d": 7, "30d": 30, "90d": 90}
    
    if period not in valid_periods:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid period. Must be one of: {', '.join(valid_periods.keys())}"
        )
    
    period_days = valid_periods[period]
    
    try:
        analytics_service = AnalyticsService(request.app.state.db_manager)
        trends = analytics_service.calculate_sales_trends(period_days)
        return trends
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating sales trends: {str(e)}"
        )


@router.get("/demand-forecast/{product_id}", summary="Forecast demand for a product")
async def forecast_demand(product_id: int, request: Request):
    """
    Forecast demand using 7-day moving average and calculate reorder recommendations.
    
    **Parameters:**
    - **product_id**: ID of the product to forecast
    
    **Returns:**
    - product_id: Product identifier
    - product_name: Product name
    - current_stock: Current stock quantity
    - reorder_level: Configured reorder level
    - avg_daily_sales: Average daily sales (7-day moving average)
    - estimated_days_until_stockout: Estimated days until stock runs out
    - recommended_reorder_quantity: Suggested quantity to order
    - forecast_period: Forecasting method used
    
    **Example Response:**
    ```json
    {
        "product_id": 1,
        "product_name": "iPhone 15 Pro",
        "current_stock": 45,
        "reorder_level": 15,
        "avg_daily_sales": 5.71,
        "estimated_days_until_stockout": 7.9,
        "recommended_reorder_quantity": 0,
        "forecast_period": "7 days moving average"
    }
    ```
    """
    try:
        analytics_service = AnalyticsService(request.app.state.db_manager)
        forecast = analytics_service.forecast_demand(product_id)
        return forecast
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error forecasting demand: {str(e)}"
        )


@router.get("/inventory-turnover", summary="Calculate inventory turnover ratio")
async def get_inventory_turnover(
    request: Request,
    category: Optional[str] = Query(None, description="Filter by product category")
):
    """
    Calculate inventory turnover ratio and identify slow-moving items.
    
    Turnover ratio = Total units sold / Average inventory
    Slow-moving items have turnover < 1.0
    
    **Parameters:**
    - **category**: Optional category filter
    
    **Returns:**
    - category: Category analyzed (or "All")
    - period: Analysis period
    - average_turnover_ratio: Average turnover across products
    - slow_moving_products: List of products with turnover < 1.0
    
    **Example Response:**
    ```json
    {
        "category": "Smartphones",
        "period": "30 days",
        "average_turnover_ratio": 2.45,
        "slow_moving_products": [
            {
                "product_id": 4,
                "name": "Sony WH-1000XM5",
                "category": "Audio",
                "current_stock": 5,
                "units_sold_30d": 27,
                "turnover_ratio": 0.54
            }
        ]
    }
    ```
    """
    try:
        analytics_service = AnalyticsService(request.app.state.db_manager)
        turnover = analytics_service.calculate_inventory_turnover(category)
        return turnover
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating inventory turnover: {str(e)}"
        )


@router.get("/top-performers", summary="Get top performing products")
async def get_top_performers(
    request: Request,
    limit: int = Query(5, ge=1, le=50, description="Number of top products to return")
):
    """
    Get top performing products by revenue in the last 30 days.
    
    **Parameters:**
    - **limit**: Number of top products to return (1-50)
    
    **Returns:**
    List of top products with:
    - product_id: Product identifier
    - product_name: Product name
    - category: Product category
    - units_sold: Total units sold in 30 days
    - revenue: Total revenue generated
    - stock_remaining: Current stock level
    
    **Example Response:**
    ```json
    [
        {
            "product_id": 1,
            "product_name": "iPhone 15 Pro",
            "category": "Smartphones",
            "units_sold": 150,
            "revenue": 149998.50,
            "stock_remaining": 45
        },
        {
            "product_id": 2,
            "product_name": "Samsung Galaxy S24",
            "category": "Smartphones",
            "units_sold": 120,
            "revenue": 107999.00,
            "stock_remaining": 8
        }
    ]
    ```
    """
    try:
        analytics_service = AnalyticsService(request.app.state.db_manager)
        top_performers = analytics_service.get_top_performers(limit)
        return top_performers
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting top performers: {str(e)}"
        )


@router.get("/restock-urgency", summary="Get restock urgency for low-stock products")
async def get_restock_urgency(request: Request):
    """
    Calculate urgency scores for products below reorder level.
    
    Urgency score = (reorder_level - current_stock) / avg_daily_sales
    Higher score indicates more urgent restocking need.
    
    **Action Levels:**
    - **CRITICAL**: Out of stock or < 2 days until stockout
    - **HIGH**: Stock < 50% of reorder level or < 5 days until stockout
    - **MEDIUM**: Below reorder level but not critical
    
    **Returns:**
    List of low-stock products sorted by urgency (highest first):
    - product_id: Product identifier
    - product_name: Product name
    - category: Product category
    - current_stock: Current stock quantity
    - reorder_level: Configured reorder level
    - avg_daily_sales: Average daily sales (7-day moving average)
    - days_until_stockout: Estimated days until stock depletes
    - urgency_score: Calculated urgency score
    - action: Urgency level (CRITICAL/HIGH/MEDIUM)
    
    **Example Response:**
    ```json
    [
        {
            "product_id": 2,
            "product_name": "Samsung Galaxy S24",
            "category": "Smartphones",
            "current_stock": 8,
            "reorder_level": 20,
            "avg_daily_sales": 9.71,
            "days_until_stockout": 0.8,
            "urgency_score": 1.24,
            "action": "CRITICAL"
        },
        {
            "product_id": 4,
            "product_name": "Sony WH-1000XM5",
            "category": "Audio",
            "current_stock": 5,
            "reorder_level": 15,
            "avg_daily_sales": 3.86,
            "days_until_stockout": 1.3,
            "urgency_score": 2.59,
            "action": "CRITICAL"
        }
    ]
    ```
    """
    try:
        analytics_service = AnalyticsService(request.app.state.db_manager)
        urgency_data = analytics_service.get_restock_urgency()
        return urgency_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating restock urgency: {str(e)}"
        )

