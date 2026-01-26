from peewee import *
from datetime import datetime
import os
import json

# 设置数据库连接
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database.db")
database = SqliteDatabase(db_path)

class BaseModel(Model):
    class Meta:
        database = database


class User(BaseModel):
    username = CharField(unique=True)
    email = CharField(unique=False)
    hashed_password = CharField()  # 使用正确的字段名
    role = CharField(default='user')  # 'admin' or 'user'
    is_active = BooleanField(default=True)
    is_del = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    # 新增关联商品和店铺的字段
    goods_stores = TextField(default='[]')  # 存储JSON格式的[{good_id:'', good_name:''}, {}, ...]

    def set_goods_stores(self, goods_stores_list):
        """设置用户关联的商品和店铺列表"""
        self.goods_stores = json.dumps(goods_stores_list, ensure_ascii=False)

    def get_goods_stores(self):
        """获取用户关联的商品和店铺列表"""
        try:
            return json.loads(self.goods_stores) if self.goods_stores else []
        except json.JSONDecodeError:
            return []
            
    class Meta:
        table_name = 'users'
    
    def __data__(self):
        """自定义序列化方法，将datetime转换为字符串"""
        data = {}
        for field in self._meta.fields.values():
            field_value = getattr(self, field.name)
            if isinstance(field_value, datetime):
                data[field.name] = field_value.strftime('%Y-%m-%d %H:%M:%S')
            else:
                data[field.name] = field_value
        return data

class JushuitanProduct(BaseModel):
    id = AutoField(primary_key=True)
    oid = CharField(null=True)  # 订单ID
    isSuccess = CharField(null=True)  # 是否成功
    msg = CharField(null=True)  # 消息
    purchaseAmt = FloatField(null=True)  # 采购金额
    totalAmt = FloatField(null=True)  # 总金额
    discountAmt = FloatField(null=True)  # 折扣金额
    commission = FloatField(null=True)  # 佣金
    freight = FloatField(null=True)  # 运费
    payAmount = FloatField(null=True)  # 支付金额
    paidAmount = FloatField(null=True)  # 已支付金额
    totalPurchasePriceGoods = FloatField(null=True)  # 商品总采购价
    smallProgramFreight = FloatField(null=True)  # 小程序运费
    totalTransactionPurchasePrice = FloatField(null=True)  # 交易总采购价
    smallProgramCommission = FloatField(null=True)  # 小程序佣金
    smallProgramPaidAmount = FloatField(null=True)  # 小程序已支付金额
    freightCalcRule = CharField(null=True)  # 运费计算规则
    oaId = CharField(null=True)  # OA ID
    soId = CharField(null=True)  # SO ID
    rawSoId = CharField(null=True)  # 原始SO ID
    mergeSoIds = CharField(null=True)  # 合并的SO IDs
    soIdList = CharField(null=True)  # SO ID列表
    supplierCoId = CharField(null=True)  # 供应商公司ID
    supplierName = CharField(null=True)  # 供应商名称
    channelCoId = CharField(null=True)  # 渠道公司ID
    channelName = CharField(null=True)  # 渠道名称
    shopId = CharField(null=True)  # 店铺ID
    shopType = CharField(null=True)  # 店铺类型
    shopName = CharField(null=True)  # 店铺名称
    disInnerOrderGoodsViewList = CharField(null=True)  # 内部订单商品视图列表
    orderTime = CharField(null=True)  # 下单时间
    payTime = CharField(null=True)  # 支付时间
    deliveryDate = CharField(null=True)  # 发货日期
    expressCode = CharField(null=True)  # 快递编码
    expressCompany = CharField(null=True)  # 快递公司
    trackNo = CharField(null=True)  # 快递单号
    orderStatus = CharField(null=True)  # 订单状态
    errorMsg = CharField(null=True)  # 错误消息
    errorDesc = CharField(null=True)  # 错误描述
    labels = CharField(null=True)  # 标签
    buyerMessage = CharField(null=True)  # 买家留言
    remark = CharField(null=True)  # 备注
    sellerFlag = IntegerField(null=True)  # 卖家标记
    updated = CharField(null=True)  # 更新时间
    clientPaidAmt = FloatField(null=True)  # 客户已支付金额
    goodsQty = IntegerField(null=True)  # 商品数量
    goodsAmt = FloatField(null=True)  # 商品金额
    freeAmount = FloatField(null=True)  # 免费金额
    orderType = CharField(null=True)  # 订单类型
    isSplit = BooleanField(null=True)  # 是否拆分
    isMerge = BooleanField(null=True)  # 是否合并
    planDeliveryDate = CharField(null=True)  # 计划发货日期
    deliverTimeLeft = CharField(null=True)  # 剩余发货时间
    printCount = IntegerField(null=True)  # 打印次数
    ioId = CharField(null=True)  # IO ID
    receiverState = CharField(null=True)  # 收件人省份
    receiverCity = CharField(null=True)  # 收件人城市
    receiverDistrict = CharField(null=True)  # 收件人区县
    weight = CharField(null=True)  # 重量
    realWeight = CharField(null=True)  # 实际重量
    wmsCoId = CharField(null=True)  # WMS公司ID
    wmsCoName = CharField(null=True)  # WMS公司名称
    drpAmount = FloatField(null=True)  # 分销金额
    shopSite = CharField(null=True)  # 店铺站点
    isDeliveryPrinted = CharField(null=True)  # 是否打印发货
    fullReceiveData = CharField(null=True)  # 完整收货数据
    fuzzFullReceiverInfo = CharField(null=True)  # 模糊收件人信息
    shopBuyerId = CharField(null=True)  # 店铺买家ID
    logisticsNos = CharField(null=True)  # 物流单号
    openId = CharField(null=True)  # 开放ID
    printedList = CharField(null=True)  # 已打印列表
    note = CharField(null=True)  # 注释
    receiverTown = CharField(null=True)  # 收件人乡镇
    solution = CharField(null=True)  # 解决方案
    orderFrom = CharField(null=True)  # 订单来源
    linkOid = CharField(null=True)  # 关联订单ID
    channelOid = CharField(null=True)  # 渠道订单ID
    isSupplierInitiatedReissueOrExchange = CharField(null=True)  # 供应商发起退换货
    confirmDate = CharField(null=True)  # 确认日期
    topDrpCoIdFrom = CharField(null=True)  # 顶级分销商公司ID
    topDrpOrderId = CharField(null=True)  # 顶级分销商订单ID
    orderIdentity = CharField(null=True)  # 订单身份
    originalSoId = CharField(null=True)  # 原始SO ID
    isVirtualShipment = BooleanField(null=True)  # 是否虚拟发货
    relationshipBySoIdMd5 = CharField(null=True)  # SO ID关系MD5
    online = BooleanField(null=True)  # 是否在线
    data_type = CharField(null=True)  # 数据类型 (regular/cancel)
    is_del = BooleanField(default=False)  # 逻辑删除标志
    created_at = DateTimeField(default=datetime.now)  # 创建时间
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'jushuitan_products'

class Product(BaseModel):
    id = AutoField(primary_key=True)
    goods_id = CharField(unique=True, null=False)
    name = CharField(null=False)
    price = FloatField(null=False)
    platform = CharField(null=False)  # 平台类型
    is_del = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'products'

class Store(BaseModel):
    id = AutoField(primary_key=True)
    name = CharField(null=False)
    platform = CharField(null=False)  # 平台类型
    store_id = CharField(unique=True, null=False)  # 店铺标识符
    is_del = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'stores'



# 商品表：包含所需的所有字段
class Goods(BaseModel):
    id = AutoField(primary_key=True)
    goods_id = CharField(null=True)  # 商品ID
    goods_name = CharField(null=True)  # 商品名称
    store_id = CharField(null=True)  # 店铺ID
    store_name = CharField(null=True)  # 店铺名称
    order_id = CharField(null=True)  # 订单ID
    payment_amount = FloatField(null=True)  # 付款金额
    sales_amount = FloatField(null=True)  # 销售金额
    sales_cost = FloatField(null=True)  # 销售成本
    gross_profit_1_occurred = FloatField(null=True)  # 毛一利润(发生)
    gross_profit_1_rate = FloatField(null=True)  # 毛一利润率
    advertising_expenses = FloatField(null=True)  # 广告费
    advertising_ratio = FloatField(null=True)  # 广告占比
    gross_profit_3 = FloatField(null=True)  # 毛三利润
    gross_profit_3_rate = FloatField(null=True)  # 毛三利润率
    gross_profit_4 = FloatField(null=True)  # 毛四利润
    gross_profit_4_rate = FloatField(null=True)  # 毛四利润率
    net_profit = FloatField(null=True)  # 净利润
    net_profit_rate = FloatField(null=True)  # 净利率
    is_del = BooleanField(default=False)  # 逻辑删除标志
    creator = CharField(null=True)  # 创建人
    created_at = DateTimeField(default=datetime.now)  # 创建时间
    updated_at = DateTimeField(default=datetime.now)  # 更新时间

    class Meta:
        table_name = 'goods'




# 创建所有表
def create_tables():
    with database:
        database.create_tables([User, JushuitanProduct, Product, Store, Goods])
