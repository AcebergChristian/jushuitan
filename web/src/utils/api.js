// API工具函数
import { message } from 'antd';
import { history } from './history';

const API_BASE_URL = 'http://localhost:8000';  // 基础URL，不包含/api

// 通用API请求函数
export const apiRequest = async (endpoint, options = {}) => {
  // 确保endpoint以/api开头
  const normalizedEndpoint = endpoint.startsWith('/api') ? endpoint : `/api${endpoint}`;
  const url = `${API_BASE_URL}${normalizedEndpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  // 如果有token，则添加到请求头
  const token = localStorage.getItem('token');
  if (token && !config.headers.Authorization) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  try {
    const response = await fetch(url, config);

    // 如果是401错误（未授权），则跳转到登录页
    if (response.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('userinfo');
      message.error('登录已过期，请重新登录');
      history.push('/login');
      return null;
    }
    
    // 如果是其他错误状态码
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = errorData.message || `请求失败: ${response.status} ${response.statusText}`;
      message.error(errorMessage);
      
      // 如果是403或其他认证相关错误也跳转到登录
      if ([401, 403, 422, 400, 405].includes(response.status)) {
        localStorage.removeItem('token');
        localStorage.removeItem('userinfo');
        history.push('/login');
        return null;
      }
      
      throw new Error(errorMessage);
    }
    
    return response;
  } catch (error) {
    // 处理网络错误等
    if (error.name === 'TypeError' && error.message.includes('NetworkError')) {
      message.error('网络连接失败，请检查网络设置');
    } else {
      message.error(error.message || '请求发生错误');
    }
    throw error;
  }
};

// 登录函数
export const login = async (username, password) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        username: username,
        password: password,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || errorData.message || '登录失败');
    }
    
    return response;
  } catch (error) {
    throw error;
  }
};

// 获取当前用户信息
export const getCurrentUser = async () => {
  const response = await apiRequest('/users/me');  // 调用时不需要加/api，函数内部会处理
  if (response) {
    return response.json();
  }
  return null;
};