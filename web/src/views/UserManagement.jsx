import React, { useState, useEffect } from 'react';
import { Table, Card, Button, Space, Modal, Form, Input, Select, message, Tag, Spin } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined } from '@ant-design/icons';
import { apiRequest } from '../utils/api';

const { Option } = Select;

const UserManagement = () => {
  const [usersList, setUsersList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [form] = Form.useForm();
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
  });
  const [goodsWithStoresList, setGoodsWithStoresList] = useState([]); // 商品和店铺关联列表
  const [searchParams, setSearchParams] = useState('');

  // 角色选项
  const roleOptions = [
    // { value: 'admin', label: '管理员' },
    // { value: 'manager', label: '经理' },
    { value: 'sales', label: '销售' },
    { value: 'user', label: '普通用户' },
  ];

  // 加载商品和店铺关联数据
  const loadGoodsWithStoresList = async () => {
  try {
    const response = await apiRequest('/goods_dict/'); // 调用新的商品字典接口
    if (response.ok) {
      const data = await response.json();
      // 直接使用接口返回的格式，无需额外处理
      setGoodsWithStoresList(data.data || []);
    }
  } catch (error) {
    console.error('获取商品字典列表失败:', error);
  }
};

  useEffect(() => {
    loadGoodsWithStoresList();
  }, []);

  // 表格列配置
  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      sorter: (a, b) => a.id - b.id,
    },
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
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
      render: (role) => {
        let color = 'default';
        if (role === 'admin') color = 'red';
        if (role === 'manager') color = 'orange';
        if (role === 'sales') color = 'blue';
        if (role === 'user') color = 'geekblue';
        
        return <Tag color={color}>{role === 'admin' ? '管理员' : role === 'manager' ? '经理' : role === 'sales' ? '销售' : '普通用户'}</Tag>;
      },
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (status) => {
        let color = 'default';
        if (status === true) color = 'green';
        if (status === false) color = 'red';
        
        return <Tag color={color}>{status === true ? '激活' : '禁用'}</Tag>;
      },
    },
    {
      title: '关联商品数量',
      dataIndex: 'goods_stores',
      key: 'goods_count',
      render: (goods_stores) => {
        return <span>{goods_stores ? goods_stores.length : 0}</span>;
      },
    },
    {
      title: '注册时间',
      dataIndex: 'created_at',
      key: 'created_at',
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space size="middle">
          <Button 
            type="link" 
            icon={<EditOutlined />} 
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Button 
            type="link" 
            danger 
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  // 加载用户数据
  const loadUsers = async (page = 1, pageSize = 10, search = '') => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        skip: (page - 1) * pageSize,
        limit: pageSize
      });
      
      if (search) {
        params.append('search', search);
      }
      
      const response = await apiRequest(`/users?${params.toString()}`);
      if (response) {
        const data = await response.json();
        // 确保每个用户的goods_stores字段都是数组
        const usersWithDefaultGoodsStores = data.data.map(user => ({
          ...user,
          goods_stores: user.goods_stores || [],
          // 将布尔型的is_active转换为中文显示
          is_active: user.is_active !== undefined ? user.is_active : true
        }));
        setUsersList(usersWithDefaultGoodsStores);
        setPagination(prev => ({
          ...prev,
          current: page,
          total: data.total
        }));
      }
    } catch (error) {
      console.error('加载用户数据失败:', error);
      message.error('加载用户数据失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers(pagination.current, pagination.pageSize);
  }, []);

  // 提交表单
  const handleSubmit = async (values) => {
  try {
    // 处理goods_stores字段，将字符串格式转换为对象格式
    let processedGoodsStores = [];
    if (values.goods_stores && values.goods_stores.length > 0) {
      processedGoodsStores = values.goods_stores.map(item => {
        if (typeof item === 'string') {
          // 如果是商品ID字符串，查找对应的商品信息
          const matchedItem = goodsWithStoresList.find(g => g.value === item);
          return {
            good_id: item,
            good_name: matchedItem ? matchedItem.label : ''
          };
        } else if (typeof item === 'object' && item !== null) {
          // 如果已经是对象格式，检查是否是新格式还是旧格式
          if (item.hasOwnProperty('value') && item.hasOwnProperty('label')) {
            // 新格式：{value: 商品ID, label: 商品名}
            return {
              good_id: item.value,
              good_name: item.label
            };
          } else if (item.hasOwnProperty('good_id') && item.hasOwnProperty('good_name')) {
            // 旧格式：{good_id: 商品ID, good_name: 商品名}
            return item;
          }
        }
        return null;
      }).filter(item => item !== null); // 过滤掉无效项
    }

    let response;
    if (editingRecord) {
      // 更新用户
      response = await apiRequest(`/users/${editingRecord.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: values.username,
          email: values.email,
          role: values.role,
          is_active: values.is_active,
          password: values.password || undefined, // 如果密码为空则不更新
          goods_stores: processedGoodsStores // 更新用户的商品店铺关联数据
        }),
      });
    } else {
      // 添加新用户
      response = await apiRequest('/users/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: values.username,
          email: values.email,
          password: values.password,
          role: values.role,
          is_active: values.is_active,
          goods_stores: processedGoodsStores // 新用户关联的商品店铺数据
        }),
      });
    }
    
    if (response && response.ok) {
      message.success(editingRecord ? '更新用户成功' : '添加用户成功');
      setModalVisible(false);
      form.resetFields();
      setEditingRecord(null);
      loadUsers(pagination.current, pagination.pageSize); // 刷新数据
    } else {
      const errorData = await response.json().catch(() => ({}));
      message.error(errorData.detail || (editingRecord ? '更新用户失败' : '添加用户失败'));
    }
  } catch (error) {
    console.error(editingRecord ? '更新用户失败:' : '添加用户失败:', error);
    message.error(editingRecord ? '更新用户失败' : '添加用户失败');
  }
};


  // 编辑用户
const handleEdit = (record) => {
  setEditingRecord({
    ...record,
    is_active: record.is_active !== undefined ? record.is_active : true,
    goods_stores: record.goods_stores || []  // 确保goods_stores字段存在且为数组
  });

  // 将关联的商品店铺数据转换为选择框格式，并处理不同数据格式
  const goodsStoresValues = record.goods_stores ? record.goods_stores.map(item => {
    return item.good_id;
  }).filter(id => id !== '') : []; // 过滤掉空值
  
  form.setFieldsValue({
    username: record.username,
    email: record.email,
    role: record.role,
    is_active: record.is_active !== undefined ? record.is_active : true,
    password: '', // 编辑时不显示原密码
    goods_stores: goodsStoresValues
  });
  setModalVisible(true);
};

  // 删除用户
  const handleDelete = async (id) => {
    Modal.confirm({
      title: '确认删除用户',
      content: '确定要删除这个用户吗？删除后无法恢复。',
      okText: '确认',
      cancelText: '取消',
      onOk: async () => {
        try {
          const response = await apiRequest(`/users/${id}`, { 
            method: 'DELETE' 
          });
          
          if (response && response.ok) {
            message.success('删除用户成功');
            // 检查当前页是否还有数据，如果没有则返回上一页
            if (usersList.length === 1 && pagination.current > 1) {
              loadUsers(pagination.current - 1, pagination.pageSize);
            } else {
              loadUsers(pagination.current, pagination.pageSize); // 刷新数据
            }
          } else {
            const errorData = await response.json().catch(() => ({}));
            message.error(errorData.detail || '删除用户失败');
          }
        } catch (error) {
          console.error('删除用户失败:', error);
          message.error('删除用户失败');
        }
      },
    });
  };

  // 显示新增表单
  const showAddForm = () => {
    setEditingRecord(null);
    form.resetFields();
    setModalVisible(true);
  };

  // 分页变化处理
  const handlePaginationChange = (page, pageSize) => {
    loadUsers(page, pageSize);
  };

  // 筛选功能
  const handleSearch = () => {
    loadUsers(1, pagination.pageSize, searchParams); // 搜索时回到第一页
  };

  return (
    <div>

      {/* 筛选条件区域 */}
<Card 
        title="用户管理" 
        extra={
          <Space>
            <Space>
              <Input
                placeholder="输入用户名或邮箱进行搜索"
                value={searchParams}
                onChange={(e) => setSearchParams(e.target.value)}
                onPressEnter={handleSearch}
                style={{ width: 200 }}
              />
              <Button 
                type="primary" 
                icon={<SearchOutlined />} 
                onClick={handleSearch}
              >
                筛选
              </Button>
            </Space>
            <Button 
              type="primary" 
              icon={<PlusOutlined />} 
              onClick={showAddForm}
            >
              添加用户
            </Button>
          </Space>
        }
      >
        <Table 
          dataSource={usersList} 
          columns={columns} 
          rowKey="id"
          loading={loading}
          scroll={{ x: 1200, y: 460 }}
          size="small"
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: pagination.total,
            onChange: handlePaginationChange,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条`,
            pageSizeOptions: ['10', '20', '50', '100']
          }}
        />
      </Card>

      <Modal
        title={editingRecord ? '编辑用户' : '添加用户'}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          form.resetFields();
          setEditingRecord(null);
        }}
        footer={null}
        width={800}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="username"
            label="用户名"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input placeholder="请输入用户名" />
          </Form.Item>
          
          <Form.Item
            name="email"
            label="邮箱"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]}
          >
            <Input placeholder="请输入邮箱地址" />
          </Form.Item>
          
          <Form.Item
            name="password"
            label="密码"
            rules={editingRecord ? [] : [{ required: true, message: '请输入密码' }]}
          >
            <Input.Password 
              placeholder={editingRecord ? "留空则不修改密码" : "请输入密码"} 
            />
          </Form.Item>
          
          <Form.Item
            name="role"
            label="角色"
            rules={[{ required: true, message: '请选择用户角色' }]}
          >
            <Select placeholder="请选择用户角色">
              {roleOptions.map(option => (
                <Option key={option.value} value={option.value}>
                  {option.label}
                </Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item
            name="is_active"
            label="状态"
            rules={[{ required: true, message: '请选择用户状态' }]}
          >
            <Select placeholder="请选择用户状态">
              <Option value={true}>激活</Option>
              <Option value={false}>禁用</Option>
            </Select>
          </Form.Item>
          
          <Form.Item
            name="goods_stores"
            label="关联商品店铺"
          >
            <Select
              mode="multiple"
              allowClear
              placeholder="请选择用户关联的商品和店铺"
              maxTagCount="responsive"
              optionLabelProp="label"
            >
              {goodsWithStoresList.map(item => (
                <Option 
                  key={`${item.value}`} 
                  value={`${item.value}`}
                  label={`${item.label}`}
                >
                  <div>
                    <div>{item.label}</div>
                    <div style={{ fontSize: '12px', color: '#999' }}>{item.value}</div>
                  </div>
                </Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item>
            <Space>
              <Button 
                type="primary" 
                htmlType="submit"
              >
                提交
              </Button>
              <Button 
                onClick={() => {
                  setModalVisible(false);
                  form.resetFields();
                  setEditingRecord(null);
                }}
              >
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default UserManagement;