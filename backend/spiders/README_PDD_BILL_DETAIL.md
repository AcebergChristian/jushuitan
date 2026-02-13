# 拼多多账单明细功能说明

## 概述

新增了拼多多账单明细数据采集和存储功能，可以自动捕获并保存每条账单的详细信息。

## 数据库表结构

### pdd_bill_details 表

存储每条账单的详细信息，包括：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | AutoField | 主键 |
| bill_id | CharField | 账单ID (唯一) |
| mall_id | BigIntegerField | 商家ID |
| order_sn | CharField | 订单号 (索引) |
| amount | FloatField | 金额(分) |
| amount_yuan | FloatField | 金额(元) |
| created_at_timestamp | BigIntegerField | 账单创建时间戳 |
| bill_type | IntegerField | 账单类型 |
| class_id | IntegerField | 分类ID |
| class_id_desc | CharField | 分类描述 |
| finance_id | IntegerField | 财务ID |
| finance_id_desc | CharField | 财务描述 |
| note | TextField | 备注 |
| bill_out_biz_code | CharField | 业务代码 |
| bill_out_biz_desc | CharField | 业务描述 |
| bill_biz_code | CharField | 账单业务代码 |
| shop_profile | CharField | 店铺配置名 |
| bill_date | DateField | 账单日期 |
| raw_data | TextField | 原始JSON数据 |
| is_del | BooleanField | 是否删除 |
| created_at | DateTimeField | 创建时间 |
| updated_at | DateTimeField | 更新时间 |

## API 接口

### 捕获的API

程序会自动捕获以下两个API的数据：

1. **账单统计API**: `queryBillStatistics`
   - 返回汇总的退款金额等统计数据

2. **账单明细API**: `pagingQueryMallBalanceBillListForMms`
   - 返回详细的账单列表
   - 包含每条账单的 orderSn 和 amount 等信息

### API 响应示例

```json
{
  "success": true,
  "result": {
    "billList": [
      {
        "billId": "4909310456897445365",
        "mallId": 263564789,
        "orderSn": "251229-176695580170223",
        "amount": 182,
        "createdAt": 1767353818,
        "type": 5,
        "classId": 2,
        "classIdDesc": "优惠券结算",
        "financeId": 2,
        "financeIdDesc": "优惠券补贴",
        "note": "交易成功优惠券支付金额结算",
        "billOutBizCode": "0010005",
        "billOutBizDesc": "交易收入-优惠券结算",
        "billBizCode": "5-00001"
      }
    ],
    "total": 15
  }
}
```

## 使用方法

### 1. 运行数据库迁移

首先需要创建新的数据表：

```bash
python backend/migrate_add_pdd_bill_detail.py
```

### 2. 运行爬虫

运行拼多多爬虫时，程序会自动：
- 捕获账单统计API和明细API的响应
- 解析账单明细数据
- 将 orderSn 和 amount 等信息保存到数据库
- 自动去重（根据 bill_id）

```bash
python backend/spiders/pdd_api_enhanced.py
```

### 3. 测试功能

运行测试脚本验证功能：

```bash
python backend/test_bill_detail.py
```

## 功能特点

1. **自动捕获**: 无需手动操作，程序自动捕获API响应
2. **数据完整**: 保存完整的账单信息，包括原始JSON数据
3. **自动去重**: 根据 bill_id 自动去重，避免重复保存
4. **金额转换**: 自动将分转换为元，方便查询
5. **索引优化**: 在 order_sn 和 bill_type 上建立索引，提高查询效率
6. **软删除**: 支持逻辑删除，数据不会真正丢失

## 数据查询示例

### 查询所有账单

```python
from backend.models.database import PddBillDetail

bills = PddBillDetail.select().where(
    PddBillDetail.is_del == False
).order_by(PddBillDetail.created_at.desc())

for bill in bills:
    print(f"订单号: {bill.order_sn}, 金额: {bill.amount_yuan}元")
```

### 按订单号查询

```python
order_bills = PddBillDetail.select().where(
    PddBillDetail.order_sn == "251229-176695580170223",
    PddBillDetail.is_del == False
)
```

### 按类型统计

```python
from peewee import fn

type_stats = (PddBillDetail
             .select(PddBillDetail.class_id_desc, 
                    fn.COUNT(PddBillDetail.id).alias('count'),
                    fn.SUM(PddBillDetail.amount_yuan).alias('total_amount'))
             .where(PddBillDetail.is_del == False)
             .group_by(PddBillDetail.class_id_desc))

for stat in type_stats:
    print(f"{stat.class_id_desc}: {stat.count}条, 总额: {stat.total_amount:.2f}元")
```

## 注意事项

1. 确保数据库连接正常
2. 首次使用需要运行迁移脚本创建表
3. bill_id 是唯一的，重复的账单会被自动跳过
4. 金额字段同时保存分和元两种单位，方便不同场景使用
5. raw_data 字段保存完整的原始JSON数据，便于后续分析

## 账单类型说明

根据API返回的数据，常见的账单类型包括：

- **type=5, classId=2**: 优惠券结算
- **type=6, classId=2**: 优惠券结算（退款扣除）
- **type=2, classId=3**: 退款

每种类型都有对应的 financeIdDesc 和 billOutBizDesc 描述。

## 故障排查

如果数据没有保存到数据库：

1. 检查数据库连接是否正常
2. 确认表是否已创建（运行迁移脚本）
3. 查看控制台输出的错误信息
4. 检查 bill_id 是否已存在（会跳过重复数据）
5. 确认API响应是否被正确捕获
