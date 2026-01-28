import React, { useState, useEffect } from 'react';
import { Table, Card, Button, Space, Modal, Form, message, Tag, Spin, DatePicker } from 'antd';
import { PlusOutlined, EyeOutlined, ReloadOutlined } from '@ant-design/icons';
import { apiRequest } from '../utils/api';

const { RangePicker } = DatePicker;


const UserGoodManagement = () => {
  const [usersList, setUsersList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [userGoodsDetails, setUserGoodsDetails] = useState([]);
  const [currentUser, setCurrentUser] = useState('');
  const [form] = Form.useForm();
  const [dataLoading, setDataLoading] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);

  // 日期范围选择器状态
  const [selectedDateRange, setSelectedDateRange] = useState([]);


  // 表格列配置 - 用户汇总数据
  const userColumns = [
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
      sorter: (a, b) => a.username && b.username ? a.username.localeCompare(b.username) : 0,
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: '角色',
      dataIndex: 'role',
      key: 'role',
      render: (text) => (
        <Tag color={text === 'admin' ? 'red' : 'blue'}>
          {text === 'admin' ? '管理员' : text === 'sales' ? '销售' : '普通用户'}
        </Tag>
      ),
    },
    {
      title: '关联商品数量',
      dataIndex: 'goods_count',
      key: 'goods_count',
      sorter: (a, b) => (a.goods_count || 0) - (b.goods_count || 0),
    },
    {
      title: '关联店铺数量',
      dataIndex: 'stores_count',
      key: 'stores_count',
      sorter: (a, b) => (a.stores_count || 0) - (b.stores_count || 0),
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
            onClick={() => handleViewUserGoodsDetails(record.id, record.username)}
          >
            查看详情
          </Button>
        </Space>
      ),
    },
  ];

  // 用户商品详情表格列配置
  const userGoodsDetailColumns = [
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
      title: '店铺ID',
      dataIndex: 'store_id',
      key: 'store_id',
    },
    {
      title: '店铺名称',
      dataIndex: 'store_name',
      key: 'store_name',
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

  // 加载用户数据
  const loadUsers = async () => {
    setDataLoading(true);
    try {
      let url = '/user_goods_summary/';
      
      // 如果选择了日期范围，添加到URL参数中
      const params = new URLSearchParams();
      if (selectedDateRange && selectedDateRange.length === 2) {
        params.append('start_date', selectedDateRange[0].format('YYYY-MM-DD'));
        params.append('end_date', selectedDateRange[1].format('YYYY-MM-DD'));
      }
      
      if (params.toString()) {
        url += '?' + params.toString();
      }

      const response = await apiRequest(url);
   
      const result = await response.json();
      
      if (result.data) {
        setUsersList(result.data);
        message.success(result.message || '用户数据加载成功');
      } else {
        message.error(result.message || '用户数据加载失败');
        setUsersList([]);
      }
    } catch (error) {
      console.error('加载用户数据失败:', error);
      message.error('加载用户数据失败');
      setUsersList([]);
    } finally {
      setDataLoading(false);
    }
  };

  // 查看用户商品详情
  const handleViewUserGoodsDetails = async (userId, username) => {
    setCurrentUser(`${username} (${userId})`);
    setDetailLoading(true);
    
    try {
      let url = `/user_goods_detail/${userId}`;
      
      // 如果选择了日期范围，添加到URL参数中
      const params = new URLSearchParams();
      if (selectedDateRange && selectedDateRange.length === 2) {
        params.append('start_date', selectedDateRange[0].format('YYYY-MM-DD'));
        params.append('end_date', selectedDateRange[1].format('YYYY-MM-DD'));
      }
      
      if (params.toString()) {
        url += '?' + params.toString();
      }

      const response = await apiRequest(url);
      const result = await response.json();
      
      if (result.data) {
        setUserGoodsDetails(result.data);
        setDetailModalVisible(true);
      } else {
        message.error(result.message || '获取用户商品详情失败');
        setUserGoodsDetails([]);
      }
    } catch (error) {
      console.error('获取用户商品详情失败:', error);
      message.error('获取用户商品详情失败');
      setUserGoodsDetails([]);
    } finally {
      setDetailLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  
  return (
    <div>
      <Card 
        title="用户商品汇总数据管理" 
        extra={
        <Space>
            <RangePicker
              value={selectedDateRange}
              onChange={setSelectedDateRange}
              placeholder={['开始日期', '结束日期']}
            />
            <Button 
              type="primary" 
              icon={<ReloadOutlined />} 
              onClick={loadUsers}
              loading={loading}
            >
              刷新数据
            </Button>
          </Space>
        }
      >
        <Spin spinning={dataLoading}>
          <Table 
            dataSource={usersList} 
            columns={userColumns} 
            rowKey={(record) => record.id || record.username}
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
        title={`用户商品详情 - ${currentUser}`}
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={null}
        width={1200}
      >
        <Spin spinning={detailLoading}>
          <Table 
            dataSource={userGoodsDetails} 
            columns={userGoodsDetailColumns} 
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

export default UserGoodManagement;