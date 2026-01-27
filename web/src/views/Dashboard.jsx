import React, { useState, useEffect } from 'react';
import { ChartBarIcon, ArrowPathIcon, UserGroupIcon, DocumentTextIcon, ShoppingBagIcon, CurrencyDollarIcon } from '@heroicons/react/24/outline';
import { apiRequest } from '../utils/api';

const Dash = () => {
  const [isSyncing, setIsSyncing] = useState(false);
  const [stats, setStats] = useState({
    total_users: 0,
    total_goods: 0,
    total_stores: 0,
    total_sales_amount: 0,
    today_sales: 0,
    week_sales: 0,
    month_sales: 0,
    total_good_types: 0,
    active_users: 0,
    total_orders: 0,
    avg_order_value: 0,
    last_updated: ''
  });
  const [chartData, setChartData] = useState([]);
  const [recentActivities, setRecentActivities] = useState([]);

  // 加载仪表盘数据
  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      // 获取统计数据
      const statsResponse = await apiRequest('/dashboard/stats');
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStats(statsData.data);
      }

      // 获取图表数据
      const chartResponse = await apiRequest('/dashboard/chart-data');
      if (chartResponse.ok) {
        const chartData = await chartResponse.json();
        setChartData(chartData.data);
      }

      // 获取最近活动
      const activityResponse = await apiRequest('/dashboard/recent-activities');
      if (activityResponse.ok) {
        const activityData = await activityResponse.json();
        setRecentActivities(activityData.data);
      }
    } catch (error) {
      console.error('加载仪表盘数据失败:', error);
    }
  };

  const handleSyncData = async () => {
    setIsSyncing(true);
    try {
      // 模拟数据同步过程，实际应用中这里应该调用真实API
      await new Promise(resolve => setTimeout(resolve, 2000));
      // 同步完成后重新加载数据
      await loadDashboardData();
      alert('数据同步完成！');
    } catch (error) {
      console.error('同步数据失败:', error);
      alert('数据同步失败，请稍后重试');
    } finally {
      setIsSyncing(false);
    }
  };

  // 根据统计数据计算变化率
  const calculateChangeRate = (current, previous) => {
    if (previous === 0) return current > 0 ? '+100%' : '0%';
    const rate = ((current - previous) / previous) * 100;
    return `${rate >= 0 ? '+' : ''}${rate.toFixed(1)}%`;
  };

  // 准备显示的统计卡片
  const dashboardStats = [
    { name: '总用户数', value: stats.total_users?.toLocaleString() || '0', change: calculateChangeRate(stats.total_users, stats.total_users * 0.9), icon: UserGroupIcon, iconColor: 'bg-blue-500' },
    { name: '总商品数', value: stats.total_goods?.toLocaleString() || '0', change: calculateChangeRate(stats.total_goods, stats.total_goods * 0.95), icon: DocumentTextIcon, iconColor: 'bg-green-500' },
    { name: '活跃店铺', value: stats.total_stores || '0', change: calculateChangeRate(stats.total_stores, stats.total_stores * 0.8), icon: ShoppingBagIcon, iconColor: 'bg-yellow-500' },
    { name: '总销售额', value: `¥${(stats.total_sales_amount || 0).toLocaleString()}`, change: calculateChangeRate(stats.total_sales_amount, stats.total_sales_amount * 0.88), icon: CurrencyDollarIcon, iconColor: 'bg-purple-500' },
  ];

  return (
    <div className="p-6 bg-gray-50 h-[80%] overflow-auto">
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
          {dashboardStats.map((stat, index) => (
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
              {chartData && chartData.length > 0 ? (
                chartData.map((item, index) => (
                  <div key={index} className="flex flex-col items-center flex-1">
                    <div className="text-xs text-gray-500 mb-1">{item.date}</div>
                    <div
                      className="w-full bg-gradient-to-t from-blue-500 to-blue-400 rounded-t-lg"
                      style={{ height: `${Math.max((item.sales / Math.max(...chartData.map(c => c.sales || 1))) * 200, 10)}px` }}
                    ></div>
                    <div className="text-xs mt-1 text-gray-600">¥{item.sales}</div>
                  </div>
                ))
              ) : (
                <div className="w-full h-full flex items-center justify-center text-gray-500">
                  暂无数据
                </div>
              )}
            </div>
          </div>

          {/* 订单图表 */}
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">本周订单趋势</h2>
            <div className="h-80 flex items-end space-x-2">
              {chartData && chartData.length > 0 ? (
                chartData.map((item, index) => (
                  <div key={index} className="flex flex-col items-center flex-1">
                    <div className="text-xs text-gray-500 mb-1">{item.date}</div>
                    <div
                      className="w-full bg-gradient-to-t from-green-500 to-green-400 rounded-t-lg"
                      style={{ height: `${Math.max((item.orders / Math.max(...chartData.map(c => c.orders || 1))) * 200, 10)}px` }}
                    ></div>
                    <div className="text-xs mt-1 text-gray-600">{item.orders} 单</div>
                  </div>
                ))
              ) : (
                <div className="w-full h-full flex items-center justify-center text-gray-500">
                  暂无数据
                </div>
              )}
            </div>
          </div>
        </div>

        {/* 最近活动 */}
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">最近活动</h2>
          <div className="flow-root">
            <ul className="divide-y divide-gray-200">
              {recentActivities && recentActivities.length > 0 ? (
                recentActivities.map((activity, index) => (
                  <li key={index} className="py-4">
                    <div className="flex items-center space-x-4">
                      <div className="flex-shrink-0">
                        <div className={`h-8 w-8 rounded-full bg-${activity.avatar_color}-500 flex items-center justify-center`}>
                          <span className="text-white text-sm">{activity.user.charAt(0)}</span>
                        </div>
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium text-gray-900 truncate">{activity.user}</p>
                        <p className="text-sm text-gray-500 truncate">{activity.action}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">{activity.time}</p>
                      </div>
                    </div>
                  </li>
                ))
              ) : (
                <li className="py-4 text-center text-gray-500">
                  暂无活动记录
                </li>
              )}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dash;