import React, { useState, useEffect } from 'react';
import { Tab } from '@headlessui/react';
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

const DataManagement = () => {
  const [activePlatformTab, setActivePlatformTab] = useState(0); // 0: 聚水潭, 1: 拼多多
  const [productType, setProductType] = useState('regular'); // 'regular': 常规商品, 'cancelled': 已取消
  const [searchTerm, setSearchTerm] = useState('');
  const [jushuitanData, setJushuitanData] = useState([]);
  const [pinduoduoData, setPinduoduoData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [totalItems, setTotalItems] = useState(0);

  // 添加筛选状态
  const [filters, setFilters] = useState({});

  // 分页相关状态
  const [showNotification, setShowNotification] = useState({ show: false, message: '', type: '' });

  // 显示通知
  const showNotificationFunc = (message, type = 'success') => {
    setShowNotification({ show: true, message, type });
    setTimeout(() => {
      setShowNotification({ show: false, message: '', type: '' });
    }, 3000);
  };


  // 获取聚水潭数据
  const fetchJushuitanData = async (page = 1, size = 10, search = '') => {
    setLoading(true);
    try {
      const skip = (page - 1) * size;
      const limit = size;

      let url = `/jushuitan_products/?skip=${skip}&limit=${limit}`;
      if (search) {
        // 不使用encodeURIComponent，直接传递搜索词
        url += `&search=${search}`;
      }

      if (productType === 'cancelled') {
        // 获取已取消的数据
        // 注意：这里需要后端也要提供类似的接口
        url = `/jushuitan_products/type/cancel?skip=${skip}&limit=${limit}`;
        if (search) {
          url += `&search=${search}`;
        }
      }

      const response = await apiRequest(url);

      if (response.ok) {
        const responseData = await response.json();
        // 适配后端返回的新格式 {data: [...], total: count, ...}
        setJushuitanData(responseData.data || responseData); // 如果后端没有包装在data字段中，则直接使用responseData
        setTotalItems(responseData.total || responseData.length);
      } else {
        console.error('获取聚水潭数据失败:', response.statusText);
        showNotificationFunc('获取聚水潭数据失败', 'error');
      }
    } catch (error) {
      console.error('获取聚水潭数据错误:', error);
      showNotificationFunc('获取聚水潭数据时发生错误', 'error');
    } finally {
      setLoading(false);
    }
  };

  // 同步聚水潭数据
  const syncJushuitanData = async () => {
    setLoading(true);
    try {
      const response = await apiRequest('/sync_jushuitan_data', {
        method: 'POST'
      });

      if (response.ok) {
        const result = await response.json();
        showNotificationFunc(result.message || '数据同步成功', 'success');

        // 同步完成后重新获取数据，保持当前的分页状态
        fetchJushuitanData(currentPage, pageSize, searchTerm);
      } else {
        const errorData = await response.json().catch(() => ({}));
        showNotificationFunc(errorData.detail || '数据同步失败', 'error');
      }
    } catch (error) {
      console.error('同步数据错误:', error);
      showNotificationFunc('同步数据时发生错误', 'error');
    } finally {
      setLoading(false);
    }
  };

  // 获取拼多多数据
  const fetchPinduoduoData = async () => {
    setLoading(true);
    try {
      // 暂时使用模拟数据，后续需要根据实际API实现
      const mockData = [
        { id: 'ORD-001254', customer: '张三', date: '2024-01-15', amount: 15998, status: 'completed', platform: '拼多多' },
        { id: 'ORD-001255', customer: '李四', date: '2024-01-15', amount: 8999, status: 'processing', platform: '拼多多' },
        { id: 'ORD-001256', customer: '王五', date: '2024-01-14', amount: 7999, status: 'pending', platform: '拼多多' },
        { id: 'ORD-001257', customer: '赵六', date: '2024-01-14', amount: 21997, status: 'completed', platform: '拼多多' },
        { id: 'ORD-001258', customer: '钱七', date: '2024-01-13', amount: 1899, status: 'cancelled', platform: '拼多多' },
      ];
      setPinduoduoData(mockData);
    } catch (error) {
      console.error('获取拼多多数据错误:', error);
      showNotificationFunc('获取拼多多数据时发生错误', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activePlatformTab === 0) { // 聚水潭
      fetchJushuitanData(currentPage, pageSize, searchTerm);
    } else { // 拼多多
      fetchPinduoduoData(currentPage, pageSize, searchTerm);
    }
  }, [activePlatformTab, productType, currentPage, pageSize]);

  // 处理搜索框变化
  const handleSearchChange = (e) => {
    const value = e.target.value;
    setSearchTerm(value);

    // 如果搜索框清空，恢复初始数据
    if (!value) {
      if (activePlatformTab === 0) {
        fetchJushuitanData(currentPage, pageSize, '');
      } else {
        fetchPinduoduoData(currentPage, pageSize, '');
      }
    }
  };

  // 点击筛选按钮，触发查询
  const handleFilterClick = () => {
    if (activePlatformTab === 0) {
      fetchJushuitanData(currentPage, pageSize, searchTerm);
    } else {
      fetchPinduoduoData(currentPage, pageSize, searchTerm);
    }
  };


  const filteredPinduoduoData = pinduoduoData.filter(item =>
    item.id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.customer?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'low-stock':
        return 'bg-yellow-100 text-yellow-800';
      case 'out-of-stock':
        return 'bg-red-100 text-red-800';
      case 'processing':
        return 'bg-blue-100 text-blue-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'cancelled':
        return 'bg-gray-100 text-gray-800';
      case 'inactive':
        return 'bg-gray-100 text-gray-800';
      case 'vip':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // 删除聚水潭数据
  const deleteJushuitanRecord = async (id) => {
    if (window.confirm('确定要删除这条记录吗？')) {
      try {
        const response = await apiRequest(`/jushuitan_products/${id}`, {
          method: 'DELETE'
        });

        if (response.ok) {
          // 重新获取数据
          fetchJushuitanData();
          showNotificationFunc('记录删除成功', 'success');
        } else {
          console.error('删除记录失败:', response.statusText);
          showNotificationFunc('删除记录失败', 'error');
        }
      } catch (error) {
        console.error('删除记录错误:', error);
        showNotificationFunc('删除记录时发生错误', 'error');
      }
    }
  };

  // 动态渲染表格
  const renderDynamicTable = (data, type) => {
    if (data.length === 0) {
      return (
        <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 rounded-lg">
          <table className="min-w-full divide-y divide-gray-300">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  暂无数据
                </th>
              </tr>
            </thead>
          </table>
        </div>
      );
    }

    // 获取所有可能的字段名（从第一条记录获取）
    const allKeys = Object.keys(data[0]);

    // 移除一些不需要显示的字段（例如 is_del）
    const displayKeys = allKeys.filter(key => key !== 'is_del');

    return (
      <div className="shadow ring-1 ring-black ring-opacity-5 rounded-lg">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-300">
            <thead className="bg-gray-50">
              <tr>
                {displayKeys.map((key, index) => (
                  <th key={index} className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[100px]">
                    {key}
                  </th>
                ))}
                <th className="px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[100px] sticky right-0 bg-gray-50 z-20 shadow-md">
                  操作
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data.map((item, rowIndex) => (
                <tr key={item.id || rowIndex} className="hover:bg-gray-50">
                  {displayKeys.map((key, colIndex) => (
                    <td key={colIndex} className="px-3 py-2 text-sm text-gray-900 max-w-xs break-words">
                      {(() => {
                        const value = item[key];

                        // 处理各种特殊字段
                        if (key === 'status' || key === 'platform' || key === 'isSuccess' || key === 'orderStatus' || key === 'orderType') {
                          return (
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadgeClass(value)}`}>
                              {value !== null && value !== undefined && value !== '' ?
                                String(value) : '-'}
                            </span>
                          );
                        }
                        // 处理 disInnerOrderGoodsViewList 特殊字段
                        else if (key === 'disInnerOrderGoodsViewList') {
                          if (typeof value === 'string' && value.trim().startsWith('[')) {
                            try {
                              // 将Python格式的字符串转换为JSON格式
                              let processedValue = value
                                .replace(/'/g, '"')  // 将单引号替换为双引号
                                .replace(/\bNone\b/g, 'null')  // 将None替换为null
                                .replace(/\bTrue\b/g, 'true')  // 将True替换为true
                                .replace(/\bFalse\b/g, 'false'); // 将False替换为false

                              const parsedValue = JSON.parse(processedValue);

                              if (Array.isArray(parsedValue) && parsedValue.length > 0) {
                                return (
                                  <div className="space-y-2">
                                    {parsedValue.map((obj, idx) => (
                                      <div key={idx} className="border border-gray-200 rounded p-2">
                                        {obj.supplierName && <div><strong>供应商:</strong> {obj.supplierName}</div>}
                                        {obj.pic && <div><strong>图片:</strong> <a href={obj.pic} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">查看</a></div>}
                                        {obj.itemCode && <div><strong>商品编码:</strong> {obj.itemCode}</div>}
                                        {obj.itemName && <div><strong>商品名称:</strong> <span className="font-bold text-blue-600">{obj.itemName}</span></div>}
                                        {obj.itemCount !== undefined && obj.itemCount !== null && <div><strong>数量:</strong> {obj.itemCount}</div>}
                                        {obj.properties && <div><strong>规格:</strong> {obj.properties}</div>}
                                        {obj.price !== undefined && obj.price !== null && <div><strong>单价:</strong> ¥{obj.price}</div>}
                                        {obj.totalPrice !== undefined && obj.totalPrice !== null && <div><strong>总价:</strong> ¥{obj.totalPrice}</div>}
                                      </div>
                                    ))}
                                  </div>
                                );
                              } else {
                                return '-';
                              }
                            } catch (e) {
                              return value.length > 50 ? (
                                <div className="group relative">
                                  <div className="truncate">{value.substring(0, 50)}...</div>
                                  <div className="absolute hidden group-hover:block bg-gray-800 text-white text-xs p-2 rounded z-10 max-w-xs break-words">
                                    {value}
                                  </div>
                                </div>
                              ) : value;
                            }
                          } else if (Array.isArray(value) && value.length > 0) {
                            // 如果已经是数组
                            return (
                              <div className="space-y-2">
                                {value.map((obj, idx) => (
                                  <div key={idx} className="border border-gray-200 rounded p-2">
                                    {obj.supplierName && <div><strong>供应商:</strong> {obj.supplierName}</div>}
                                    {obj.pic && <div><strong>图片:</strong> <a href={obj.pic} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">查看</a></div>}
                                    {obj.itemCode && <div><strong>商品编码:</strong> {obj.itemCode}</div>}
                                    {obj.itemName && <div><strong>商品名称:</strong> <span className="font-bold text-blue-600">{obj.itemName}</span></div>}
                                    {obj.itemCount !== undefined && obj.itemCount !== null && <div><strong>数量:</strong> {obj.itemCount}</div>}
                                    {obj.properties && <div><strong>规格:</strong> {obj.properties}</div>}
                                    {obj.price !== undefined && obj.price !== null && <div><strong>单价:</strong> ¥{obj.price}</div>}
                                    {obj.totalPrice !== undefined && obj.totalPrice !== null && <div><strong>总价:</strong> ¥{obj.totalPrice}</div>}
                                  </div>
                                ))}
                              </div>
                            );
                          } else {
                            return '-';
                          }
                        }
                        // 处理金额类字段
                        else if (['price', 'amount', 'totalSpent', 'purchaseAmt', 'totalAmt', 'commission', 'freight', 'payAmount',
                          'discountAmt', 'paidAmount', 'totalPurchasePriceGoods', 'smallProgramFreight',
                          'totalTransactionPurchasePrice', 'smallProgramCommission', 'smallProgramPaidAmount',
                          'clientPaidAmt', 'goodsAmt', 'freeAmount', 'drpAmount'].includes(key)) {
                          return value ? `¥${parseFloat(value).toLocaleString()}` : '-';
                        }
                        // 处理布尔值字段
                        else if (typeof value === 'boolean') {
                          return value ? '是' : '否';
                        }
                        // 处理数字字段（非金额）
                        else if (typeof value === 'number' && !['price', 'amount', 'totalSpent', 'purchaseAmt', 'totalAmt', 'commission', 'freight', 'payAmount',
                          'discountAmt', 'paidAmount', 'totalPurchasePriceGoods', 'smallProgramFreight',
                          'totalTransactionPurchasePrice', 'smallProgramCommission', 'smallProgramPaidAmount',
                          'clientPaidAmt', 'goodsAmt', 'freeAmount', 'drpAmount'].includes(key)) {
                          return value;
                        }
                        // 处理JSON字符串或数组字符串
                        else if (typeof value === 'string' && (value.trim().startsWith('[') || value.trim().startsWith('{'))) {
                          try {
                            let parsedValue;
                            // 检查是否为Python格式的字符串（包含单引号和None/True/False）
                            if (value.includes("'") || value.includes("None") || value.includes("True") || value.includes("False")) {
                              let processedValue = value.replace(/'/g, '"')
                                .replace(/None/g, 'null')
                                .replace(/True/g, 'true')
                                .replace(/False/g, 'false');
                              parsedValue = JSON.parse(processedValue);
                            } else {
                              parsedValue = JSON.parse(value);
                            }

                            // 如果是数组
                            if (Array.isArray(parsedValue)) {
                              if (parsedValue.length === 0) {
                                return '-';
                              }

                              // 如果是简单数组（如标签数组），显示为标签
                              if (parsedValue.length > 0 && typeof parsedValue[0] === 'string') {
                                return (
                                  <div className="flex flex-wrap gap-1">
                                    {parsedValue.map((val, idx) => (
                                      <span key={idx} className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                        {val}
                                      </span>
                                    ))}
                                  </div>
                                );
                              }
                              // 如果是复杂对象数组，显示第一个对象的部分字段
                              else if (parsedValue.length > 0 && typeof parsedValue[0] === 'object' && parsedValue[0] !== null) {
                                return (
                                  <div className="space-y-1">
                                    {parsedValue.slice(0, 3).map((obj, idx) => {
                                      if (obj.itemName) {
                                        return (
                                          <div key={idx} className="break-all">
                                            商品: {obj.itemName} ({obj.itemCount}件)
                                          </div>
                                        );
                                      } else if (obj.receiverName) {
                                        return (
                                          <div key={idx} className="break-all">
                                            收件人: {obj.receiverName}
                                          </div>
                                        );
                                      } else {
                                        // 提取对象的主要字段
                                        const fields = [];
                                        if (obj.itemName) fields.push(`商品: ${obj.itemName}`);
                                        if (obj.receiverName) fields.push(`收件人: ${obj.receiverName}`);
                                        if (obj.price) fields.push(`价格: ¥${obj.price}`);
                                        if (obj.totalPrice) fields.push(`总价: ¥${obj.totalPrice}`);
                                        if (obj.itemCount) fields.push(`数量: ${obj.itemCount}`);

                                        return (
                                          <div key={idx} className="break-all">
                                            {fields.length > 0 ? fields.join(', ') : JSON.stringify(obj)}
                                          </div>
                                        );
                                      }
                                    })}
                                    {parsedValue.length > 3 && (
                                      <div className="text-xs text-gray-500">...还有{parsedValue.length - 3}项</div>
                                    )}
                                  </div>
                                );
                              }
                            }
                            // 如果是对象
                            else if (typeof parsedValue === 'object' && parsedValue !== null) {
                              // 特定对象类型的处理
                              if (parsedValue.ReceiverName || parsedValue.ReceiverPhone || parsedValue.ReceiverAddress) {
                                return (
                                  <div className="space-y-1">
                                    {parsedValue.ReceiverName && <div className="break-all">姓名: {parsedValue.ReceiverName}</div>}
                                    {parsedValue.ReceiverPhone && <div className="break-all">电话: {parsedValue.ReceiverPhone}</div>}
                                    {parsedValue.ReceiverAddress && <div className="break-all">地址: {parsedValue.ReceiverAddress}</div>}
                                  </div>
                                );
                              } else if (parsedValue.receiver_name || parsedValue.receiver_phone || parsedValue.receiver_address) {
                                return (
                                  <div className="space-y-1">
                                    {parsedValue.receiver_name && <div className="break-all">姓名: {parsedValue.receiver_name}</div>}
                                    {parsedValue.receiver_phone && <div className="break-all">电话: {parsedValue.receiver_phone}</div>}
                                    {parsedValue.receiver_address && <div className="break-all">地址: {parsedValue.receiver_address}</div>}
                                  </div>
                                );
                              } else {
                                return (
                                  <div className="break-all">
                                    {JSON.stringify(parsedValue)}
                                  </div>
                                );
                              }
                            }
                          } catch (e) {
                            // 如果解析失败，按普通字符串显示
                            return value.length > 50 ? (
                              <div className="group relative">
                                <div className="truncate">{value.substring(0, 50)}...</div>
                                <div className="absolute hidden group-hover:block bg-gray-800 text-white text-xs p-2 rounded z-10 max-w-xs break-words">
                                  {value}
                                </div>
                              </div>
                            ) : value;
                          }
                        }
                        // 处理日期时间字段
                        else if (key.includes('Time') || key.includes('Date') || key.includes('created_at') || key.includes('updated_at')) {
                          return value ? new Date(value).toLocaleString() : '-';
                        }
                        // 处理普通字符串
                        else if (typeof value === 'string') {
                          if (value === '') {
                            return '-';
                          }
                          return value.length > 50 ? (
                            <div className="group relative">
                              <div className="truncate">{value.substring(0, 50)}...</div>
                              <div className="absolute hidden group-hover:block bg-gray-800 text-white text-xs p-2 rounded z-10 max-w-xs break-words">
                                {value}
                              </div>
                            </div>
                          ) : value;
                        }
                        // 处理null, undefined等
                        else if (value === null || value === undefined) {
                          return '-';
                        }
                        // 其他情况
                        else {
                          return String(value);
                        }
                      })()}
                    </td>
                  ))}
                  <td className="px-3 py-2 whitespace-nowrap text-right text-sm font-medium sticky right-0 bg-white z-10 shadow-md">
                    <div className="flex justify-end space-x-2">
                      <button className="text-blue-600 hover:text-blue-900">
                        <EyeIcon className="h-5 w-5" />
                      </button>
                      <button className="text-green-600 hover:text-green-900">
                        <PencilIcon className="h-5 w-5" />
                      </button>
                      <button
                        className="text-red-600 hover:text-red-900"
                        onClick={() => type === 'jushuitan' ? deleteJushuitanRecord(item.id) : null}
                      >
                        <TrashIcon className="h-5 w-5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
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
          <h1 className="text-3xl font-bold text-gray-900">数据管理</h1>
          <p className="mt-2 text-gray-600">聚水潭数据 | 拼多多数据</p>
        </div>

        {/* 平台选项卡 */}
        <div className="bg-white rounded-xl shadow p-6 mb-6">
          <Tab.Group selectedIndex={activePlatformTab} onChange={setActivePlatformTab}>
            <Tab.List className="flex space-x-1 rounded-xl bg-blue-100 p-1 mb-6">
              <Tab
                className={({ selected }) =>
                  `w-full rounded-lg py-3 text-sm font-medium leading-5
                  ${selected
                    ? 'bg-white shadow text-blue-700 outline-none'
                    : 'text-blue-500 hover:bg-white/[0.12] hover:text-blue-700'}`
                }
              >
                聚水潭
              </Tab>
              <Tab
                className={({ selected }) =>
                  `w-full rounded-lg py-3 text-sm font-medium leading-5
                  ${selected
                    ? 'bg-white shadow text-blue-700 outline-none'
                    : 'text-blue-500 hover:bg-white/[0.12] hover:text-blue-700'}`
                }
              >
                拼多多
              </Tab>
            </Tab.List>
            <Tab.Panels>
              <Tab.Panel>
                {/* 聚水潭平台内容 */}
                <div className="space-y-6">
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
                            placeholder="搜索商品..."
                            value={searchTerm}
                            onChange={handleSearchChange}
                          />
                        </div>
                      </div>
                      <div className="flex space-x-3">
                        <button
                          className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                          onClick={handleFilterClick}
                        >
                          <FunnelIcon className="h-5 w-5 mr-2" />
                          筛选
                        </button>
                        <button
                          className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                          onClick={syncJushuitanData}
                        >
                          <ArrowDownTrayIcon className="h-5 w-5 mr-2" />
                          同步
                        </button>
                        {/* <button className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg text-sm font-medium text-white bg-blue-600 hover:bg-blue-700">
                          <PlusIcon className="h-5 w-5 mr-2" />
                          新建
                        </button> */}
                      </div>
                    </div>
                  </div>

                  {/* 商品类型切换 */}
                  <div className="bg-white rounded-xl shadow p-6 mb-6">
                    <div className="flex items-center space-x-4">
                      <span className="text-sm font-medium text-gray-700">数据类型:</span>
                      <div className="flex space-x-2">
                        <button
                          className={`px-4 py-2 text-sm rounded-lg ${productType === 'regular'
                              ? 'bg-blue-600 text-white'
                              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                            }`}
                          onClick={() => setProductType('regular')}
                        >
                          常规数据
                        </button>
                        <button
                          className={`px-4 py-2 text-sm rounded-lg ${productType === 'cancelled'
                              ? 'bg-blue-600 text-white'
                              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                            }`}
                          onClick={() => setProductType('cancelled')}
                        >
                          已取消
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* 商品数据表格 */}
                  {loading ? (
                    <div className="text-center py-10">加载中...</div>
                  ) : (
                    <>
                      {renderDynamicTable(jushuitanData, 'jushuitan')}
                      <PaginationBar />
                    </>
                  )}
                </div>
              </Tab.Panel>
              <Tab.Panel>
                {/* 拼多多平台内容 */}
                <div className="space-y-6">
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
                            placeholder="搜索订单..."
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
                        {/* <button className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg text-sm font-medium text-white bg-blue-600 hover:bg-blue-700">
                          <PlusIcon className="h-5 w-5 mr-2" />
                          新建
                        </button> */}
                      </div>
                    </div>
                  </div>

                  {/* 订单数据表格 */}
                  {loading ? (
                    <div className="text-center py-10">加载中...</div>
                  ) : (
                    renderDynamicTable(filteredPinduoduoData, 'pinduoduo')
                  )}
                </div>
              </Tab.Panel>
            </Tab.Panels>
          </Tab.Group>
        </div>
      </div>

      {/* 通知组件 */}
      <Notification />
    </div>
  );
};

export default DataManagement;