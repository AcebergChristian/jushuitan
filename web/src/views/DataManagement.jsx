import React, { useState, useEffect } from 'react';
import { Table, Card, Button, Space, Input, message, Tabs, DatePicker } from 'antd';
import { SearchOutlined, SyncOutlined } from '@ant-design/icons';
import { apiRequest } from '../utils/api';

const { TabPane } = Tabs;

const DataManagement = () => {
  const [activePlatformTab, setActivePlatformTab] = useState(0); // 0: 聚水潭, 1: 拼多多
  const [dataList, setDataList] = useState([]);
  const [pinduoduoData, setPinduoduoData] = useState([]);
  const [loading, setLoading] = useState(false);

  // 分页相关状态
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
  });

  // 搜索和筛选状态
  const [searchParams, setSearchParams] = useState({
    keyword: '',
  });

  // 添加状态变量来存储选中的日期
  const [selectedSyncDate, setSelectedSyncDate] = useState('');



  // 根据参考组件动态生成列配置
  const generateColumns = (data) => {
    if (!data || data.length === 0) {
      return [{
        title: '暂无数据',
        dataIndex: 'nodata',
        key: 'nodata',
        render: () => '暂无数据'
      }];
    }

    // 获取所有可能的字段名（从第一条记录获取）
    const firstItem = data[0];
    if (!firstItem) {
      return [{
        title: '暂无数据',
        dataIndex: 'nodata',
        key: 'nodata',
        render: () => '暂无数据'
      }];
    }
    // 获取所有可能的字段名（从第一条记录获取）
    const allKeys = Object.keys(data[0]);
    // 移除一些不需要显示的字段
    const displayKeys = allKeys.filter(key => key !== 'is_del');

    return displayKeys.map((key, index) => ({
      title: key,
      dataIndex: key,
      key: key,
      render: (value) => {
        // 处理各种特殊字段
        if (key === 'status' || key === 'platform' || key === 'isSuccess' || key === 'orderStatus' || key === 'orderType' || key === 'data_type') {
          let badgeClass = '';
          switch (value) {
            case 'active':
            case 'completed':
            case 'regular':
              badgeClass = 'bg-green-100 text-green-800';
              break;
            case 'low-stock':
              badgeClass = 'bg-yellow-100 text-yellow-800';
              break;
            case 'out-of-stock':
              badgeClass = 'bg-red-100 text-red-800';
              break;
            case 'processing':
              badgeClass = 'bg-blue-100 text-blue-800';
              break;
            case 'pending':
              badgeClass = 'bg-yellow-100 text-yellow-800';
              break;
            case 'cancelled':
            case 'cancel':
              badgeClass = 'bg-gray-100 text-gray-800';
              break;
            case 'inactive':
              badgeClass = 'bg-gray-100 text-gray-800';
              break;
            case 'vip':
              badgeClass = 'bg-purple-100 text-purple-800';
              break;
            default:
              badgeClass = 'bg-gray-100 text-gray-800';
          }

          return (
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${badgeClass}`}>
              {value !== null && value !== undefined && value !== '' ? String(value) : '-'}
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
      }
    }));
  };

  // 获取聚水潭数据
  const fetchJushuitanData = async (page = pagination.current, size = pagination.pageSize, search = searchParams.keyword) => {
    setLoading(true);
    try {
      const skip = (page - 1) * size;
      const limit = size;

      let url = `/jushuitan_products/?skip=${skip}&limit=${limit}`;
      if (search) {
        url += `&search=${encodeURIComponent(search)}`; // 防特殊字符
      }

      const response = await apiRequest(url);

      if (response.ok) {
        const responseData = await response.json();
        setDataList(responseData.data || responseData);
        setPagination(prev => ({
          ...prev,
          total: responseData.total || responseData.length || 0,
        }));
      } else {
        message.error('获取聚水潭数据失败');
      }
    } catch (error) {
      message.error('获取聚水潭数据时发生错误');
    } finally {
      setLoading(false);
    }
  };

  // 同步聚水潭数据（同步后刷新当前页）
  const syncJushuitanData = async (syncDate = '') => {
    setLoading(true);
    try {
      const response = await apiRequest('/sync_jushuitan_data',
        {
          method: 'POST',
          body: JSON.stringify({ sync_date: syncDate }) // 传递日期参数
        }
      );
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '同步失败');
      }

      const data = await response.json();
      message.success(data.message || '同步成功');
      fetchJushuitanData(); // 重新获取数据
    } catch (error) {
      console.error('同步数据失败:', error);
      message.error(error.message || '同步失败');
    } finally {
      setLoading(false);
    }
  };

  // 获取拼多多数据
  const fetchPinduoduoData = async (page = 1, size = 10, search = '') => {
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
      message.error('获取拼多多数据时发生错误');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activePlatformTab === 0) {
      fetchJushuitanData(pagination.current, pagination.pageSize, searchParams.keyword);
    } else {
      fetchPinduoduoData(pagination.current, pagination.pageSize, searchParams.keyword);
    }
  }, [activePlatformTab, pagination.current, pagination.pageSize, searchParams.keyword]);

  // 处理搜索
  const handleSearch = (value) => {
    setSearchParams({
      keyword: value,
    });

    // 重置到第一页并重新加载
    setPagination({
      ...pagination,
      current: 1,
    });

    if (activePlatformTab === 0) {
      fetchJushuitanData(1, pagination.pageSize, value);
    } else {
      fetchPinduoduoData(1, pagination.pageSize, value);
    }
  };

  // 处理分页/排序变化
  const handleTableChange = (paginator, filters, sorter) => {
    setPagination({
      current: paginator.current,
      pageSize: paginator.pageSize,
      total: pagination.total,
    });
    // effect 会自动触发 fetch，无需手动调用
  };

  // 获取当前数据源
  const getCurrentData = () => (activePlatformTab === 0 ? dataList : pinduoduoData);

  const columns = generateColumns(getCurrentData());

  return (
    <div>
      <Card
        title="数据管理"
        extra={
          <Space>
            <Input.Search
              placeholder={activePlatformTab === 0 ? "搜索商品..." : "搜索订单..."}
              allowClear
              enterButton="搜索"
              onSearch={handleSearch}
              style={{ width: 300 }}
            />
            {activePlatformTab === 0 && (
              <Space>
                <DatePicker
                  placeholder="选择同步日期"
                  onChange={(date, dateString) => setSelectedSyncDate(dateString)}
                  style={{ width: 150 }}
                />
                <Button
                  type="primary"
                  icon={<SyncOutlined />}
                  onClick={() => syncJushuitanData(selectedSyncDate)}
                >
                  同步数据
                </Button>
              </Space>
            )}
          </Space>
        }
      >
        <Tabs
          activeKey={activePlatformTab.toString()}
          onChange={(key) => setActivePlatformTab(Number(key))}
        >
          <TabPane tab="聚水潭" key="0">
            <Table
              dataSource={dataList}
              columns={columns}
              rowKey="id"
              loading={loading}
              size="small"
              pagination={{
                ...pagination,
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total) => `共 ${total} 条`,
                pageSizeOptions: ['10', '20', '50', '100'],
              }}
              onChange={handleTableChange}
              scroll={{ x: 'max-content', y: 400 }}
            />
          </TabPane>
          <TabPane tab="拼多多" key="1">
            <Table
              dataSource={pinduoduoData}
              columns={columns}
              rowKey="id"
              loading={loading}
              size="small"
              pagination={{
                ...pagination,
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total) => `共 ${total} 条`,
                pageSizeOptions: ['10', '20', '50', '100'],
              }}
              onChange={handleTableChange}
              scroll={{ x: 'max-content', y: 400 }}
            />
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default DataManagement;