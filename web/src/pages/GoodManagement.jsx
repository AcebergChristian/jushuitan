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

const GoodManagement = () => {
  const [goodsData, setGoodsData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [totalItems, setTotalItems] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [showNotification, setShowNotification] = useState({ show: false, message: '', type: '' });
  const [selectedGood, setSelectedGood] = useState(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);

  // 显示通知
  const showNotificationFunc = (message, type = 'success') => {
    setShowNotification({ show: true, message, type });
    setTimeout(() => {
      setShowNotification({ show: false, message: '', type: '' });
    }, 3000);
  };

  // 获取商品数据
  const fetchGoodsData = async (page = 1, size = 10, search = '') => {
    setLoading(true);
    try {
      const skip = (page - 1) * size;
      const limit = size;

      let url = `/goods/?skip=${skip}&limit=${limit}`;
      if (search) {
        url += `&search=${encodeURIComponent(search)}`;
      }

      const response = await apiRequest(url);

      if (response.ok) {
        const responseData = await response.json();
        setGoodsData(responseData.data || []);
        setTotalItems(responseData.total || 0);
      } else {
        console.error('获取商品数据失败:', response.statusText);
        showNotificationFunc('获取商品数据失败', 'error');
      }
    } catch (error) {
      console.error('获取商品数据错误:', error);
      showNotificationFunc('获取商品数据时发生错误', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGoodsData(currentPage, pageSize, searchTerm);
  }, [currentPage, pageSize]);

  // 处理搜索框变化
  const handleSearchChange = (e) => {
    const value = e.target.value;
    setSearchTerm(value);
  };

  // 处理搜索提交
  const handleSearchSubmit = () => {
    fetchGoodsData(currentPage, pageSize, searchTerm);
    setCurrentPage(1); // 搜索时回到第一页
  };

  // 查看商品详情
  const viewGoodDetails = (good) => {
    setSelectedGood(good);
    setIsDetailModalOpen(true);
  };


  // 同步商品数据
  const syncGoodsData = async () => {
    setLoading(true);
    try {
      const response = await apiRequest('/sync_goods/', {
        method: 'GET'
      });

      if (response.ok) {
        const result = await response.json();
        showNotificationFunc(result.message || '商品数据同步成功', 'success');
        
        // 同步完成后重新获取当前页的数据
        fetchGoodsData(currentPage, pageSize, searchTerm);
      } else {
        const errorData = await response.json().catch(() => ({}));
        showNotificationFunc(errorData.detail || '商品数据同步失败', 'error');
      }
    } catch (error) {
      console.error('同步商品数据错误:', error);
      showNotificationFunc('同步商品数据时发生错误', 'error');
    } finally {
      setLoading(false);
    }
  };




  // 渲染商品数据表格
  const renderGoodsTable = () => {
    if (goodsData.length === 0) {
      return (
        <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 rounded-lg">
          <table className="min-w-full divide-y divide-gray-300">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  暂无商品数据
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
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">商品ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">商品名称</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">店铺ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">店铺名称</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">订单ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">付款金额</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">销售金额</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">销售成本</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">毛一利润</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">毛一利润率</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">广告费</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">广告占比</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">毛三利润</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">毛三利润率</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">毛四利润</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">毛四利润率</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">净利润</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">净利率</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">创建时间</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">更新时间</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[120px]">操作</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {goodsData.map((item, index) => (
              <tr key={item.id || index} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.goods_id || '-'}</td>
                <td className="px-6 py-4 text-sm text-gray-900 max-w-xs break-words">{item.goods_name || '-'}</td>
                <td className="px-6 py-4 text-sm text-gray-900">{item.store_id || '-'}</td>
                <td className="px-6 py-4 text-sm text-gray-900">{item.store_name || '-'}</td>
                <td className="px-6 py-4 text-sm text-gray-900">{item.order_id || '-'}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">¥{(item.payment_amount || 0).toFixed(2)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">¥{(item.sales_amount || 0).toFixed(2)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">¥{(item.sales_cost || 0).toFixed(2)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">¥{(item.gross_profit_1_occurred || 0).toFixed(2)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{(item.gross_profit_1_rate || 0).toFixed(2)}%</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">¥{(item.advertising_expenses || 0).toFixed(2)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{(item.advertising_rate || 0).toFixed(2)}%</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">¥{(item.gross_profit_3 || 0).toFixed(2)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{(item.gross_profit_3_rate || 0).toFixed(2)}%</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">¥{(item.gross_profit_4 || 0).toFixed(2)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{(item.gross_profit_4_rate || 0).toFixed(2)}%</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">¥{(item.net_profit || 0).toFixed(2)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{(item.net_profit_rate || 0).toFixed(2)}%</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {item.created_at ? new Date(item.created_at).toLocaleDateString() : '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {item.updated_at ? new Date(item.updated_at).toLocaleDateString() : '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <div className="flex justify-end space-x-2">
                    <button 
                      className="text-blue-600 hover:text-blue-900"
                      onClick={() => viewGoodDetails(item)}
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
    if (!selectedGood) return null;

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
                <Dialog.Panel className="w-full max-w-4xl transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                  <Dialog.Title
                    as="h3"
                    className="text-lg font-medium leading-6 text-gray-900 border-b pb-3"
                  >
                    商品详情
                  </Dialog.Title>
                  
                  <div className="mt-4 max-h-96 overflow-y-auto">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <div className="flex">
                          <span className="w-32 text-sm font-medium text-gray-500">商品ID:</span>
                          <span className="text-sm text-gray-900">{selectedGood.goods_id || '-'}</span>
                        </div>
                        <div className="flex">
                          <span className="w-32 text-sm font-medium text-gray-500">商品名称:</span>
                          <span className="text-sm text-gray-900">{selectedGood.goods_name || '-'}</span>
                        </div>
                        <div className="flex">
                          <span className="w-32 text-sm font-medium text-gray-500">店铺ID:</span>
                          <span className="text-sm text-gray-900">{selectedGood.store_id || '-'}</span>
                        </div>
                        <div className="flex">
                          <span className="w-32 text-sm font-medium text-gray-500">店铺名称:</span>
                          <span className="text-sm text-gray-900">{selectedGood.store_name || '-'}</span>
                        </div>
                        <div className="flex">
                          <span className="w-32 text-sm font-medium text-gray-500">订单ID:</span>
                          <span className="text-sm text-gray-900">{selectedGood.order_id || '-'}</span>
                        </div>
                        <div className="flex">
                          <span className="w-32 text-sm font-medium text-gray-500">付款金额:</span>
                          <span className="text-sm text-gray-900">¥{(selectedGood.payment_amount || 0).toFixed(2)}</span>
                        </div>
                        <div className="flex">
                          <span className="w-32 text-sm font-medium text-gray-500">销售金额:</span>
                          <span className="text-sm text-gray-900">¥{(selectedGood.sales_amount || 0).toFixed(2)}</span>
                        </div>
                        <div className="flex">
                          <span className="w-32 text-sm font-medium text-gray-500">销售成本:</span>
                          <span className="text-sm text-gray-900">¥{(selectedGood.sales_cost || 0).toFixed(2)}</span>
                        </div>
                        <div className="flex">
                          <span className="w-32 text-sm font-medium text-gray-500">毛一利润:</span>
                          <span className="text-sm text-gray-900">¥{(selectedGood.gross_profit_1_occurred || 0).toFixed(2)}</span>
                        </div>
                        <div className="flex">
                          <span className="w-32 text-sm font-medium text-gray-500">毛一利润率:</span>
                          <span className="text-sm text-gray-900">{(selectedGood.gross_profit_1_rate || 0).toFixed(2)}%</span>
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        <div className="flex">
                          <span className="w-32 text-sm font-medium text-gray-500">广告费:</span>
                          <span className="text-sm text-gray-900">¥{(selectedGood.advertising_expenses || 0).toFixed(2)}</span>
                        </div>
                        <div className="flex">
                          <span className="w-32 text-sm font-medium text-gray-500">广告占比:</span>
                          <span className="text-sm text-gray-900">{(selectedGood.advertising_rate || 0).toFixed(2)}%</span>
                        </div>
                        <div className="flex">
                          <span className="w-32 text-sm font-medium text-gray-500">毛三利润:</span>
                          <span className="text-sm text-gray-900">¥{(selectedGood.gross_profit_3 || 0).toFixed(2)}</span>
                        </div>
                        <div className="flex">
                          <span className="w-32 text-sm font-medium text-gray-500">毛三利润率:</span>
                          <span className="text-sm text-gray-900">{(selectedGood.gross_profit_3_rate || 0).toFixed(2)}%</span>
                        </div>
                        <div className="flex">
                          <span className="w-32 text-sm font-medium text-gray-500">毛四利润:</span>
                          <span className="text-sm text-gray-900">¥{(selectedGood.gross_profit_4 || 0).toFixed(2)}</span>
                        </div>
                        <div className="flex">
                          <span className="w-32 text-sm font-medium text-gray-500">毛四利润率:</span>
                          <span className="text-sm text-gray-900">{(selectedGood.gross_profit_4_rate || 0).toFixed(2)}%</span>
                        </div>
                        <div className="flex">
                          <span className="w-32 text-sm font-medium text-gray-500">净利润:</span>
                          <span className="text-sm text-gray-900">¥{(selectedGood.net_profit || 0).toFixed(2)}</span>
                        </div>
                        <div className="flex">
                          <span className="w-32 text-sm font-medium text-gray-500">净利率:</span>
                          <span className="text-sm text-gray-900">{(selectedGood.net_profit_rate || 0).toFixed(2)}%</span>
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        <div className="flex">
                          <span className="w-32 text-sm font-medium text-gray-500">创建人:</span>
                          <span className="text-sm text-gray-900">{selectedGood.creator || '-'}</span>
                        </div>
                        <div className="flex">
                          <span className="w-32 text-sm font-medium text-gray-500">创建时间:</span>
                          <span className="text-sm text-gray-900">
                            {selectedGood.created_at ? new Date(selectedGood.created_at).toLocaleString() : '-'}
                          </span>
                        </div>
                        <div className="flex">
                          <span className="w-32 text-sm font-medium text-gray-500">更新时间:</span>
                          <span className="text-sm text-gray-900">
                            {selectedGood.updated_at ? new Date(selectedGood.updated_at).toLocaleString() : '-'}
                          </span>
                        </div>
                      </div>
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
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">商品管理</h1>
          <p className="mt-2 text-gray-600">管理商品信息及财务数据</p>
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
                  placeholder="搜索商品名称..."
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
              <button
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                onClick={syncGoodsData}
              >
                <ArrowDownTrayIcon className="h-5 w-5 mr-2" />
                同步
              </button>
            </div>
          </div>
        </div>

        {/* 商品数据表格 */}
        {loading ? (
          <div className="text-center py-10">加载中...</div>
        ) : (
          <>
            {renderGoodsTable()}
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

export default GoodManagement;