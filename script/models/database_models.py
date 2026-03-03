# database_models.py - 数据库模型

from peewee import *
from datetime import datetime
import json

from models.database_config import database


class BaseModel(Model):
    class Meta:
        database = database


# PDD 广告推广数据表
class PddTable(BaseModel):
    id = AutoField(primary_key=True)
    
    # 基础广告信息
    ad_id = CharField(index=True)  # 广告ID
    ad_name = CharField(null=True)  # 广告名称
    goods_id = CharField(null=True, index=True)  # 商品ID
    store_id = CharField(null=True, index=True)  # 店铺ID
    
    # 商品信息
    goods_name = CharField(null=True)  # 商品名称

    # 推广费
    orderSpendNetCostPerOrder = FloatField(null=True)  # 推广费
    
    # 数据日期
    data_date = DateField(null=True, index=True)  # 推广数据的日期（年-月-日）

    # 原始JSON数据(可选,用于存储完整的API响应)
    raw_data = TextField(null=True)  # 原始JSON数据
    
    # 系统字段
    is_del = BooleanField(default=False)  # 逻辑删除标志
    created_at = DateTimeField(default=datetime.now)  # 记录创建时间
    updated_at = DateTimeField(default=datetime.now)  # 记录更新时间
    
    class Meta:
        table_name = 'pdd_ads'
        indexes = (
            (('store_id', 'data_date'), False),  # 店铺ID+数据日期索引
            (('ad_id', 'data_date'), True),  # 广告ID+数据日期唯一索引
        )
    
    def set_raw_data(self, data_dict):
        """设置原始JSON数据"""
        self.raw_data = json.dumps(data_dict, ensure_ascii=False)
    
    def get_raw_data(self):
        """获取原始JSON数据"""
        try:
            return json.loads(self.raw_data) if self.raw_data else {}
        except json.JSONDecodeError:
            return {}
    
    def save(self, *args, **kwargs):
        """保存时自动更新updated_at"""
        self.updated_at = datetime.now()
        super().save(*args, **kwargs)


# PDD 账单记录表（退款数据）
class PddBillRecord(BaseModel):
    """
    拼多多账单记录表 - 只保留核心字段
    """
    id = AutoField(primary_key=True)
    shop_id = CharField(max_length=255, index=True, verbose_name="店铺ID")  # 店铺ID
    order_sn = CharField(max_length=255, index=True, verbose_name="订单号")  # 订单号
    amount = FloatField(verbose_name="金额(元)")  # 金额(元)
    bill_date = DateField(verbose_name="账单日期")  # 账单日期
    is_del = BooleanField(default=False, verbose_name="是否删除")  # 软删除标志
    created_at = DateTimeField(default=datetime.now, verbose_name="创建时间")  # 创建时间
    updated_at = DateTimeField(default=datetime.now, verbose_name="更新时间")  # 更新时间

    class Meta:
        table_name = 'pdd_bill_records'
        indexes = (
            (('shop_id', 'order_sn'), True),  # 店铺ID+订单号唯一索引
        )

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        super().save(*args, **kwargs)
