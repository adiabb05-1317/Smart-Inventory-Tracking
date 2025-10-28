import { useEffect, useState } from 'react';
import { useAnalyticsStore } from '../../stores/analyticsStore';

export const Analytics = () => {
  const { salesTrends, topPerformers, fetchSalesTrends, fetchTopPerformers } = useAnalyticsStore();
  const [period, setPeriod] = useState('30d');

  useEffect(() => {
    fetchSalesTrends(period);
    fetchTopPerformers(10);
  }, [period, fetchSalesTrends, fetchTopPerformers]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Analytics</h1>
          <p className="text-gray-500 mt-1">Sales performance and trends</p>
        </div>
        <select
          value={period}
          onChange={(e) => setPeriod(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="7d">Last 7 days</option>
          <option value="30d">Last 30 days</option>
          <option value="90d">Last 90 days</option>
        </select>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Sales Summary ({period})</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <p className="text-2xl font-bold text-blue-600">${salesTrends?.total_revenue?.toLocaleString() || 0}</p>
            <p className="text-gray-500">Total Revenue</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-green-600">{salesTrends?.total_units || 0}</p>
            <p className="text-gray-500">Units Sold</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-purple-600">{salesTrends?.categories?.length || 0}</p>
            <p className="text-gray-500">Active Categories</p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Top Performers</h2>
        <div className="space-y-3">
          {topPerformers.map((product, idx) => (
            <div key={product.product_id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-4">
                <span className="text-2xl font-bold text-gray-400">#{idx + 1}</span>
                <div>
                  <p className="font-semibold text-gray-800">{product.product_name}</p>
                  <p className="text-sm text-gray-500">{product.category}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-lg font-bold text-blue-600">{product.units_sold} sales</p>
                <p className="text-sm text-gray-500">${product.revenue?.toLocaleString()}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {salesTrends?.categories && salesTrends.categories.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Category Performance</h2>
          <div className="space-y-3">
            {salesTrends.categories.map((category, idx) => (
              <div key={idx} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-semibold text-gray-800">{category.category}</p>
                  <p className="text-sm text-gray-500">{category.units_sold} units sold</p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-green-600">${category.revenue?.toLocaleString()}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
