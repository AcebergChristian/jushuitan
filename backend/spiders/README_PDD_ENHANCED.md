# 拼多多数据爬虫增强版使用说明

## 功能概述

`pdd_api_enhanced.py` 是原 `pdd_api.py` 的增强版本，新增以下功能：

1. ✅ **日期选择**：在推广页面自动/手动选择查询日期
2. ✅ **数据存储**：将推广数据保存到 `pdd_ads` 表
3. ✅ **账单查询**：访问账单页面，获取退款金额（outcomeAmount）
4. ✅ **账单存储**：将账单数据保存到 `pdd_bill_records` 表

## 数据库表结构

### pdd_ads 表
存储推广广告数据，包含：
- 广告基础信息（ad_id, ad_name, goods_id, mall_id等）
- 报表数据（曝光、点击、花费、订单、GMV等）
- ROI和转化数据

### pdd_bill_records 表（新增）
存储每日账单数据，包含：
- shop_profile: 店铺配置名
- bill_date: 账单日期
- outcome_amount: 支出金额（退款）
- begin_time/end_time: 时间戳范围
- raw_data: 原始JSON数据

## 使用步骤

### 1. 数据库迁移

首先运行迁移脚本创建新表：

```bash
cd backend
python migrate_add_pdd_bill.py
```

### 2. 配置店铺

编辑 `pdd_api_enhanced.py` 中的店铺配置：

```python
SHOP_PROFILES = [
    "pdd_shop_001",  # 你的Chrome配置文件名
]
```

### 3. 运行爬虫

```bash
cd backend/spiders
python pdd_api_enhanced.py
```

### 4. 操作流程

运行后会依次执行：

#### 步骤1：登录
- 浏览器自动打开拼多多商家后台
- 手动登录（如果需要）
- 按回车继续

#### 步骤2：推广页面
- 自动跳转到推广页面
- 脚本会尝试自动选择日期（默认昨天）
- 如果自动选择失败，请手动选择日期
- 确认日期正确后按回车

#### 步骤3：爬取推广数据
- 自动翻页获取所有推广数据
- 实时显示进度
- 自动保存到 `pdd_ads` 表

#### 步骤4：获取账单数据
- 自动跳转到账单页面
- **手动操作**：
  1. 点击时间范围选择器
  2. 点击【展开高级选项】
  3. 勾选【优惠券结算】和【退款】
  4. 点击【查询】按钮
- 按回车后自动捕获API响应
- 自动保存到 `pdd_bill_records` 表

## 数据查询示例

### 查询推广数据

```python
from models.database import PddTable
from datetime import datetime, timedelta

# 查询昨天的推广数据
yesterday = datetime.now() - timedelta(days=1)
ads = PddTable.select().where(
    PddTable.created_at >= yesterday.replace(hour=0, minute=0, second=0),
    PddTable.is_del == False
)

for ad in ads:
    print(f"商品: {ad.goods_name}, 花费: {ad.spend}, GMV: {ad.gmv}")
```

### 查询账单数据

```python
from models.database import PddBillRecord
from datetime import date, timedelta

# 查询昨天的账单
yesterday = date.today() - timedelta(days=1)
bill = PddBillRecord.get_or_none(
    PddBillRecord.bill_date == yesterday,
    PddBillRecord.shop_profile == "pdd_shop_001"
)

if bill:
    print(f"退款金额: {bill.outcome_amount} 元")
```

## 注意事项

1. **Chrome配置文件**：确保路径正确
   ```python
   f"--user-data-dir=/Users/Aceberg/chrome_profiles/{profile_name}"
   ```

2. **日期选择**：如果自动选择失败，请手动选择后按回车

3. **账单操作**：账单页面的筛选条件必须手动设置，脚本会等待你完成操作

4. **数据去重**：
   - 推广数据按 `ad_id` 去重
   - 账单数据按 `shop_profile + bill_date` 去重

5. **时间戳**：账单查询使用的时间戳是当天 00:00:00 到 23:59:59

## 原始脚本

原始的 `pdd_api.py` 保持不变，如果只需要爬取推广数据而不保存到数据库，可以继续使用原脚本。

## 故障排除

### 问题1：找不到日期选择器
- 手动选择日期后按回车继续

### 问题2：未捕获到账单数据
- 确保完成了所有手动操作步骤
- 等待查询完成后再按回车
- 检查网络请求是否正常

### 问题3：数据库保存失败
- 检查数据库连接
- 运行迁移脚本确保表已创建
- 查看错误日志

## 扩展功能

如需自定义查询日期，修改主函数中的 `target_date`：

```python
# 查询指定日期
target_date = datetime(2024, 2, 1)

# 查询最近7天
for i in range(7):
    target_date = datetime.now() - timedelta(days=i)
    # ... 执行爬取
```
