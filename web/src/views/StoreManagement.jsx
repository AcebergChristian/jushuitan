import React, { useState, useEffect } from 'react';
import { Table, Card, Button, Space, Modal, Form, DatePicker, message, Tag, Spin } from 'antd';
import { EyeOutlined, RedoOutlined } from '@ant-design/icons';
import { apiRequest } from '../utils/api';

const { RangePicker } = DatePicker;

const StoreManagement = () => {
  const [storesList, setStoresList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [storeDetails, setStoreDetails] = useState([]);
  const [currentStoreId, setCurrentStoreId] = useState('');
  const [form] = Form.useForm();
  const [dataLoading, setDataLoading] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);

  const [dateRange, setDateRange] = useState(null); // 添加日期范围状态
  // 店铺状态选项
  const statusOptions = [
    { value: 'active', label: '启用' },
    { value: 'inactive', label: '停用' },
    { value: 'pending', label: '待审核' },
  ];

  // 表格列配置 - 店铺汇总数据
  const storeColumns = [
    {
      title: '店铺ID',
      dataIndex: 'store_id',
      key: 'store_id',
      sorter: (a, b) => a.store_id && b.store_id ? a.store_id.localeCompare(b.store_id) : 0,
    },
    {
      title: '店铺名称',
      dataIndex: 'store_name',
      key: 'store_name',
    },
    {
      title: '商品数量',
      dataIndex: 'goods_count',
      key: 'goods_count',
      sorter: (a, b) => (a.goods_count || 0) - (b.goods_count || 0),
    },
    {
      title: '付款金额',
      dataIndex: 'payment_amount',
      key: 'payment_amount',
      render: (text) => `¥${Number(text || 0).toFixed(2)}`,
      sorter: (a, b) => (a.payment_amount || 0) - (b.payment_amount || 0),
    },
    {
      title: '销售金额',
      dataIndex: 'sales_amount',
      key: 'sales_amount',
      render: (text) => `¥${Number(text || 0).toFixed(2)}`,
      sorter: (a, b) => (a.sales_amount || 0) - (b.sales_amount || 0),
    },
    {
      title: '销售成本',
      dataIndex: 'sales_cost',
      key: 'sales_cost',
      render: (text) => `¥${Number(text || 0).toFixed(2)}`,
      sorter: (a, b) => (a.sales_cost || 0) - (b.sales_cost || 0),
    },
    {
      title: '毛一利润(发生)',
      dataIndex: 'gross_profit_1_occurred',
      key: 'gross_profit_1_occurred',
      render: (text) => `¥${Number(text || 0).toFixed(2)}`,
      sorter: (a, b) => (a.gross_profit_1_occurred || 0) - (b.gross_profit_1_occurred || 0),
    },
    {
      title: '毛一利润率',
      dataIndex: 'gross_profit_1_rate',
      key: 'gross_profit_1_rate',
      render: (text) => `${Number(text || 0).toFixed(2)}%`,
      sorter: (a, b) => (a.gross_profit_1_rate || 0) - (b.gross_profit_1_rate || 0),
    },
    {
      title: '广告费',
      dataIndex: 'advertising_expenses',
      key: 'advertising_expenses',
      render: (text) => `¥${Number(text || 0).toFixed(2)}`,
      sorter: (a, b) => (a.advertising_expenses || 0) - (b.advertising_expenses || 0),
    },
    {
      title: '广告占比',
      dataIndex: 'advertising_ratio',
      key: 'advertising_ratio',
      render: (text) => `${Number(text || 0).toFixed(2)}%`,
      sorter: (a, b) => (a.advertising_ratio || 0) - (b.advertising_ratio || 0),
    },
    {
      title: '毛三利润',
      dataIndex: 'gross_profit_3',
      key: 'gross_profit_3',
      render: (text) => `¥${Number(text || 0).toFixed(2)}`,
      sorter: (a, b) => (a.gross_profit_3 || 0) - (b.gross_profit_3 || 0),
    },
    {
      title: '毛三利润率',
      dataIndex: 'gross_profit_3_rate',
      key: 'gross_profit_3_rate',
      render: (text) => `${Number(text || 0).toFixed(2)}%`,
      sorter: (a, b) => (a.gross_profit_3_rate || 0) - (b.gross_profit_3_rate || 0),
    },
    {
      title: '毛四利润',
      dataIndex: 'gross_profit_4',
      key: 'gross_profit_4',
      render: (text) => `¥${Number(text || 0).toFixed(2)}`,
      sorter: (a, b) => (a.gross_profit_4 || 0) - (b.gross_profit_4 || 0),
    },
    {
      title: '毛四利润率',
      dataIndex: 'gross_profit_4_rate',
      key: 'gross_profit_4_rate',
      render: (text) => `${Number(text || 0).toFixed(2)}%`,
      sorter: (a, b) => (a.gross_profit_4_rate || 0) - (b.gross_profit_4_rate || 0),
    },
    {
      title: '净利润',
      dataIndex: 'net_profit',
      key: 'net_profit',
      render: (text) => `¥${Number(text || 0).toFixed(2)}`,
      sorter: (a, b) => (a.net_profit || 0) - (b.net_profit || 0),
    },
    {
      title: '净利率',
      dataIndex: 'net_profit_rate',
      key: 'net_profit_rate',
      render: (text) => `${Number(text || 0).toFixed(2)}%`,
      sorter: (a, b) => (a.net_profit_rate || 0) - (b.net_profit_rate || 0),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button 
            type="link" 
            icon={<EyeOutlined />}
            onClick={() => handleViewDetails(record.store_id)}
          >
            查看详情
          </Button>
        </Space>
      ),
    },
  ];

  // 商品详情表格列配置
  const detailColumns = [
    {
      title: '商品ID',
      dataIndex: 'good_id',
      key: 'good_id',
    },
    {
      title: '商品名称',
      dataIndex: 'good_name',
      key: 'good_name',
    },
    {
      title: '付款金额',
      dataIndex: 'payment_amount',
      key: 'payment_amount',
      render: (text) => `¥${Number(text || 0).toFixed(2)}`,
    },
    {
      title: '销售金额',
      dataIndex: 'sales_amount',
      key: 'sales_amount',
      render: (text) => `¥${Number(text || 0).toFixed(2)}`,
    },
    {
      title: '销售成本',
      dataIndex: 'sales_cost',
      key: 'sales_cost',
      render: (text) => `¥${Number(text || 0).toFixed(2)}`,
    },
    {
      title: '毛一利润(发生)',
      dataIndex: 'gross_profit_1_occurred',
      key: 'gross_profit_1_occurred',
      render: (text) => `¥${Number(text || 0).toFixed(2)}`,
    },
    {
      title: '毛一利润率',
      dataIndex: 'gross_profit_1_rate',
      key: 'gross_profit_1_rate',
      render: (text) => `${Number(text || 0).toFixed(2)}%`,
    },
    {
      title: '广告费',
      dataIndex: 'advertising_expenses',
      key: 'advertising_expenses',
      render: (text) => `¥${Number(text || 0).toFixed(2)}`,
    },
    {
      title: '广告占比',
      dataIndex: 'advertising_ratio',
      key: 'advertising_ratio',
      render: (text) => `${Number(text || 0).toFixed(2)}%`,
    },
    {
      title: '毛三利润',
      dataIndex: 'gross_profit_3',
      key: 'gross_profit_3',
      render: (text) => `¥${Number(text || 0).toFixed(2)}`,
    },
    {
      title: '毛三利润率',
      dataIndex: 'gross_profit_3_rate',
      key: 'gross_profit_3_rate',
      render: (text) => `${Number(text || 0).toFixed(2)}%`,
    },
    {
      title: '毛四利润',
      dataIndex: 'gross_profit_4',
      key: 'gross_profit_4',
      render: (text) => `¥${Number(text || 0).toFixed(2)}`,
    },
    {
      title: '毛四利润率',
      dataIndex: 'gross_profit_4_rate',
      key: 'gross_profit_4_rate',
      render: (text) => `${Number(text || 0).toFixed(2)}%`,
    },
    {
      title: '净利润',
      dataIndex: 'net_profit',
      key: 'net_profit',
      render: (text) => `¥${Number(text || 0).toFixed(2)}`,
    },
    {
      title: '净利率',
      dataIndex: 'net_profit_rate',
      key: 'net_profit_rate',
      render: (text) => `${Number(text || 0).toFixed(2)}%`,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
    },
  ];

  // 加载店铺数据
  const loadStores = async (showMessage = true) => {
    setDataLoading(true);
    try {
      // 构建查询参数，包括日期范围
      let url = '/stores_data/';
      const params = new URLSearchParams();
      
      if (dateRange) {
        params.append('start_date', dateRange[0].format('YYYY-MM-DD'));
        params.append('end_date', dateRange[1].format('YYYY-MM-DD'));
      }
      
      if (params.toString()) {
        url += '?' + params.toString();
      }
      
      const response = await apiRequest(url);
      const result = await response.json();
      
      if (result.data) {
        setStoresList(result.data);
        if (showMessage) {
          message.success(result.message || '数据加载成功');
        }
      } else {
        if (showMessage) {
          message.error(result.message || '数据加载失败');
        }
        setStoresList([]);
      }
    } catch (error) {
      console.error('加载店铺数据失败:', error);
      if (showMessage) {
        message.error('加载店铺数据失败');
      }
      setStoresList([]);
    } finally {
      setDataLoading(false);
    }
  };



  // 查看店铺详情
  const handleViewDetails = async (storeId) => {
    setCurrentStoreId(storeId);
    setDetailLoading(true);
    
    try {
      const response = await apiRequest(`/store_goods_detail/${storeId}`);
      const result = await response.json();
      
      if (result.data) {
        setStoreDetails(result.data);
        setDetailModalVisible(true);
      } else {
        message.error(result.message || '获取店铺商品详情失败');
        setStoreDetails([]);
      }
    } catch (error) {
      console.error('获取店铺商品详情失败:', error);
      message.error('获取店铺商品详情失败');
      setStoreDetails([]);
    } finally {
      setDetailLoading(false);
    }
  };

  useEffect(() => {
    loadStores();
  }, []);

  
  return (
    <div>
      <Card 
        title="用户商品店铺数据管理" 
        extra={
          <div style={{ display: 'flex', gap: 8 }}>
            <RangePicker
              value={dateRange}
              onChange={setDateRange}
              placeholder={['开始日期', '结束日期']}
              format="YYYY-MM-DD"
            />
            <Button 
              type="primary" 
              icon={<RedoOutlined />} 
              onClick={loadStores}
              loading={dataLoading}
            >
              刷新数据
            </Button>
          </div>
        }
      >
        <Spin spinning={dataLoading}>
          <Table 
            dataSource={storesList} 
            columns={storeColumns} 
            rowKey={(record) => record.store_id || record.id}
            loading={dataLoading}
            size="small"
            scroll={{ x: 'max-content', y: 400 }}
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total) => `共 ${total} 条`,
            }}
          />
        </Spin>
      </Card>

      <Modal
        title={`店铺商品详情 - ${currentStoreId}`}
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={null}
        width={1200}
      >
        <Spin spinning={detailLoading}>
          <Table 
            dataSource={storeDetails} 
            columns={detailColumns} 
            rowKey={(record) => record.good_id || record.id}
            size="small"
            scroll={{ x: 'max-content', y: 400 }}
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total) => `共 ${total} 条`,
            }}
          />
        </Spin>
      </Modal>
    </div>
  )
}

export default StoreManagement;