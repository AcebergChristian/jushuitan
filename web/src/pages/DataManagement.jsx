import React, { useState } from 'react';
import { Tab } from '@headlessui/react';
import { 
  MagnifyingGlassIcon, 
  FunnelIcon, 
  ArrowDownTrayIcon, 
  PlusIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon 
} from '@heroicons/react/24/outline';

const DataManagement = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');

  // 模拟数据
  const productData = [
    { id: 1, name: 'iPhone 15 Pro', sku: 'IP15P-128GB-NAT', price: 7999, stock: 42, status: 'active', platform: '聚水潭' },
    { id: 2, name: 'MacBook Air M2', sku: 'MBA-M2-256GB-SIL', price: 8999, stock: 18, status: 'active', platform: '拼多多' },
    { id: 3, name: 'iPad Pro 12.9', sku: 'IPADP-129-M2-256', price: 8599, stock: 25, status: 'low-stock', platform: '聚水潭' },
    { id: 4, name: 'AirPods Pro 2', sku: 'APOP2-WIRELESS-CASE', price: 1899, stock: 0, status: 'out-of-stock', platform: '拼多多' },
    { id: 5, name: 'Apple Watch Series 9', sku: 'AWS9-45MM-ALUM', price: 2999, stock: 37, status: 'active', platform: '聚水潭' },
  ];

  const orderData = [
    { id: 'ORD-001254', customer: '张三', date: '2024-01-15', amount: 15998, status: 'completed', platform: '聚水潭' },
    { id: 'ORD-001255', customer: '李四', date: '2024-01-15', amount: 8999, status: 'processing', platform: '拼多多' },
    { id: 'ORD-001256', customer: '王五', date: '2024-01-14', amount: 7999, status: 'pending', platform: '聚水潭' },
    { id: 'ORD-001257', customer: '赵六', date: '2024-01-14', amount: 21997, status: 'completed', platform: '拼多多' },
    { id: 'ORD-001258', customer: '钱七', date: '2024-01-13', amount: 1899, status: 'cancelled', platform: '聚水潭' },
  ];

  const customerData = [
    { id: 1, name: '张三', email: 'zhangsan@example.com', phone: '138****8888', orders: 24, totalSpent: 45680, status: 'active' },
    { id: 2, name: '李四', email: 'lisi@example.com', phone: '139****9999', orders: 12, totalSpent: 23450, status: 'active' },
    { id: 3, name: '王五', email: 'wangwu@example.com', phone: '137****7777', orders: 8, totalSpent: 15600, status: 'inactive' },
    { id: 4, name: '赵六', email: 'zhaoliu@example.com', phone: '136****6666', orders: 36, totalSpent: 78900, status: 'vip' },
    { id: 5, name: '钱七', email: 'qianqi@example.com', phone: '135****5555', orders: 5, totalSpent: 8700, status: 'active' },
  ];

  const filteredProductData = productData.filter(item =>
    item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.sku.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredOrderData = orderData.filter(item =>
    item.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.customer.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredCustomerData = customerData.filter(item =>
    item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.email.toLowerCase().includes(searchTerm.toLowerCase())
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

  const renderTable = (headers, data, columns, type) => (
    <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 rounded-lg">
      <table className="min-w-full divide-y divide-gray-300">
        <thead className="bg-gray-50">
          <tr>
            {headers.map((header, index) => (
              <th key={index} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {header}
              </th>
            ))}
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              操作
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {data.length > 0 ? (
            data.map((item) => (
              <tr key={item.id || item.sku || item.email} className="hover:bg-gray-50">
                {columns.map((col, idx) => (
                  <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {col === 'status' || col === 'platform' ? (
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadgeClass(item[col])}`}>
                        {item[col]}
                      </span>
                    ) : col === 'price' || col === 'amount' || col === 'totalSpent' ? (
                      `¥${item[col].toLocaleString()}`
                    ) : (
                      item[col]
                    )}
                  </td>
                ))}
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <div className="flex justify-end space-x-2">
                    <button className="text-blue-600 hover:text-blue-900">
                      <EyeIcon className="h-5 w-5" />
                    </button>
                    <button className="text-green-600 hover:text-green-900">
                      <PencilIcon className="h-5 w-5" />
                    </button>
                    <button className="text-red-600 hover:text-red-900">
                      <TrashIcon className="h-5 w-5" />
                    </button>
                  </div>
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan={headers.length + 1} className="px-6 py-4 text-center text-sm text-gray-500">
                暂无数据
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
          <h1 className="text-3xl font-bold text-gray-900">数据管理</h1>
          <p className="mt-2 text-gray-600">管理您的商品、订单和客户数据</p>
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
                  placeholder="搜索..."
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
              <button className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg text-sm font-medium text-white bg-blue-600 hover:bg-blue-700">
                <PlusIcon className="h-5 w-5 mr-2" />
                新建
              </button>
              <button className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                <ArrowDownTrayIcon className="h-5 w-5 mr-2" />
                导出
              </button>
            </div>
          </div>
        </div>

        {/* 选项卡 */}
        <Tab.Group selectedIndex={activeTab} onChange={setActiveTab}>
          <Tab.List className="flex space-x-1 rounded-xl bg-blue-100 p-1 mb-6">
            <Tab
              className={({ selected }) =>
                `w-full rounded-lg py-3 text-sm font-medium leading-5
                ${selected
                  ? 'bg-white shadow text-blue-700'
                  : 'text-blue-500 hover:bg-white/[0.12] hover:text-blue-700'}`
              }
            >
              商品数据
            </Tab>
            <Tab
              className={({ selected }) =>
                `w-full rounded-lg py-3 text-sm font-medium leading-5
                ${selected
                  ? 'bg-white shadow text-blue-700'
                  : 'text-blue-500 hover:bg-white/[0.12] hover:text-blue-700'}`
              }
            >
              订单数据
            </Tab>
            <Tab
              className={({ selected }) =>
                `w-full rounded-lg py-3 text-sm font-medium leading-5
                ${selected
                  ? 'bg-white shadow text-blue-700'
                  : 'text-blue-500 hover:bg-white/[0.12] hover:text-blue-700'}`
              }
            >
              客户数据
            </Tab>
          </Tab.List>
          <Tab.Panels>
            <Tab.Panel>
              {renderTable(
                ['商品名称', 'SKU', '价格', '库存', '状态', '平台'],
                filteredProductData,
                ['name', 'sku', 'price', 'stock', 'status', 'platform'],
                'products'
              )}
            </Tab.Panel>
            <Tab.Panel>
              {renderTable(
                ['订单号', '客户', '日期', '金额', '状态', '平台'],
                filteredOrderData,
                ['id', 'customer', 'date', 'amount', 'status', 'platform'],
                'orders'
              )}
            </Tab.Panel>
            <Tab.Panel>
              {renderTable(
                ['姓名', '邮箱', '电话', '订单数', '消费总额', '状态'],
                filteredCustomerData,
                ['name', 'email', 'phone', 'orders', 'totalSpent', 'status'],
                'customers'
              )}
            </Tab.Panel>
          </Tab.Panels>
        </Tab.Group>
      </div>
    </div>
  );
};

export default DataManagement;