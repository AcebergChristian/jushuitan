// API工具函数
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

  const response = await fetch(url, config);

  if (!response.ok) {
    localStorage.removeItem('token');
    localStorage.removeItem('userinfo');

    // 如果响应状态不是200-299，则抛出错误
    const errorData = await response.json();
    throw new Error(errorData.message || '请求失败');
  }
  return response;
  // 如果是401错误（未授权），则跳转到登录页
  // if (response.status === 401) {
  //   localStorage.removeItem('token');
  //   localStorage.removeItem('userinfo');
  //   window.location.href = '/login';
  //   return null;
  // }

  // return response;
};

// 登录函数 - 注意：登录不需要/api前缀，因为它已经在后端定义为根路径
export const login = async (username, password) => {
  const response = await fetch(`${API_BASE_URL}/api/login`, {  // 添加/api前缀
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({
      username: username,
      password: password,
    }),
  });

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