import React, { useState, useEffect } from 'react';
import { Table, Card, Button, Space, Input, message, Modal, Tag, DatePicker } from 'antd';
import { SearchOutlined, SyncOutlined, EyeOutlined } from '@ant-design/icons';
import { apiRequest } from '../utils/api';
import dayjs from 'dayjs';

const GoodManagement = () => {
  const [goodsList, setGoodsList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [totalItems, setTotalItems] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedGood, setSelectedGood] = useState(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);

  // 在组件内部添加日期状态
const [syncDate, setSyncDate] = useState(dayjs()); // 默认为当前日期

  // 加载商品数据
  const loadGoods = async (page = 1, size = 10, search = '') => {
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
        setGoodsList(responseData.data || []);
        setTotalItems(responseData.total || 0);
      } else {
        console.error('获取商品数据失败:', response.statusText);
        message.error('获取商品数据失败');
      }
    } catch (error) {
      console.error('获取商品数据错误:', error);
      message.error('获取商品数据时发生错误');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadGoods(currentPage, pageSize, searchTerm);
  }, [currentPage, pageSize]);

  // 处理搜索框变化
  const handleSearchChange = (e) => {
    const value = e.target.value;
    setSearchTerm(value);
  };

  // 处理搜索提交
  const handleSearchSubmit = () => {
    loadGoods(currentPage, pageSize, searchTerm);
    setCurrentPage(1); // 搜索时回到第一页
  };

  // 同步商品数据
  const syncGoodsData = async () => {
  setLoading(true);
  try {
    // 使用选定的日期进行同步
    const syncDateStr = syncDate.format('YYYY-MM-DD');
    
    const response = await apiRequest('/sync_goods/', {
      method: 'POST',  // 改为POST方法以发送日期参数
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        sync_date: syncDateStr  // 添加日期参数
      }),
    });

    if (response.ok) {
      const result = await response.json();
      message.success(result.message || '商品数据同步成功');
      
      // 同步完成后重新获取当前页的数据
      loadGoods(currentPage, pageSize, searchTerm);
    } else {
      const errorData = await response.json().catch(() => ({}));
      message.error(errorData.detail || '商品数据同步失败');
    }
  } catch (error) {
    console.error('同步商品数据错误:', error);
    message.error('同步商品数据时发生错误');
  } finally {
    setLoading(false);
  }
};

  // 查看商品详情
  const viewGoodDetails = (good) => {
    setSelectedGood(good);
    setIsDetailModalOpen(true);
  };

  // 表格列配置
  const columns = [
    {
      title: '商品ID',
      dataIndex: 'goods_id',
      key: 'goods_id',
      sorter: (a, b) => (a.goods_id || 0) - (b.goods_id || 0),
    },
    {
      title: '商品名称',
      dataIndex: 'goods_name',
      key: 'goods_name',
      render: (text) => <span className="max-w-xs truncate">{text || '-'}</span>,
    },
    {
      title: '店铺ID',
      dataIndex: 'store_id',
      key: 'store_id',
      sorter: (a, b) => (a.store_id || 0) - (b.store_id || 0),
    },
    {
      title: '店铺名称',
      dataIndex: 'store_name',
      key: 'store_name',
    },
    {
      title: '订单ID',
      dataIndex: 'order_id',
      key: 'order_id',
    },
    {
      title: '付款金额',
      dataIndex: 'payment_amount',
      key: 'payment_amount',
      render: (amount) => `¥${(amount || 0).toFixed(2)}`,
      sorter: (a, b) => (a.payment_amount || 0) - (b.payment_amount || 0),
    },
    {
      title: '销售金额',
      dataIndex: 'sales_amount',
      key: 'sales_amount',
      render: (amount) => `¥${(amount || 0).toFixed(2)}`,
      sorter: (a, b) => (a.sales_amount || 0) - (b.sales_amount || 0),
    },
    {
      title: '销售成本',
      dataIndex: 'sales_cost',
      key: 'sales_cost',
      render: (cost) => `¥${(cost || 0).toFixed(2)}`,
      sorter: (a, b) => (a.sales_cost || 0) - (b.sales_cost || 0),
    },
    {
      title: '毛一利润',
      dataIndex: 'gross_profit_1_occurred',
      key: 'gross_profit_1_occurred',
      render: (profit) => `¥${(profit || 0).toFixed(2)}`,
      sorter: (a, b) => (a.gross_profit_1_occurred || 0) - (b.gross_profit_1_occurred || 0),
    },
    {
      title: '毛一利润率',
      dataIndex: 'gross_profit_1_rate',
      key: 'gross_profit_1_rate',
      render: (rate) => `${(rate || 0).toFixed(2)}%`,
      sorter: (a, b) => (a.gross_profit_1_rate || 0) - (b.gross_profit_1_rate || 0),
    },
    {
      title: '广告费',
      dataIndex: 'advertising_expenses',
      key: 'advertising_expenses',
      render: (expense) => `¥${(expense || 0).toFixed(2)}`,
      sorter: (a, b) => (a.advertising_expenses || 0) - (b.advertising_expenses || 0),
    },
    {
      title: '广告占比',
      dataIndex: 'advertising_rate',
      key: 'advertising_rate',
      render: (rate) => `${(rate || 0).toFixed(2)}%`,
      sorter: (a, b) => (a.advertising_rate || 0) - (b.advertising_rate || 0),
    },
    {
      title: '毛三利润',
      dataIndex: 'gross_profit_3',
      key: 'gross_profit_3',
      render: (profit) => `¥${(profit || 0).toFixed(2)}`,
      sorter: (a, b) => (a.gross_profit_3 || 0) - (b.gross_profit_3 || 0),
    },
    {
      title: '毛三利润率',
      dataIndex: 'gross_profit_3_rate',
      key: 'gross_profit_3_rate',
      render: (rate) => `${(rate || 0).toFixed(2)}%`,
      sorter: (a, b) => (a.gross_profit_3_rate || 0) - (b.gross_profit_3_rate || 0),
    },
    {
      title: '毛四利润',
      dataIndex: 'gross_profit_4',
      key: 'gross_profit_4',
      render: (profit) => `¥${(profit || 0).toFixed(2)}`,
      sorter: (a, b) => (a.gross_profit_4 || 0) - (b.gross_profit_4 || 0),
    },
    {
      title: '毛四利润率',
      dataIndex: 'gross_profit_4_rate',
      key: 'gross_profit_4_rate',
      render: (rate) => `${(rate || 0).toFixed(2)}%`,
      sorter: (a, b) => (a.gross_profit_4_rate || 0) - (b.gross_profit_4_rate || 0),
    },
    {
      title: '净利润',
      dataIndex: 'net_profit',
      key: 'net_profit',
      render: (profit) => `¥${(profit || 0).toFixed(2)}`,
      sorter: (a, b) => (a.net_profit || 0) - (b.net_profit || 0),
    },
    {
      title: '净利率',
      dataIndex: 'net_profit_rate',
      key: 'net_profit_rate',
      render: (rate) => `${(rate || 0).toFixed(2)}%`,
      sorter: (a, b) => (a.net_profit_rate || 0) - (b.net_profit_rate || 0),
    },
    {
      title: '商品订单时间',
      dataIndex: 'goodorder_time',
      key: 'goodorder_time',
      render: (date) => date || '-',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date) => date || '-',
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      render: (date) => date || '-',
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space size="middle">
          <Button 
            type="link" 
            icon={<EyeOutlined />} 
            onClick={() => viewGoodDetails(record)}
          >
            查看
          </Button>
        </Space>
      ),
    },
  ];

  // 详情模态框
  const DetailModal = () => {
    if (!selectedGood) return null;

    return (
      <Modal
        title="商品详情"
        open={isDetailModalOpen}
        onCancel={() => setIsDetailModalOpen(false)}
        footer={[
          <Button key="close" onClick={() => setIsDetailModalOpen(false)}>
            关闭
          </Button>
        ]}
        width={800}
      >
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
      </Modal>
    );
  };

  return (
    <div>
      <Card 
        title="商品管理" 
        extra={
          <Space>
            <Input.Search
              placeholder="搜索商品名称..."
              allowClear
              enterButton="搜索"
              value={searchTerm}
              onChange={handleSearchChange}
              onSearch={handleSearchSubmit}
              style={{ width: 300 }}
            />

            <DatePicker 
              value={syncDate}
              onChange={setSyncDate}
              placeholder="选择同步日期"
            />
            <Button 
              type="primary" 
              icon={<SyncOutlined />}
              onClick={syncGoodsData}
            >
              同步
            </Button>
          </Space>
        }
      >
        <Table 
          dataSource={goodsList} 
          columns={columns} 
          rowKey="id"
          loading={loading}
          size="small"
          scroll={{ x: 'max-content', y: 400 }}
          pagination={{
            current: currentPage,
            pageSize: pageSize,
            total: totalItems,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条`,
            pageSizeOptions: ['5', '10', '20', '50'],
            onChange: (page, size) => {
              setCurrentPage(page);
              setPageSize(size);
            },
          }}
        />
      </Card>
      
      {/* 详情模态框 */}
      <DetailModal />
    </div>
  );
};

export default GoodManagement;