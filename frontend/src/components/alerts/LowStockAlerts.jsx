import { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { AlertTriangle, Package } from 'lucide-react';

export const LowStockAlerts = () => {
  const [lowStockItems, setLowStockItems] = useState([]);
  const [restockUrgency, setRestockUrgency] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    try {
      const [lowStock, urgency] = await Promise.all([
        api.getLowStock(),
        api.getRestockUrgency()
      ]);
      setLowStockItems(lowStock.data);
      setRestockUrgency(urgency.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching alerts:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-20">Loading alerts...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-800">Low Stock Alerts</h1>
        <p className="text-gray-500 mt-1">{lowStockItems.length} items need attention</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle className="text-red-600" size={24} />
            <h2 className="text-xl font-semibold text-gray-800">Critical Stock Levels</h2>
          </div>
          <div className="space-y-3">
            {lowStockItems.map(item => (
              <div key={item.id} className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold text-gray-800">{item.name}</p>
                    <p className="text-sm text-gray-500">{item.category}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-red-600">{item.stock_quantity} left</p>
                    <p className="text-xs text-gray-500">Min: {item.reorder_level}</p>
                  </div>
                </div>
              </div>
            ))}
            {lowStockItems.length === 0 && (
              <p className="text-center text-gray-400 py-8">No critical stock alerts</p>
            )}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center gap-2 mb-4">
            <Package className="text-blue-600" size={24} />
            <h2 className="text-xl font-semibold text-gray-800">Restock Recommendations</h2>
          </div>
          <div className="space-y-3">
            {restockUrgency.map(item => (
              <div key={item.product_id} className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold text-gray-800">{item.product_name}</p>
                    <p className="text-sm text-gray-500">Current: {item.current_stock}</p>
                  </div>
                  <div className="text-right">
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      item.action === 'CRITICAL'
                        ? 'bg-red-100 text-red-800'
                        : item.action === 'HIGH'
                        ? 'bg-orange-100 text-orange-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {item.action} priority
                    </span>
                    <p className="text-xs text-gray-500 mt-1">Score: {item.urgency_score?.toFixed(2)}</p>
                  </div>
                </div>
              </div>
            ))}
            {restockUrgency.length === 0 && (
              <p className="text-center text-gray-400 py-8">No restock recommendations</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
