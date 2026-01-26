import React from 'react';
import { Card, Row, Col, Statistic, Typography } from 'antd';
import { UserOutlined, ShoppingCartOutlined, DatabaseOutlined, TeamOutlined } from '@ant-design/icons';

const { Title } = Typography;

const Dashboard = () => {
  // 示例数据统计
  const statsData = [
    {
      title: '总用户数',
      value: 12345,
      icon: <UserOutlined style={{ fontSize: '36px' }} />,
      color: '#1890ff',
    },
    {
      title: '商品总数',
      value: 6789,
      icon: <ShoppingCartOutlined style={{ fontSize: '36px' }} />,
      color: '#52c41a',
    },
    {
      title: '数据记录',
      value: 98765,
      icon: <DatabaseOutlined style={{ fontSize: '36px' }} />,
      color: '#722ed1',
    },
    {
      title: '活跃用户',
      value: 4321,
      icon: <TeamOutlined style={{ fontSize: '36px' }} />,
      color: '#fa8c16',
    },
  ];

  return (
    <div>
      <Title level={2}>仪表板</Title>
      
      <Row gutter={[16, 16]}>
        {statsData.map((stat, index) => (
          <Col xs={24} sm={12} md={6} key={index}>
            <Card>
              <Statistic
                title={stat.title}
                value={stat.value}
                prefix={stat.icon}
                valueStyle={{ color: stat.color }}
              />
            </Card>
          </Col>
        ))}
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} md={12}>
          <Card title="欢迎使用聚水潭系统">
            <p>这是一个功能完善的管理系统，可以帮您高效管理您的业务数据。</p>
            <p>在这里您可以：</p>
            <ul>
              <li>查看和管理用户信息</li>
              <li>管理商品数据</li>
              <li>监控系统状态</li>
              <li>处理业务数据</li>
            </ul>
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card title="系统概览">
            <p>当前在线用户: 24</p>
            <p>今日新增数据: 126</p>
            <p>系统运行状态: 正常</p>
            <p>最近备份时间: 2026-01-25 10:00</p>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;