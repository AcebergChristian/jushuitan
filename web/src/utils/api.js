// API工具函数
import { message } from 'antd';
import { history } from './history';

const API_BASE_URL = '';  // 使用相对路径，让代理配置生效


// 通用 API 请求函数（生产 / 开发通用）
export const apiRequest = async (endpoint, options = {}) => {
  // 统一保证 /api 前缀
  const url = endpoint.startsWith('/api') ? endpoint : `/api${endpoint}`;

  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  // 自动携带 token
  const token = localStorage.getItem('token');
  if (token && !config.headers.Authorization) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  try {
    const response = await fetch(url, config);

    // 未登录 / token 失效
    if (response.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
      return null;
    }

    return response;
  } catch (error) {
    console.error('API 请求失败:', error);
    throw error;
  }
};

// 登录函数
export const login = async (username, password) => {
  const response = await fetch('/api/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({
      username,
      password,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || '登录失败');
  }

  return response;
};

// 获取当前用户信息
export const getCurrentUser = async () => {
  const response = await apiRequest('/users/me');  // 调用时不需要加/api，函数内部会处理
  if (response) {
    return response.json();
  }
  return null;
};