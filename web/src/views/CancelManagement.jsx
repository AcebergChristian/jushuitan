import React, { useState, useEffect } from 'react';
import { Table, Card, Button, Space, Modal, Form, DatePicker, message, Tabs, Popconfirm, Spin} from 'antd';
import { EyeOutlined, RedoOutlined, SyncOutlined } from '@ant-design/icons';
import { apiRequest } from '../utils/api';

const { RangePicker } = DatePicker;
const { TabPane } = Tabs;

const CancelManagement = () => {
  const [cancelData, setCancelData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [syncLoading, setSyncLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [cancelDetails, setCancelDetails] = useState([]);
  const [currentTab, setCurrentTab] = useState('store'); // 'store' 或 'product'
  const [form] = Form.useForm();
  const [dataLoading, setDataLoading] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);
  const [syncDate, setSyncDate] = useState(null);
  const [searchText, setSearchText] = useState('');


  
  const [currentDimension, setCurrentDimension] = useState('store'); // 添加维度状态


  // 店铺维度表格列配置
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
      sorter: (a, b) => a.store_name && b.store_name ? a.store_name.localeCompare(b.store_name) : 0,
    },
    {
      title: '退货订单数',
      dataIndex: 'return_orders_count',
      key: 'return_orders_count',
      sorter: (a, b) => (a.return_orders_count || 0) - (b.return_orders_count || 0),
    },
    {
      title: '退货金额',
      dataIndex: 'return_amount',
      key: 'return_amount',
      render: (text) => `¥${Number(text || 0).toFixed(2)}`,
      sorter: (a, b) => (a.return_amount || 0) - (b.return_amount || 0),
    },
    {
      title: '退款金额',
      dataIndex: 'refund_amount',
      key: 'refund_amount',
      render: (text) => `¥${Number(text || 0).toFixed(2)}`,
      sorter: (a, b) => (a.refund_amount || 0) - (b.refund_amount || 0),
    },
    {
      title: '退货率',
      dataIndex: 'return_rate',
      key: 'return_rate',
      render: (text) => `${Number(text || 0).toFixed(2)}%`,
      sorter: (a, b) => (a.return_rate || 0) - (b.return_rate || 0),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button 
            type="link" 
            icon={<EyeOutlined />}
            onClick={() => handleViewDetails(record.store_id, 'store')}
          >
            查看详情
          </Button>
        </Space>
      ),
    },
  ];



  // 商品维度表格列配置
const productColumns = [
  {
    title: '商品ID',
    dataIndex: 'dimension_id',
    key: 'dimension_id',
    sorter: (a, b) => a.dimension_id && b.dimension_id ? a.dimension_id.localeCompare(b.dimension_id) : 0,
  },
  {
    title: '商品名称',
    dataIndex: 'dimension_name',
    key: 'dimension_name',
  },
  {
    title: '退货订单数',
    dataIndex: 'return_orders_count',
    key: 'return_orders_count',
    sorter: (a, b) => (a.return_orders_count || 0) - (b.return_orders_count || 0),
  },
  {
    title: '退货金额',
    dataIndex: 'return_amount',
    key: 'return_amount',
    render: (text) => `¥${Number(text || 0).toFixed(2)}`,
    sorter: (a, b) => (a.return_amount || 0) - (b.return_amount || 0),
  },
  {
    title: '退款金额',
    dataIndex: 'refund_amount',
    key: 'refund_amount',
    render: (text) => `¥${Number(text || 0).toFixed(2)}`,
    sorter: (a, b) => (a.refund_amount || 0) - (b.refund_amount || 0),
  },
  {
    title: '退货率',
    dataIndex: 'return_rate',
    key: 'return_rate',
    render: (text) => `${Number(text || 0).toFixed(2)}%`,
    sorter: (a, b) => (a.return_rate || 0) - (b.return_rate || 0),
  },
  {
    title: '创建时间',
    dataIndex: 'created_at',
    key: 'created_at',
  },
  {
    title: '更新时间',
    dataIndex: 'updated_at',
    key: 'updated_at',
  },
  {
    title: '操作',
    key: 'actions',
    render: (_, record) => (
      <Space>
        <Button 
          type="link" 
          icon={<EyeOutlined />}
          onClick={() => handleViewDetails(record.dimension_id, 'product')}
        >
          查看详情
        </Button>
      </Space>
    ),
  },
];



  // 退货详情表格列配置
  const detailColumns = [
    {
      title: '订单ID',
      dataIndex: 'order_id',
      key: 'order_id',
    },
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
      title: '订单金额',
      dataIndex: 'order_amount',
      key: 'order_amount',
      render: (text) => `¥${Number(text || 0).toFixed(2)}`,
    },
    {
      title: '退货金额',
      dataIndex: 'return_amount',
      key: 'return_amount',
      render: (text) => `¥${Number(text || 0).toFixed(2)}`,
    },
    {
      title: '退款金额',
      dataIndex: 'refund_amount',
      key: 'refund_amount',
      render: (text) => `¥${Number(text || 0).toFixed(2)}`,
    },
    {
      title: '退货原因',
      dataIndex: 'return_reason',
      key: 'return_reason',
    },
    {
      title: '退货状态',
      dataIndex: 'return_status',
      key: 'return_status',
      render: (status) => (
        <span>
          {status === 'completed' ? <Tag color="green">已完成</Tag> : 
           status === 'processing' ? <Tag color="orange">处理中</Tag> : 
           status === 'rejected' ? <Tag color="red">已拒绝</Tag> : 
           <Tag>{status}</Tag>}
        </span>
      ),
    },
    {
      title: '退货时间',
      dataIndex: 'return_time',
      key: 'return_time',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
    },
  ];



  // 同步退货数据
  const syncReturnData = async () => {
  setSyncLoading(true);
  try {
    // 必须选择一个日期
    if (!syncDate) {
      message.error('请先选择要同步的日期');
      setSyncLoading(false);
      return;
    }
    
    let syncDateValue = syncDate.format('YYYY-MM-DD');

    const response = await apiRequest('/sync_cancel_data', {
      method: 'POST',
      body: JSON.stringify({
        sync_date: syncDateValue, // 只传递单个日期
      }),
    });
    const result = await response.json();
    
    if (response.ok) {
      message.success(result.message || '退货数据同步成功');
      loadData(); // 重新加载数据
    } else {
      message.error(result.message || '退货数据同步失败');
    }
  } catch (error) {
    console.error('退货数据同步失败:', error);
    message.error('退货数据同步失败');
  } finally {
    setSyncLoading(false);
  }
};




  // 添加状态变量
  const [dateRange, setDateRange] = useState(null); // 日期范围
  
  // 加载退货数据
  const loadData = async (showMessage = true) => {
    setDataLoading(true);
    try {
      let url = '/cancel_data/';
      const params = new URLSearchParams();
      
      if (dateRange) {
        params.append('start_date', dateRange[0].format('YYYY-MM-DD'));
        params.append('end_date', dateRange[1].format('YYYY-MM-DD'));
      }
      
      if (searchText) {
        params.append('search', searchText);
      }
      
      // 添加维度参数
      params.append('dimension', currentDimension);
      
      if (params.toString()) {
        url += '?' + params.toString();
      }
      
      const response = await apiRequest(url);
      const result = await response.json();
      
      if (result.data) {
        setCancelData(result.data);
        if (showMessage) {
          message.success(result.message || '数据加载成功');
        }
      } else {
        if (showMessage) {
          message.error(result.message || '数据加载失败');
        }
        setCancelData([]);
      }
    } catch (error) {
      console.error('加载退货数据失败:', error);
      if (showMessage) {
        message.error('加载退货数据失败');
      }
      setCancelData([]);
    } finally {
      setDataLoading(false);
    }
  };

  // 查看详情
  const handleViewDetails = async (id, type) => {
    setDetailLoading(true);
    
    try {
      let url;
      if (type === 'store') {
        url = `/cancel_store_details/${id}`;
      } else {
        url = `/cancel_product_details/${id}`;
      }
      
      const response = await apiRequest(url);
      const result = await response.json();
      
      if (result.data) {
        setCancelDetails(result.data);
        setDetailModalVisible(true);
      } else {
        message.error(result.message || '获取详情失败');
        setCancelDetails([]);
      }
    } catch (error) {
      console.error('获取详情失败:', error);
      message.error('获取详情失败');
      setCancelDetails([]);
    } finally {
      setDetailLoading(false);
    }
  };

  

  useEffect(() => {
    loadData();
  }, []);



  // 获取当前数据类型
  const getCurrentDataType = () => {
    return currentTab === 'store' ? '店铺' : '商品';
  };

  return (
    <div>
      <Card 
  title="退货数据管理" 
  extra={
    <Space>

        <DatePicker
          value={syncDate}
          onChange={setSyncDate}
          placeholder="请选择同步日期"
          format="YYYY-MM-DD"
          allowClear={true} // 禁止清除选择
        />
        <Button 
          type="primary" 
          icon={<SyncOutlined />} 
          loading={syncLoading}
          disabled={!syncDate} // 禁用按钮直到选择日期
        >
          同步数据
        </Button>
    </Space>
  }
>
  <div style={{ marginBottom: 16 }}>
    <Space style={{ width: '100%', justifyContent: 'space-between' }}>
      <Space>
        <RangePicker
          value={dateRange}
          onChange={setDateRange}
          placeholder={['开始日期', '结束日期']}
          format="YYYY-MM-DD"
        />
        <input
          type="text"
          placeholder="模糊搜索..."
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          style={{ padding: '4px 11px', borderRadius: 6, border: '1px solid #d9d9d9' }}
        />
        <Button 
          type="primary" 
          icon={<SyncOutlined />} 
          loading={dataLoading}
          onClick={loadData}
        >
          查询
        </Button>
      </Space>
    </Space>
  </div>

  {/* 添加维度切换Tab */}
  <Tabs 
    defaultActiveKey="store" 
    activeKey={currentDimension}
    onChange={setCurrentDimension}
    items={[
      {
        key: 'store',
        label: '店铺维度',
        children: (
          <Spin spinning={dataLoading}>
            <Table 
              dataSource={cancelData} 
              columns={storeColumns} 
              rowKey={(record) => record.dimension_id || record.id}
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
        ),
      },
      {
        key: 'product',
        label: '商品维度',
        children: (
          <Spin spinning={dataLoading}>
            <Table 
              dataSource={cancelData} 
              columns={productColumns} // 需要定义商品维度的列
              rowKey={(record) => record.dimension_id || record.id}
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
        ),
      },
    ]}
  />
</Card>

      <Modal
        title={`${getCurrentDataType()}退货详情`}
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={null}
        width={1200}
      >
        <Spin spinning={detailLoading}>
          <Table 
            dataSource={cancelDetails} 
            columns={detailColumns} 
            rowKey={(record) => record.order_id || record.id}
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
  );
};

export default CancelManagement;