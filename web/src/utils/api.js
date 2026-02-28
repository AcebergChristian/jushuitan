// API工具函数
import { message } from 'antd';
import { history } from './history';

// 根据环境动态设置基础URL
const getApiBaseUrl = () => {
  if (typeof window !== 'undefined') {
    // 在生产环境中，如果前端和后端在同一域名下，但不同端口，需要指定端口
    // 或者使用绝对URL指向后端服务
    const isDev = process.env.NODE_ENV === 'development';
    if (isDev) {
      return ''; // 开发环境使用代理
    }
    // 生产环境：根据实际情况配置后端API的基础URL
    // 如果后端运行在相同域名的不同端口上，例如 :8000
    return window.location.protocol + '//' + window.location.hostname + ':8000';
  }
  return '';
};

const API_BASE_URL = getApiBaseUrl();

// 通用 API 请求函数（生产 / 开发通用）
export const apiRequest = async (endpoint, options = {}) => {
  // 统一保证 /api 前缀
  const url = endpoint.startsWith('/api') ? `${API_BASE_URL}${endpoint}` : `${API_BASE_URL}/api${endpoint}`;

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

// 登录函数 - 修改为使用动态基础URL
export const login = async (username, password) => {
  const isDev = process.env.NODE_ENV === 'development';
  let url;
  
  if (isDev) {
    url = ':8000/api/login';
  } else {
    // 生产环境使用完整URL（包含端口8000）
    url = `${window.location.protocol}//${window.location.hostname}/api/login`;
  }
  
  try {
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    credentials: 'include', // 包含cookies等凭证信息
    body: new URLSearchParams({
      username,
      password,
    }),
  });

  if (response.ok) {
      const data = await response.json();
      // 存储token
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('userinfo', data.userinfo);
      
      return { success: true, data };
    } else {
      // 尝试获取错误详情
      let errorDetail = '用户名或密码错误';
      try {
        const errorData = await response.json();
        errorDetail = errorData.detail || errorData.message || errorDetail;
      } catch (parseErr) {
        // 如果无法解析错误响应，则使用默认错误信息
      }
      return { success: false, error: errorDetail };
    }
  } catch (error) {
    console.error('Login error:', error);
    return { success: false, error: error.message };
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