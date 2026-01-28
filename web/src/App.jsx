import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
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
import StoreManagement from './views/StoreManagement';
import UserGoodManagement from './views/UserGoodManagement';

function App() {
  return (
    <ConfigProvider locale={zhCN}>
        <Routes>

          {/* 登录页 */}
          <Route path="/login" element={<LoginPage />} />

          {/* 后台布局 */}
          <Route path="/" element={<Home />}>
            <Route
              index
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />

            <Route
              path="data-management"
              element={
                <ProtectedRoute>
                  <DataManagement />
                </ProtectedRoute>
              }
            />

            <Route
              path="good-management"
              element={
                <ProtectedRoute>
                  <GoodManagement />
                </ProtectedRoute>
              }
            />

            <Route
              path="userstore-management"
              element={
                <ProtectedRoute>
                  <StoreManagement />
                </ProtectedRoute>
              }
            />

            <Route
              path="user-management"
              element={
                <ProtectedRoute>
                  <UserManagement />
                </ProtectedRoute>
              }
            />

            <Route
              path="usergood-management"
              element={
                <ProtectedRoute>
                  <UserGoodManagement />
                </ProtectedRoute>
              }
            />

            {/* 未匹配路径 */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>

        </Routes>
    </ConfigProvider>
  );
}

export default App;