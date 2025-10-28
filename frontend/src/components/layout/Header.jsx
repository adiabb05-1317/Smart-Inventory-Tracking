import { Bell, User } from 'lucide-react';

export const Header = () => {
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-gray-800">Inventory Management</h2>
          <p className="text-sm text-gray-500">Manage your electronics store efficiently</p>
        </div>
        
        <div className="flex items-center gap-4">
          <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <Bell size={20} className="text-gray-600" />
          </button>
          <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <User size={20} className="text-gray-600" />
          </button>
        </div>
      </div>
    </header>
  );
};
