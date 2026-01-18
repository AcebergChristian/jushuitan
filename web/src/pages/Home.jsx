import React, { useState } from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { 
  HomeIcon, 
  TableCellsIcon, 
  UserGroupIcon, 
  ArrowLeftOnRectangleIcon,
  Bars3Icon,
  XMarkIcon 
} from '@heroicons/react/24/outline';

const Home = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  const navigation = [
    { name: '仪表板', href: '/', icon: HomeIcon },
    { name: '数据管理', href: '/data-management', icon: TableCellsIcon },
    { name: '用户管理', href: '/user-management', icon: UserGroupIcon },
  ];

  const isActive = (path) => location.pathname === path;

  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.href = '/login'; // 确保退出后跳转到登录页
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-row">
      {/* 移动端侧边栏覆盖层 */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 lg:hidden bg-black bg-opacity-50"
          onClick={() => setSidebarOpen(false)}
        ></div>
      )}

      {/* 侧边栏 */}
      <div 
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-y-0 lg:h-screen`}
      >
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center">
            <div className="h-8 w-8 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg"></div>
            <span className="ml-2 text-xl font-bold text-gray-900">聚水潭系统</span>
          </div>
          <button
            type="button"
            className="lg:hidden -mr-2 h-6 w-6 rounded-md p-1 text-gray-500 hover:text-gray-600"
            onClick={() => setSidebarOpen(false)}
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        <nav className="mt-5 px-2 space-y-1">
          {navigation.map((item) => (
            <Link
              key={item.name}
              to={item.href}
              className={`${
                isActive(item.href)
                  ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                  : 'text-gray-700 hover:bg-gray-100'
              } group flex items-center px-4 py-3 text-sm font-medium rounded-lg transition duration-150`}
              onClick={() => setSidebarOpen(false)}
            >
              <item.icon
                className={`${
                  isActive(item.href) ? 'text-blue-600' : 'text-gray-500'
                } mr-3 h-5 w-5 flex-shrink-0`}
              />
              {item.name}
            </Link>
          ))}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          >
            <ArrowLeftOnRectangleIcon className="h-5 w-5 mr-2" />
            退出登录
          </button>
        </div>
      </div>

      {/* 主内容区 */}
      <div className=" flex flex-col flex-1">
        {/* 顶部导航栏 */}
        <header className="sticky top-0 z-10 bg-white shadow-sm">
          <div className="flex items-center justify-between px-4 py-3">
            <div className="flex items-center">
              <button
                type="button"
                className="lg:hidden -ml-0.5 mr-2 h-10 w-10 rounded-md p-2 text-gray-500 hover:text-gray-600 hover:bg-gray-100"
                onClick={() => setSidebarOpen(true)}
              >
                <Bars3Icon className="h-6 w-6" />
              </button>
              <h1 className="text-xl font-semibold text-gray-900 capitalize">
                {location.pathname === '/' ? '仪表板' : 
                 location.pathname.includes('data-management') ? '数据管理' : 
                 location.pathname.includes('user-management') ? '用户管理' : '首页'}
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center">
                <div className="h-8 w-8 rounded-full bg-gradient-to-r from-blue-500 to-indigo-500 flex items-center justify-center">
                  <span className="text-white text-sm font-medium">管</span>
                </div>
                <span className="ml-2 text-sm font-medium text-gray-700">管理员</span>
              </div>
            </div>
          </div>
        </header>

        {/* 页面内容 */}
        <main className="flex-1">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Home;