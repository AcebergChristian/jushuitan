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
  XMarkIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import { apiRequest } from '../utils/api';

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [newUser, setNewUser] = useState({ 
    username: '', 
    email: '', 
    role: 'sales', 
    is_active: true,
    good_id: null 
  });

  // 分页相关状态
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [pageSize, setPageSize] = useState(10);


  const [activeTab, setActiveTab] = useState(0);


  // 提示消息状态
  const [notification, setNotification] = useState({ show: false, message: '', type: '' });
  // 显示通知的函数
  const showNotification = (message, type = 'success') => {
    setNotification({ show: true, message, type });
    setTimeout(() => {
      setNotification({ show: false, message: '', type: '' });
    }, 3000);
  };

  useEffect(() => {
    fetchUsers();
  }, [currentPage, pageSize, searchTerm]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      // 构建查询参数
      const params = new URLSearchParams({
        skip: (currentPage - 1) * pageSize,
        limit: pageSize
      });
      if (searchTerm) {
        params.append('search', searchTerm);
      }
      
      const response = await apiRequest(`/users?${params.toString()}`);
      if (response && response.ok) {
        const data = await response.json();
        // 假设后端返回的是数组，这里简单处理
        // 如果后端返回包含分页信息的对象，需要相应调整
        setUsers(Array.isArray(data) ? data : []);
        // 这里假设后端返回分页信息，暂时模拟总数
        // 实际上后端可能需要返回 { users: [...], total: count, totalPages: count/pageSize }
        setTotalItems(data.length); // 这里应该是实际总数，需后端配合
      } else if(response) {
        console.error('获取用户列表失败:', response.statusText);
      }
    } catch (error) {
      console.error('获取用户列表错误:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!isModalOpen) {
      setEditingUser(null);
      setNewUser({ 
        username: '', 
        email: '', 
        role: 'sales', 
        is_active: true,
        good_id: null 
      });
    }
  }, [isModalOpen]);

  const filteredUsers = users.filter(user =>
    user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.role?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // 处理分页
  const handlePageChange = (page) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  const handlePageSizeChange = (size) => {
    setPageSize(parseInt(size));
    setCurrentPage(1); // 更改页面大小时回到第一页
  };

  const handleSaveUser = async () => {
    try {
      let response;
      if (editingUser) {
        // 更新现有用户
        response = await apiRequest(`/users/${editingUser.id}`, {
          method: 'PUT',
          body: JSON.stringify({
            username: editingUser.username,
            email: editingUser.email,
            is_active: editingUser.is_active,
            role: editingUser.role,
            good_id: editingUser.good_id
          }),
        });
      } else {
        // 添加新用户
        response = await apiRequest('/users/', {
          method: 'POST',
          body: JSON.stringify({
            username: newUser.username,
            email: newUser.email,
            password: 'defaultpassword', // 实际应用中应通过安全方式设置密码
            is_active: newUser.is_active,
            role: newUser.role,
            good_id: newUser.good_id
          }),
        });
      }

      if (response && response.ok) {
        const savedUser = await response.json();
        if (editingUser) {
          setUsers(users.map(user => user.id === editingUser.id ? savedUser : user));
        } else {
          // 重新获取用户列表以反映最新的分页
          fetchUsers();
        }
        setIsModalOpen(false);
      } else if(response){
        console.error('保存用户失败:', response);
        showNotification( response.statusText, 'error');
        // alert('保存用户失败');
      }
    } catch (error) {
      console.error('保存用户错误:', error);
      showNotification( error, 'error');
      // alert('保存用户时发生错误');
    }
  };

  const handleEditUser = (user) => {
    setEditingUser({ ...user });
    setIsModalOpen(true);
  };

  const handleDeleteUser = async (id) => {
    if (window.confirm('确定要删除这个用户吗？')) {
      try {
        const response = await apiRequest(`/users/${id}`, {
          method: 'DELETE',
        });
        
        if (response && response.ok) {
          // 删除后重新获取用户列表
          fetchUsers();
        } else if(response){
          console.error('删除用户失败:', response.statusText);
          showNotification( response.statusText, 'error');
        }
      } catch (error) {
        console.error('删除用户错误:', error);
        showNotification( error, 'error');
      }
    }
  };

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case true:
        return 'bg-green-100 text-green-800';
      case false:
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getRoleBadgeClass = (role) => {
    switch (role) {
      case 'admin':
        return 'bg-purple-100 text-purple-800';
      case 'manager':
        return 'bg-blue-100 text-blue-800';
      case 'sales':
        return 'bg-yellow-100 text-yellow-800';
      case 'user':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const renderUsersTable = () => (
    <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 rounded-lg">
      <table className="min-w-full divide-y divide-gray-300">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">用户名</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">邮箱</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">角色</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">关联商品ID</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">创建时间</th>
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {filteredUsers.length > 0 ? (
            filteredUsers.map((user) => (
              <tr key={user.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{user.username}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{user.email}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRoleBadgeClass(user.role)}`}>
                    {user.role || 'user'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{user.good_id || '-'}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadgeClass(user.is_active)}`}>
                    {user.is_active ? '激活' : '未激活'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{user.created_at}</td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <div className="flex justify-end space-x-2">
                    <button 
                      className="text-blue-600 hover:text-blue-900"
                      onClick={() => handleEditUser(user)}
                    >
                      <PencilIcon className="h-5 w-5" />
                    </button>
                    <button 
                      className="text-red-600 hover:text-red-900"
                      onClick={() => handleDeleteUser(user.id)}
                    >
                      <TrashIcon className="h-5 w-5" />
                    </button>
                  </div>
                </td>
              </tr>
            ))
          ) : loading ? (
            <tr>
              <td colSpan={7} className="px-6 py-4 text-center text-sm text-gray-500">
                加载中...
              </td>
            </tr>
          ) : (
            <tr>
              <td colSpan={7} className="px-6 py-4 text-center text-sm text-gray-500">
                暂无用户数据
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );

  // 分页栏组件
  const PaginationBar = () => (
    <div className="flex items-center justify-between border-t border-gray-200 bg-white px-4 py-3 sm:px-6">
      <div className="flex flex-1 justify-between sm:hidden">
        <button
          onClick={() => handlePageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className={`relative inline-flex items-center rounded-md border px-4 py-2 text-sm font-medium ${
            currentPage === 1
              ? 'cursor-not-allowed border-gray-300 bg-gray-100 text-gray-400'
              : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
          }`}
        >
          上一页
        </button>
        <button
          onClick={() => handlePageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className={`relative ml-3 inline-flex items-center rounded-md border px-4 py-2 text-sm font-medium ${
            currentPage === totalPages
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
          <div className="flex items-center space-x-2 mb-4 ">
            <label htmlFor="page-size" className="text-sm text-gray-700">每页显示:</label>
            <select
              id="page-size"
              value={pageSize}
              onChange={(e) => handlePageSizeChange(e.target.value)}
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
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
              className={`relative inline-flex items-center rounded-l-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 ${
                currentPage === 1 ? 'cursor-not-allowed opacity-50' : ''
              }`}
            >
              <span className="sr-only">上一页</span>
              <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fillRule="evenodd" d="M12.79 5.23a.75.75 0 01-.02 1.06L8.832 10l3.938 3.71a.75.75 0 11-1.04 1.08l-4.5-4.25a.75.75 0 010-1.08l4.5-4.25a.75.75 0 011.06.02z" clipRule="evenodd" />
              </svg>
            </button>

            {/* 页码按钮 */}
            {[...Array(Math.min(5, totalPages))].map((_, i) => {
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
                    onClick={() => handlePageChange(pageNum)}
                    className={`relative inline-flex items-center px-4 py-2 text-sm font-semibold ${
                      currentPage === pageNum
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
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
              className={`relative inline-flex items-center rounded-r-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 ${
                currentPage === totalPages ? 'cursor-not-allowed opacity-50' : ''
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


  // 渲染通知组件
  const Notification = () => {
    if (!notification.show) return null;
    
    const bgColor = notification.type === 'error' ? 'bg-red-500' : 'bg-green-500';
    
    return (
      <div className="fixed top-4 right-4 z-50">
        <div className={`${bgColor} text-white px-6 py-4 rounded-lg shadow-lg flex items-center`}>
          <span>{notification.message}</span>
          <button 
            onClick={() => setNotification({ show: false, message: '', type: '' })}
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
          <h1 className="text-3xl font-bold text-gray-900">用户管理</h1>
          <p className="mt-2 text-gray-600">管理用户账户和用户之间的关系</p>
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
                  className="block w-full pl-10 pr-12 py-2.5 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                  placeholder="搜索用户或关系..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>
            <div className="flex space-x-3">
              {/* <button className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                <FunnelIcon className="h-5 w-5 mr-2" />
                筛选
              </button> */}
              <button 
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
                onClick={() => setIsModalOpen(true)}
              >
                <PlusIcon className="h-5 w-5 mr-2" />
                新增用户
              </button>
              {/* <button className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                <ArrowDownTrayIcon className="h-5 w-5 mr-2" />
                导出
              </button> */}
            </div>
          </div>
        </div>

        {/* 选项卡 */}
        <div className="bg-white rounded-xl shadow overflow-hidden">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex">
              <button
                className={`py-4 px-6 text-center border-b-2 font-medium text-sm ${
                  activeTab === 0
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                用户管理
              </button>
            </nav>
          </div>

          <div className="p-6">
            {renderUsersTable()}
            <PaginationBar />
          </div>
        </div>
      </div>


      {/* 通知组件 */}
      <Notification />

      {/* 用户编辑/新增模态框 */}
      <Transition appear show={isModalOpen} as={Fragment}>
        <Dialog as="div" className="relative z-10" onClose={() => setIsModalOpen(false)}>
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
                <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                  <Dialog.Title
                    as="h3"
                    className="text-lg font-medium leading-6 text-gray-900 border-b pb-3"
                  >
                    {editingUser ? '编辑用户' : '新增用户'}
                  </Dialog.Title>
                  
                  <div className="mt-4 space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">用户名</label>
                      <input
                        type="text"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        value={editingUser ? editingUser.username : newUser.username}
                        onChange={(e) => 
                          editingUser 
                            ? setEditingUser({...editingUser, username: e.target.value}) 
                            : setNewUser({...newUser, username: e.target.value})
                        }
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">邮箱</label>
                      <input
                        type="email"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        value={editingUser ? editingUser.email : newUser.email}
                        onChange={(e) => 
                          editingUser 
                            ? setEditingUser({...editingUser, email: e.target.value}) 
                            : setNewUser({...newUser, email: e.target.value})
                        }
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">角色</label>
                      <select
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        value={editingUser ? editingUser.role : newUser.role}
                        onChange={(e) => 
                          editingUser 
                            ? setEditingUser({...editingUser, role: e.target.value}) 
                            : setNewUser({...newUser, role: e.target.value})
                        }
                      >
                        <option value="user">普通用户</option>
                        <option value="sales">销售人员</option>
                        <option value="manager">经理</option>
                        <option value="admin">管理员</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">关联商品ID</label>
                      <input
                        type="number"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        placeholder="可选，留空表示不关联"
                        value={editingUser ? editingUser.good_id || '' : newUser.good_id || ''}
                        onChange={(e) => 
                          editingUser 
                            ? setEditingUser({...editingUser, good_id: e.target.value ? parseInt(e.target.value) : null}) 
                            : setNewUser({...newUser, good_id: e.target.value ? parseInt(e.target.value) : null})
                        }
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">状态</label>
                      <select
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        value={editingUser ? editingUser.is_active : newUser.is_active}
                        onChange={(e) => 
                          editingUser 
                            ? setEditingUser({...editingUser, is_active: e.target.value === 'true'}) 
                            : setNewUser({...newUser, is_active: e.target.value === 'true'})
                        }
                      >
                        <option value="true">激活</option>
                        <option value="false">未激活</option>
                      </select>
                    </div>
                  </div>

                  <div className="mt-6 flex justify-end space-x-3">
                    <button
                      type="button"
                      className="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                      onClick={() => setIsModalOpen(false)}
                    >
                      取消
                    </button>
                    <button
                      type="button"
                      className="inline-flex justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                      onClick={handleSaveUser}
                    >
                      保存
                    </button>
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </Dialog>
      </Transition>
    </div>
  );
};

export default UserManagement;