import React, { useState, useEffect } from 'react';
import { Tab, Dialog, Transition } from '@headlessui/react';
import { Fragment } from 'react';
import {
  MagnifyingGlassIcon,
  FunnelIcon,
  ArrowDownTrayIcon,
  PlusIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import { apiRequest } from '../utils/api';

const StoreManagement = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [totalItems, setTotalItems] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [showNotification, setShowNotification] = useState({ show: false, message: '', type: '' });
  const [selectedUser, setSelectedUser] = useState(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [userGoods, setUserGoods] = useState([]);

  // 显示通知
  const showNotificationFunc = (message, type = 'success') => {
    setShowNotification({ show: true, message, type });
    setTimeout(() => {
      setShowNotification({ show: false, message: '', type: '' });
    }, 3000);
  };

  // 获取用户数据
  const fetchUsers = async (page = 1, size = 10, search = '') => {
    setLoading(true);
    try {
      const skip = (page - 1) * size;
      const limit = size;

      let url = `/users/?skip=${skip}&limit=${limit}`;
      if (search) {
        url += `&search=${encodeURIComponent(search)}`;
      }

      const response = await apiRequest(url);

      if (response.ok) {
        const responseData = await response.json();
        setUsers(responseData.map(user => ({
          ...user,
          goodsStores: user.goods_stores || [] // 保持一致的命名
        })));
        setTotalItems(responseData.length); // 这里可能需要后端返回总数量
      } else {
        console.error('获取用户数据失败:', response.statusText);
        showNotificationFunc('获取用户数据失败', 'error');
      }
    } catch (error) {
      console.error('获取用户数据错误:', error);
      showNotificationFunc('获取用户数据时发生错误', 'error');
    } finally {
      setLoading(false);
    }
  };

  // 获取特定用户关联的商品数据
  const fetchUserGoods = async (userId) => {
    try {
      const response = await apiRequest(`/users/${userId}/goods`);
      
      if (response.ok) {
        const data = await response.json();
        setUserGoods(data.data || []);
      } else {
        console.error('获取用户商品数据失败:', response.statusText);
        setUserGoods([]);
      }
    } catch (error) {
      console.error('获取用户商品数据错误:', error);
      setUserGoods([]);
    }
  };

  useEffect(() => {
    fetchUsers(currentPage, pageSize, searchTerm);
  }, [currentPage, pageSize]);

  // 处理搜索框变化
  const handleSearchChange = (e) => {
    const value = e.target.value;
    setSearchTerm(value);
  };

  // 处理搜索提交
  const handleSearchSubmit = () => {
    fetchUsers(currentPage, pageSize, searchTerm);
    setCurrentPage(1); // 搜索时回到第一页
  };

  // 查看用户详情
  const viewUserDetails = (user) => {
    setSelectedUser(user);
    fetchUserGoods(user.id); // 获取该用户关联的商品
    setIsDetailModalOpen(true);
  };

  // 渲染用户数据表格
  const renderUsersTable = () => {
    if (users.length === 0) {
      return (
        <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 rounded-lg">
          <table className="min-w-full divide-y divide-gray-300">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  暂无用户数据
                </th>
              </tr>
            </thead>
          </table>
        </div>
      );
    }

    return (
      <div className="shadow ring-1 ring-black ring-opacity-5 rounded-lg overflow-x-auto overflow-y-auto">
        <table className="min-w-full divide-y divide-gray-300">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">用户ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">用户名</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">邮箱</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">角色</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">关联店铺数</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[120px]">操作</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {users.map((user, index) => (
              <tr key={user.id || index} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{user.id}</td>
                <td className="px-6 py-4 text-sm text-gray-900 max-w-xs break-words">{user.username}</td>
                <td className="px-6 py-4 text-sm text-gray-900">{user.email}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{user.role}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {user.is_active ? '活跃' : '禁用'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {user.goodsStores ? user.goodsStores.length : 0}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <div className="flex justify-end space-x-2">
                    <button 
                      className="text-blue-600 hover:text-blue-900"
                      onClick={() => viewUserDetails(user)}
                    >
                      <EyeIcon className="h-5 w-5" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  // 详情模态框
  const DetailModal = () => {
    if (!selectedUser) return null;

    return (
      <Transition appear show={isDetailModalOpen} as={Fragment}>
        <Dialog as="div" className="relative z-10" onClose={() => setIsDetailModalOpen(false)}>
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black bg-opacity-25" />
          </Transition.Child>

          <div className="fixed inset-0 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4 text-center">
              <Transition.Child
                as={Fragment}
                enter="ease-out duration-300"
                enterFrom="opacity-0 scale-95"
                enterTo="opacity-100 scale-100"
                leave="ease-in duration-200"
                leaveFrom="opacity-100 scale-100"
                leaveTo="opacity-0 scale-95"
              >
                <Dialog.Panel className="w-full max-w-6xl transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                  <Dialog.Title
                    as="h3"
                    className="text-lg font-medium leading-6 text-gray-900 border-b pb-3"
                  >
                    用户详情 - {selectedUser.username}
                  </Dialog.Title>
                  
                  <div className="mt-4 max-h-[70vh] overflow-y-auto">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                      <div className="space-y-2">
                        <div className="flex">
                          <span className="w-32 text-sm font-medium text-gray-500">用户ID:</span>
                          <span className="text-sm text-gray-900">{selectedUser.id}</span>
                        </div>
                        <div className="flex">
                          <span className="w-32 text-sm font-medium text-gray-500">用户名:</span>
                          <span className="text-sm text-gray-900">{selectedUser.username}</span>
                        </div>
                        <div className="flex">
                          <span className="w-32 text-sm font-medium text-gray-500">邮箱:</span>
                          <span className="text-sm text-gray-900">{selectedUser.email}</span>
                        </div>
                        <div className="flex">
                          <span className="w-32 text-sm font-medium text-gray-500">角色:</span>
                          <span className="text-sm text-gray-900">{selectedUser.role}</span>
                        </div>
                        <div className="flex">
                          <span className="w-32 text-sm font-medium text-gray-500">状态:</span>
                          <span className="text-sm text-gray-900">{selectedUser.is_active ? '活跃' : '禁用'}</span>
                        </div>
                        <div className="flex">
                          <span className="w-32 text-sm font-medium text-gray-500">关联店铺数:</span>
                          <span className="text-sm text-gray-900">{selectedUser.goodsStores ? selectedUser.goodsStores.length : 0}</span>
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        <div className="flex">
                          <span className="w-32 text-sm font-medium text-gray-500">创建时间:</span>
                          <span className="text-sm text-gray-900">
                            {selectedUser.created_at ? new Date(selectedUser.created_at).toLocaleString() : '-'}
                          </span>
                        </div>
                        <div className="flex">
                          <span className="w-32 text-sm font-medium text-gray-500">更新时间:</span>
                          <span className="text-sm text-gray-900">
                            {selectedUser.updated_at ? new Date(selectedUser.updated_at).toLocaleString() : '-'}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* 关联的商品信息 */}
                    <div className="mt-6">
                      <h4 className="text-md font-medium text-gray-900 mb-3">关联商品信息</h4>
                      {userGoods.length > 0 ? (
                        <div className="overflow-x-auto">
                          <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                              <tr>
                                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">商品ID</th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">商品名称</th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">店铺ID</th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">店铺名称</th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">销售金额</th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">净利润</th>
                              </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                              {userGoods.map((good, index) => (
                                <tr key={good.id || index} className="hover:bg-gray-50">
                                  <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">{good.goods_id}</td>
                                  <td className="px-4 py-2 text-sm text-gray-900 max-w-xs truncate">{good.goods_name}</td>
                                  <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">{good.store_id}</td>
                                  <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">{good.store_name}</td>
                                  <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">¥{(good.sales_amount || 0).toFixed(2)}</td>
                                  <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">¥{(good.net_profit || 0).toFixed(2)}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      ) : (
                        <p className="text-sm text-gray-500">暂无关联商品信息</p>
                      )}
                    </div>
                  </div>

                  <div className="mt-6 flex justify-end">
                    <button
                      type="button"
                      className="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none outline-none"
                      onClick={() => setIsDetailModalOpen(false)}
                    >
                      关闭
                    </button>
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </Dialog>
      </Transition>
    );
  };

  // 分页栏组件
  const PaginationBar = () => {
    const totalPages = Math.ceil(totalItems / pageSize);

    return (
      <div className="flex items-center justify-between border-t border-gray-200 bg-white px-4 py-3 sm:px-6 mt-4">
        <div className="flex flex-1 justify-between sm:hidden">
          <button
            onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
            disabled={currentPage === 1}
            className={`relative inline-flex items-center rounded-md border px-4 py-2 text-sm font-medium ${currentPage === 1
                ? 'cursor-not-allowed border-gray-300 bg-gray-100 text-gray-400'
                : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
              }`}
          >
            上一页
          </button>
          <button
            onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
            disabled={currentPage === totalPages}
            className={`relative ml-3 inline-flex items-center rounded-md border px-4 py-2 text-sm font-medium ${currentPage === totalPages
                ? 'cursor-not-allowed border-gray-300 bg-gray-100 text-gray-400'
                : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
              }`}
          >
            下一页
          </button>
        </div>
        <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
          <div>
            <p className="text-sm text-gray-700">
              显示 <span className="font-medium">{(currentPage - 1) * pageSize + 1}</span> 到{' '}
              <span className="font-medium">
                {Math.min(currentPage * pageSize, totalItems)}
              </span>{' '}
              条，共 <span className="font-medium">{totalItems}</span> 条
            </p>
          </div>
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <label htmlFor="page-size" className="text-sm text-gray-700">每页显示:</label>
              <select
                id="page-size"
                value={pageSize}
                onChange={(e) => {
                  setPageSize(parseInt(e.target.value));
                  setCurrentPage(1);
                }}
                className="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              >
                <option value="5">5</option>
                <option value="10">10</option>
                <option value="20">20</option>
                <option value="50">50</option>
              </select>
            </div>
            <nav className="isolate inline-flex -space-x-px rounded-md shadow-sm ml-4" aria-label="Pagination">
              <button
                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
                className={`relative inline-flex items-center rounded-l-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 ${currentPage === 1 ? 'cursor-not-allowed opacity-50' : ''
                  }`}
              >
                <span className="sr-only">上一页</span>
                <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                  <path fillRule="evenodd" d="M12.79 5.23a.75.75 0 01-.02 1.06L8.832 10l3.938 3.71a.75.75 0 11-1.04 1.08l-4.5-4.25a.75.75 0 010-1.08l4.5-4.25a.75.75 0 011.06.02z" clipRule="evenodd" />
                </svg>
              </button>

              {/* 页码按钮 */}
              {[...Array(Math.min(5, totalPages || 1))].map((_, i) => {
                let pageNum;
                if (totalPages <= 5) {
                  // 总页数小于等于5，显示所有页码
                  pageNum = i + 1;
                } else if (currentPage <= 3) {
                  // 当前页靠近前面，显示前几页
                  pageNum = i + 1;
                } else if (currentPage >= totalPages - 2) {
                  // 当前页靠近后面，显示后几页
                  pageNum = totalPages - 4 + i;
                } else {
                  // 当前页在中间，显示当前页前后各两页
                  pageNum = currentPage - 2 + i;
                }

                if (pageNum <= totalPages) {
                  return (
                    <button
                      key={pageNum}
                      onClick={() => setCurrentPage(pageNum)}
                      className={`relative inline-flex items-center px-4 py-2 text-sm font-semibold ${currentPage === pageNum
                          ? 'z-10 bg-blue-600 text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600'
                          : 'text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50'
                        } focus:outline-offset-0`}
                    >
                      {pageNum}
                    </button>
                  );
                }
                return null;
              })}

              <button
                onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                disabled={currentPage === totalPages}
                className={`relative inline-flex items-center rounded-r-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 ${currentPage === totalPages ? 'cursor-not-allowed opacity-50' : ''
                  }`}
              >
                <span className="sr-only">下一页</span>
                <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                  <path fillRule="evenodd" d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z" clipRule="evenodd" />
                </svg>
              </button>
            </nav>
          </div>
        </div>
      </div>
    );
  };

  // 通知组件
  const Notification = () => {
    if (!showNotification.show) return null;

    const bgColor = showNotification.type === 'error' ? 'bg-red-500' : 'bg-green-500';

    return (
      <div className="fixed top-4 right-4 z-50">
        <div className={`${bgColor} text-white px-6 py-4 rounded-lg shadow-lg flex items-center`}>
          <span>{showNotification.message}</span>
          <button
            onClick={() => setShowNotification({ show: false, message: '', type: '' })}
            className="ml-4 text-white hover:text-gray-200"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">用户店铺关联管理</h1>
          <p className="mt-2 text-gray-600">管理用户与店铺及商品的关联关系</p>
        </div>

        {/* 搜索和筛选工具栏 */}
        <div className="bg-white rounded-xl shadow p-6 mb-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="flex-1 max-w-md">
              <div className="relative rounded-md shadow-sm">
                <div className="pointer-events-none absolute inset-y-0 left-0 pl-3 flex items-center">
                  <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  className="block w-full pl-10 pr-12 py-2.5 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 outline-none"
                  placeholder="搜索用户名..."
                  value={searchTerm}
                  onChange={handleSearchChange}
                />
              </div>
            </div>
            <div className="flex space-x-3">
              <button
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                onClick={handleSearchSubmit}
              >
                <FunnelIcon className="h-5 w-5 mr-2" />
                搜索
              </button>
            </div>
          </div>
        </div>

        {/* 用户数据表格 */}
        {loading ? (
          <div className="text-center py-10">加载中...</div>
        ) : (
          <>
            {renderUsersTable()}
            <PaginationBar />
          </>
        )}
      </div>

      {/* 详情模态框 */}
      <DetailModal />

      {/* 通知组件 */}
      <Notification />
    </div>
  );
};

export default StoreManagement;