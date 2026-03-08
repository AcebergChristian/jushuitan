import React, { useState } from 'react';
import { ArrowDownTrayIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { apiRequest } from '../utils/api';
import { DatePicker } from 'antd';

const DataManagement = () => {
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [loading, setLoading] = useState(false);
  const [showNotification, setShowNotification] = useState({
    show: false,
    message: '',
    type: '',
  });

  const showNotificationFunc = (message, type = 'success') => {
    setShowNotification({ show: true, message, type });
    setTimeout(() => {
      setShowNotification({ show: false, message: '', type: '' });
    }, 3000);
  };

  const handleSync = async () => {
    if (loading) return;

    setLoading(true);
    try {
      // 调用 /sync_jushuitan_data，并传递选择的年月日（sync_date）
      const payload = startDate ? { sync_date: startDate } : {};
      const response = await apiRequest('/sync_jushuitan_data', {
        method: 'POST',
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        const result = await response.json().catch(() => ({}));
        showNotificationFunc(result.message || '数据同步成功', 'success');
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

  const Notification = () => {
    if (!showNotification.show) return null;

    const bgColor =
      showNotification.type === 'error' ? 'bg-red-500' : 'bg-green-500';

    return (
      <div className="fixed top-4 right-4 z-50">
        <div
          className={`${bgColor} text-white px-6 py-4 rounded-lg shadow-lg flex items-center`}
        >
          <span>{showNotification.message}</span>
          <button
            onClick={() =>
              setShowNotification({ show: false, message: '', type: '' })
            }
            className="ml-4 text-white hover:text-gray-200"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen/2 bg-gradient-to-br from-slate-50 via-slate-100 to-slate-200 flex items-center justify-center">
      <div className="w-full max-w-4xl">
        {/* 标题 */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight mb-2">
            同步数据
          </h1>
          <p className="text-slate-500 text-sm">
            从聚水潭后台拉取最新数据，用于后续统计与分析。
          </p>
        </div>

        {/* 主卡片：左日期选择 + 右同步按钮 */}
        <div className="bg-white/80 backdrop-blur shadow-xl rounded-2xl border border-slate-100 p-6 md:p-8">
          <div className="flex flex-col md:flex-row gap-6 items-stretch">
            {/* 左侧：日期选择 */}
            <div className="flex-1">
              <h2 className="text-sm font-medium text-slate-700 mb-3">
                选择日期（可选）
              </h2>
              <div className="space-y-2">
                <label className="block text-xs font-medium text-slate-500 mb-1">
                  日期
                </label>
                <DatePicker
                  className="w-full"
                  allowClear
                  onChange={(_, dateString) => {
                    const value = Array.isArray(dateString) ? dateString[0] : dateString;
                    setStartDate(value || '');
                    setEndDate('');
                  }}
                />
              </div>
              <p className="mt-2 text-xs text-slate-400">
                如不选择日期，将按照系统默认范围同步最近的数据。
              </p>
            </div>

            {/* 右侧：同步按钮（用 div 做的卡片样式按钮） */}
            <div className="w-full md:w-40 flex md:flex-col gap-3 items-stretch justify-center">
              <div
                className={`relative flex-1 md:w-full flex items-center justify-center rounded-xl border text-sm font-medium transition-all select-none ${
                  loading
                    ? 'bg-slate-200 text-slate-400 border-slate-200 cursor-not-allowed'
                    : 'bg-blue-600 text-white border-blue-600 cursor-pointer shadow-lg shadow-blue-500/30 hover:bg-blue-700 hover:shadow-xl hover:-translate-y-0.5'
                }`}
                onClick={loading ? undefined : handleSync}
              >
                <ArrowDownTrayIcon className="h-5 w-5 mr-2" />
                {loading ? '同步中...' : '开始同步'}
              </div>
              <div className="text-xs text-slate-400 text-center md:text-left">
                点击「开始同步」后，请在几分钟后再刷新其他页面查看最新数据。
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 通知组件 */}
      <Notification />
    </div>
  );
};

export default DataManagement;
