import React, { useState, useEffect } from 'react';
import ClientManager from './components/ClientManager';
import CommodityManager from './components/CommodityManager';
import StockAcceptanceManager from './components/StockAcceptanceManager';
import StockDeliveryManager from './components/StockDeliveryManager';
import Login from './components/Login';

function App() {
  const [user, setUser] = useState(null);

  // Restore user from localStorage on first load
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  // Called after successful login
  const handleLogin = (userData) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  if (!user) {
    return <Login onLogin={handleLogin} />;
  }

  const { username, role } = user;

  return (
    <div className="bg-gray-100 min-h-screen p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">
          Welcome, {username} ({role})
        </h2>
        <button
          onClick={handleLogout}
          className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
        >
          Logout
        </button>
      </div>

      {role === 'admin' && (
        <>
          <ClientManager />
          <CommodityManager user={user} />
          <StockAcceptanceManager user={user} />
          <StockDeliveryManager user={user} />
        </>
      )}

      {role === 'manager' && (
        <>
          <ClientManager />
          <StockAcceptanceManager user={user} />
          <StockDeliveryManager user={user} />
        </>
      )}

      {role === 'staff' && (
        <>
          <StockAcceptanceManager user={user} />
          <StockDeliveryManager user={user} />
        </>
      )}
    </div>
  );
}

export default App;
