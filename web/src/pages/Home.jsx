import React, { useEffect, useState } from 'react';
import { Layout, Menu, Button, Dropdown, Avatar, Space, Row, Col } from 'antd';
import {
  HomeOutlined,
  DatabaseOutlined,
  UserOutlined,
  ShoppingCartOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  UsergroupAddOutlined
} from '@ant-design/icons';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { isAuthenticated, getCurrentUserInfo } from '../utils/auth';

const { Header, Sider, Content } = Layout;

const Home = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [userinfo, setUserinfo] = useState(null);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const userInfo = getCurrentUserInfo();
    setUserinfo(userInfo);
  }, []);

  // 检查用户是否为管理员
  const hasAdminRole = () => {
    return userinfo && userinfo.role === 'admin';
  };

  // 导航菜单项
  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '仪表板',
    },
    {
      key: '/data-management',
      icon: <DatabaseOutlined />,
      label: '订单管理',
    },
    {
      key: '/good-management',
      icon: <ShoppingCartOutlined />,
      label: '商品台账',
    },
    {
      key: '/userstore-management',
      icon: <UserOutlined />,
      label: '店铺管理',
    },
    {
      key: '/usergood-management',
      icon: <UserOutlined />,
      label: '用户商品管理',
    },
    ...(hasAdminRole() ? [{
      key: '/user-management',
      icon: <UsergroupAddOutlined />,
      label: '用户管理',
    }] : []),
  ];

  const handleMenuClick = (e) => {
    navigate(e.key);
  };


  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userinfo');
    navigate('/login');
  };

  const menuOverlay = {
    items: [
      {
        key: 'logout',
        icon: <LogoutOutlined />,
        danger: true,
        label: '退出登录',
        onClick: handleLogout,
      },
    ],
  }

  // 根据当前路径确定选中的菜单项
  const selectedKeys = [location.pathname];

  // 根据路径显示页面标题
  const getPageTitle = () => {
    switch (location.pathname) {
      case '/': return '仪表板';
      case '/data-management': return '数据管理';
      case '/good-management': return '商品管理';
      case '/userstore-management': return '店铺管理';
      case '/user-management': return '用户管理';
      default: return '首页';
    }
  };

  // 如果用户未登录，重定向到登录页面
  if (!isAuthenticated()) {
    navigate('/login');
    return null;
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider trigger={null} collapsible collapsed={collapsed} width={256}>
        <div className="logo" style={{ height: '64px', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '0 16px' }}>
          <img src="https://assets.sursung.com/prod/gylsc/static/channelLogo.ae1c123a.svg" alt="Logo" style={{ height: '32px', marginRight: '8px' }} />
          {!collapsed && <span style={{ fontSize: '18px', fontWeight: 'bold', color: '#fff' }}>聚水潭系统</span>}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={selectedKeys}
          onClick={handleMenuClick}
          items={menuItems}
        />
      </Sider>

      <Layout className="site-layout">

        <Header className="site-layout-background" style={{ padding: 0, background: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingLeft: 16 }}>
          <Row align="middle" style={{ width: '100%' }}>
            <Col span={12}>
              <Button
                type="text"
                icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
                onClick={() => setCollapsed(!collapsed)}
                style={{
                  fontSize: '16px',
                  width: 64,
                  height: 64,
                }}
              />
              <span style={{ fontSize: '18px', fontWeight: 'bold' }}>{getPageTitle()}</span>
            </Col>
            <Col span={12} style={{ textAlign: 'right', paddingRight: 24 }}>
              <Dropdown
                menu={{
                  items: [
                    {
                      key: 'logout',
                      icon: <LogoutOutlined />,
                      danger: true,
                      label: '退出登录',
                      onClick: handleLogout,
                    },
                  ],
                }}
                placement="bottomRight"
              >
                <Space style={{ cursor: 'pointer' }}>
                  <Avatar size="large" style={{ backgroundColor: '#1890ff' }}>
                    {userinfo?.username?.charAt(0)?.toUpperCase() || 'U'}
                  </Avatar>
                  <span>{userinfo?.username || '管理员'}</span>
                </Space>
              </Dropdown>
            </Col>
          </Row>
        </Header>


        <Content
          className="site-layout-background"
          style={{
            margin: '24px 16px',
            padding: 10,
            minHeight: 280,
            overflow: 'auto',
          }}
        >
          <Outlet />
        </Content>


      </Layout>
    </Layout>
  );
};

export default Home;