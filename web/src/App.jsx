import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import Home from './pages/Home';
import Dash from './components/Dash';
import DataManagement from './pages/DataManagement';
import UserManagement from './pages/UserManagement';

function App() {
  const isAuthenticated = !!localStorage.getItem('token'); // 简单的身份验证检查

  return (
    <div className="App">
      <Routes>
        <Route 
          path="/login" 
          element={!isAuthenticated ? <LoginPage /> : <Navigate to="/" />} 
        />
        <Route 
          path="/" 
          element={isAuthenticated ? <Home /> : <Navigate to="/login" />}
        >
          <Route index element={<Dash />} />
          <Route path="data-management" element={<DataManagement />} />
          <Route path="user-management" element={<UserManagement />} />
        </Route>
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </div>
  );
}

export default App;