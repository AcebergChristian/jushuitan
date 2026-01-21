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

  const [relations, setRelations] = useState([
    { id: 1, user: '张三', relatedUser: '李四', relationType: '同事', createdDate: '2024-01-01' },
    { id: 2, user: '王五', relatedUser: '赵六', relationType: '上级', createdDate: '2024-01-05' },
    { id: 3, user: '李四', relatedUser: '钱七', relationType: '下属', createdDate: '2024-01-08' },
  ]);

  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await apiRequest('/users/');
      if (response && response.ok) {
        const data = await response.json();
        setUsers(data);
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

  const filteredRelations = relations.filter(relation =>
    relation.user.toLowerCase().includes(searchTerm.toLowerCase()) ||
    relation.relatedUser.toLowerCase().includes(searchTerm.toLowerCase()) ||
    relation.relationType.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
          setUsers([...users, savedUser]);
        }
        setIsModalOpen(false);
      } else if(response){
        console.error('保存用户失败:', response.statusText);
        alert('保存用户失败');
      }
    } catch (error) {
      console.error('保存用户错误:', error);
      alert('保存用户时发生错误');
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
          setUsers(users.filter(user => user.id !== id));
        } else if(response){
          console.error('删除用户失败:', response.statusText);
          alert('删除用户失败');
        }
      } catch (error) {
        console.error('删除用户错误:', error);
        alert('删除用户时发生错误');
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
              <button className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                <FunnelIcon className="h-5 w-5 mr-2" />
                筛选
              </button>
              <button 
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
                onClick={() => setIsModalOpen(true)}
              >
                <PlusIcon className="h-5 w-5 mr-2" />
                新增用户
              </button>
              <button className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                <ArrowDownTrayIcon className="h-5 w-5 mr-2" />
                导出
              </button>
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
                onClick={() => setActiveTab(0)}
              >
                用户管理
              </button>
              <button
                className={`py-4 px-6 text-center border-b-2 font-medium text-sm ${
                  activeTab === 1
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                onClick={() => setActiveTab(1)}
              >
                用户关系
              </button>
            </nav>
          </div>

          <div className="p-6">
            {activeTab === 0 && renderUsersTable()}
            {activeTab === 1 && renderRelationsTable()}
          </div>
        </div>
      </div>

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