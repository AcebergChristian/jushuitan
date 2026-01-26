import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import LoginPage from './pages/LoginPage';
import Home from './pages/Home';
import ProtectedRoute from './components/ProtectedRoute';

// 引入视图组件
import Dashboard from './views/Dashboard';
import DataManagement from './views/DataManagement';
import GoodManagement from './views/GoodManagement';
import UserManagement from './views/UserManagement';
import UserStoreManagement from './views/UserStoreManagement';
import UserGoodManagement from './views/UserGoodManagement';

function App() {
  return (
    <ConfigProvider locale={zhCN}>
        <Routes>
          <Route 
            path="/login" 
            element={<LoginPage />} 
          />
          <Route 
            path="/*" 
            element={<Home />} 
          >
            <Route index element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="data-management" element={<ProtectedRoute><DataManagement /></ProtectedRoute>} />
            <Route path="good-management" element={<ProtectedRoute><GoodManagement /></ProtectedRoute>} />
            <Route path="userstore-management" element={<ProtectedRoute><UserStoreManagement /></ProtectedRoute>} />
            <Route path="user-management" element={<ProtectedRoute><UserManagement /></ProtectedRoute>} />
            <Route path="usergood-management" element={<ProtectedRoute><UserGoodManagement /></ProtectedRoute>} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
    </ConfigProvider>
  );
}

export default App;