import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import Home from './pages/Home';
import Dash from './components/Dash';
import DataManagement from './pages/DataManagement';
import UserManagement from './pages/UserManagement';
import { isAuthenticated } from './utils/auth';

function App() {
  const authStatus = isAuthenticated(); // 使用专门的身份验证函数
  const userinfo = JSON.parse(localStorage.getItem('userinfo'));


  return (
    <div className="App">
      <Routes>
        <Route 
          path="/login" 
          element={!authStatus ? <LoginPage /> : <Navigate to="/" />} 
        />
        <Route 
          path="/" 
          element={authStatus ? <Home /> : <Navigate to="/login" />}
        >
          <Route index element={<Dash />} />
          <Route path="data-management" element={<DataManagement />} />
          {userinfo && userinfo.role === 'admin' && <Route path="user-management" element={<UserManagement />} />}
        </Route>
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </div>
  );
}

export default App;