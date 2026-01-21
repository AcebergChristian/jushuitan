// 身份验证辅助函数

// 检查用户是否已认证
export const isAuthenticated = () => {
  const token = localStorage.getItem('token');
  return !!token;
};

// 获取当前用户的token
export const getToken = () => {
  return localStorage.getItem('token');
};


// 验证token是否有效（通过调用API）
export const validateToken = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/users/me', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${getToken()}`
      }
    });
    
    return response.ok;
  } catch (error) {
    console.error('Token validation error:', error);
    return false;
  }
};




// 登录并存储用户信息
export const loginAndStoreUserInfo = async (username, password) => {
  try {
    const response = await fetch('http://localhost:8000/api/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        username: username,
        password: password,
      }),
    });

    if (response.ok) {
      const data = await response.json();
      // 存储token
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('userinfo', JSON.stringify(data.userinfo));
      
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





// 获取当前用户信息（从本地存储）
export const getCurrentUserInfo = () => {
  const userinfo = localStorage.getItem('userinfo');
  // 检查userinfo是否存在且不为"undefined"
  if (!userinfo || userinfo === "undefined") {
    return null;
  }
  try {
    return JSON.parse(userinfo);
  } catch (error) {
    console.error('解析用户信息失败:', error);
    return null;
  }
};