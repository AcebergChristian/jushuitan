import React, { useState } from 'react';
import { ChartBarIcon, ArrowPathIcon, UserGroupIcon, DocumentTextIcon } from '@heroicons/react/24/outline';

const Dash = () => {
  const [isSyncing, setIsSyncing] = useState(false);

  const handleSyncData = async () => {
    setIsSyncing(true);
    // 模拟数据同步过程
    await new Promise(resolve => setTimeout(resolve, 2000));
    setIsSyncing(false);
    alert('数据同步完成！');
  };

  // 模拟统计数据
  const stats = [
    { name: '总商品数', value: '1,254', change: '+5.2%', icon: DocumentTextIcon, iconColor: 'bg-blue-500' },
    { name: '活跃店铺', value: '24', change: '+1.2%', icon: UserGroupIcon, iconColor: 'bg-green-500' },
    { name: '待处理订单', value: '42', change: '-3.1%', icon: ChartBarIcon, iconColor: 'bg-yellow-500' },
    { name: '今日销售额', value: '¥24,568', change: '+12.4%', icon: ChartBarIcon, iconColor: 'bg-purple-500' },
  ];

  // 模拟图表数据
  const chartData = [
    { day: '周一', sales: 4000, orders: 240 },
    { day: '周二', sales: 3000, orders: 139 },
    { day: '周三', sales: 2000, orders: 980 },
    { day: '周四', sales: 2780, orders: 390 },
    { day: '周五', sales: 1890, orders: 480 },
    { day: '周六', sales: 2390, orders: 380 },
    { day: '周日', sales: 3490, orders: 430 },
  ];

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* 标题和同步按钮 */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">仪表板</h1>
            <p className="mt-2 text-gray-600">查看您的业务概览和关键指标</p>
          </div>
          <button
            onClick={handleSyncData}
            disabled={isSyncing}
            className={`flex items-center px-6 py-3 rounded-lg text-white font-medium ${
              isSyncing ? 'bg-blue-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
            } transition duration-200`}
          >
            {isSyncing ? (
              <>
                <ArrowPathIcon className="animate-spin h-5 w-5 mr-2" />
                同步中...
              </>
            ) : (
              <>
                <ArrowPathIcon className="h-5 w-5 mr-2" />
                同步最新数据
              </>
            )}
          </button>
        </div>

        {/* 统计卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => (
            <div key={index} className="bg-white rounded-xl shadow p-6">
              <div className="flex items-center">
                <div className={`p-3 rounded-lg ${stat.iconColor}`}>
                  <stat.icon className="h-6 w-6 text-white" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                  <p className="text-2xl font-semibold text-gray-900">{stat.value}</p>
                </div>
              </div>
              <div className="mt-4">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  stat.change.startsWith('+') ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {stat.change} vs 上周
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* 图表区域 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* 销售图表 */}
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">本周销售趋势</h2>
            <div className="h-80 flex items-end space-x-2">
              {chartData.map((item, index) => (
                <div key={index} className="flex flex-col items-center flex-1">
                  <div className="text-xs text-gray-500 mb-1">{item.day}</div>
                  <div
                    className="w-full bg-gradient-to-t from-blue-500 to-blue-400 rounded-t-lg"
                    style={{ height: `${(item.sales / 5000) * 200}px` }}
                  ></div>
                  <div className="text-xs mt-1 text-gray-600">¥{item.sales}</div>
                </div>
              ))}
            </div>
          </div>

          {/* 订单图表 */}
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">本周订单趋势</h2>
            <div className="h-80 flex items-end space-x-2">
              {chartData.map((item, index) => (
                <div key={index} className="flex flex-col items-center flex-1">
                  <div className="text-xs text-gray-500 mb-1">{item.day}</div>
                  <div
                    className="w-full bg-gradient-to-t from-green-500 to-green-400 rounded-t-lg"
                    style={{ height: `${(item.orders / 1000) * 200}px` }}
                  ></div>
                  <div className="text-xs mt-1 text-gray-600">{item.orders} 单</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 最近活动 */}
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">最近活动</h2>
          <div className="flow-root">
            <ul className="divide-y divide-gray-200">
              <li className="py-4">
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    <div className="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center">
                      <span className="text-white text-sm">张</span>
                    </div>
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-gray-900 truncate">张三</p>
                    <p className="text-sm text-gray-500 truncate">添加了新的商品 "iPhone 15 Pro"</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">2 小时前</p>
                  </div>
                </div>
              </li>
              <li className="py-4">
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    <div className="h-8 w-8 rounded-full bg-green-500 flex items-center justify-center">
                      <span className="text-white text-sm">李</span>
                    </div>
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-gray-900 truncate">李四</p>
                    <p className="text-sm text-gray-500 truncate">完成了订单 #ORD-001254</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">4 小时前</p>
                  </div>
                </div>
              </li>
              <li className="py-4">
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    <div className="h-8 w-8 rounded-full bg-purple-500 flex items-center justify-center">
                      <span className="text-white text-sm">王</span>
                    </div>
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-gray-900 truncate">王五</p>
                    <p className="text-sm text-gray-500 truncate">同步了聚水潭和拼多多数据</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">6 小时前</p>
                  </div>
                </div>
              </li>
              <li className="py-4">
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    <div className="h-8 w-8 rounded-full bg-yellow-500 flex items-center justify-center">
                      <span className="text-white text-sm">赵</span>
                    </div>
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-gray-900 truncate">赵六</p>
                    <p className="text-sm text-gray-500 truncate">更新了用户权限设置</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">1 天前</p>
                  </div>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dash;