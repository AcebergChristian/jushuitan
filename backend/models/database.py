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
    email = CharField()
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
    refund_amount = FloatField(null=True)  # 退款金额
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
    goodorder_time = DateTimeField(null=True)  # 商品订单时间
    created_at = DateTimeField(default=datetime.now)  # 创建时间
    updated_at = DateTimeField(default=datetime.now)  # 更新时间

    class Meta:
        table_name = 'goods'


# 店铺表：以店铺为主键，聚合所有金额字段
class Store(BaseModel):
    id = AutoField(primary_key=True)
    store_id = CharField(unique=True)  # 店铺ID，唯一标识
    store_name = CharField(null=True)  # 店铺名称
    total_payment_amount = FloatField(default=0.0)  # 总付款金额
    total_sales_amount = FloatField(default=0.0)  # 总销售金额
    total_refund_amount = FloatField(default=0.0)  # 总退款金额
    total_sales_cost = FloatField(default=0.0)  # 总销售成本
    total_gross_profit_1_occurred = FloatField(default=0.0)  # 总毛一利润(发生)
    avg_gross_profit_1_rate = FloatField(default=0.0)  # 平均毛一利润率
    total_advertising_expenses = FloatField(default=0.0)  # 总广告费
    avg_advertising_ratio = FloatField(default=0.0)  # 平均广告占比
    total_gross_profit_3 = FloatField(default=0.0)  # 总毛三利润
    avg_gross_profit_3_rate = FloatField(default=0.0)  # 平均毛三利润率
    total_gross_profit_4 = FloatField(default=0.0)  # 总毛四利润
    avg_gross_profit_4_rate = FloatField(default=0.0)  # 平均毛四利润率
    total_net_profit = FloatField(default=0.0)  # 总净利润
    avg_net_profit_rate = FloatField(default=0.0)  # 平均净利率
    goods_count = IntegerField(default=0)  # 商品数量
    order_count = IntegerField(default=0)  # 订单数量
    is_del = BooleanField(default=False)  # 逻辑删除标志
    creator = CharField(null=True)  # 创建人
    last_order_time = DateTimeField(null=True)  # 最后订单时间
    created_at = DateTimeField(default=datetime.now)  # 创建时间
    updated_at = DateTimeField(default=datetime.now)  # 更新时间

    class Meta:
        table_name = 'stores'



class JushuitanCancelProduct(BaseModel):
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
        table_name = 'jushuitan_cancel_products'



class RefundRecord(BaseModel):
    """
    退款记录表
    """
    id = AutoField(primary_key=True)
    good_id = CharField(max_length=255, null=True, verbose_name="商品ID")  # 商品ID
    store_id = CharField(max_length=255, null=True, verbose_name="店铺ID")  # 店铺ID
    order_id = CharField(max_length=255, null=True, verbose_name="订单ID")  # 订单ID
    refund_amount = FloatField(default=0.0, verbose_name="退款金额")  # 退款金额
    refund_time = DateTimeField(null=True, verbose_name="退款时间")  # 退款时间
    is_del = BooleanField(default=False, verbose_name="是否删除")  # 软删除标志
    creator = CharField(max_length=255, null=True, verbose_name="创建人")  # 创建人
    created_at = DateTimeField(default=datetime.now, verbose_name="创建时间")  # 创建时间
    updated_at = DateTimeField(default=datetime.now, verbose_name="更新时间")  # 更新时间

    class Meta:
        table_name = 'refund_records'

    def save(self, *args, **kwargs):
        # 自动更新更新时间
        self.updated_at = datetime.now()
        super().save(*args, **kwargs
)


# pdd table - 拼多多广告推广数据表
class PddTable(BaseModel):
    id = AutoField(primary_key=True)
    
    # 基础广告信息
    ad_id = CharField(unique=True, index=True)  # 广告ID
    ad_name = CharField(null=True)  # 广告名称
    ad_status = IntegerField(null=True)  # 广告状态
    plan_id = CharField(null=True, index=True)  # 计划ID
    goods_id = CharField(null=True, index=True)  # 商品ID
    mall_id = CharField(null=True, index=True)  # 店铺ID
    
    # 商品信息
    goods_name = CharField(null=True)  # 商品名称
    thumb_url = TextField(null=True)  # 商品缩略图URL
    cat_id = CharField(null=True)  # 类目ID
    min_on_sale_group_price = FloatField(null=True)  # 最低在售拼团价
    
    # 出价和预算信息
    bid_type = IntegerField(null=True)  # 出价类型
    agent_bid = FloatField(null=True)  # 代理出价
    optimization_bid = FloatField(null=True)  # 优化出价
    target_roi = FloatField(null=True)  # 目标ROI
    daily_cost = FloatField(null=True)  # 日消耗
    max_cost = FloatField(null=True)  # 最大消耗
    cost_type = IntegerField(null=True)  # 消耗类型
    
    # 建议信息
    suggest_value = FloatField(null=True)  # 建议出价值
    suggest_level = IntegerField(null=True)  # 建议等级
    suggest_min_value = FloatField(null=True)  # 建议最小值
    suggest_max_value = FloatField(null=True)  # 建议最大值
    suggest_max_cost = FloatField(null=True)  # 建议最大消耗
    
    # 报表数据 - 核心指标
    impression = IntegerField(default=0)  # 曝光量
    click = IntegerField(default=0)  # 点击量
    spend = FloatField(default=0.0)  # 花费
    ctr = FloatField(default=0.0)  # 点击率
    cvr = FloatField(default=0.0)  # 转化率
    
    # 订单相关
    order_num = IntegerField(default=0)  # 订单数
    direct_order_num = IntegerField(default=0)  # 直接订单数
    indirect_order_num = IntegerField(default=0)  # 间接订单数
    net_order_num = IntegerField(default=0)  # 净订单数
    settlement_order = IntegerField(default=0)  # 结算订单数
    cost_per_order = FloatField(default=0.0)  # 订单成本
    
    # GMV相关
    gmv = FloatField(default=0.0)  # GMV
    direct_gmv = FloatField(default=0.0)  # 直接GMV
    indirect_gmv = FloatField(default=0.0)  # 间接GMV
    net_gmv = FloatField(default=0.0)  # 净GMV
    settlement_gmv = FloatField(default=0.0)  # 结算GMV
    net_gmv_rate = FloatField(default=0.0)  # 净GMV率
    settlement_gmv_rate = FloatField(default=0.0)  # 结算GMV率
    
    # 退款相关
    refund_order_30d = IntegerField(default=0)  # 30天退款订单数
    refund_gmv_30d = FloatField(default=0.0)  # 30天退款GMV
    refund_order_rate_30d = FloatField(default=0.0)  # 30天退款订单率
    refund_gmv_rate_30d = FloatField(default=0.0)  # 30天退款GMV率
    exempt_refund_order_30d = IntegerField(default=0)  # 30天免责退款订单数
    exempt_refund_gmv_30d = FloatField(default=0.0)  # 30天免责退款GMV
    exempt_refund_order_rate_30d = FloatField(default=0.0)  # 30天免责退款订单率
    exempt_refund_gmv_rate_30d = FloatField(default=0.0)  # 30天免责退款GMV率
    quick_refund_order_num = IntegerField(default=0)  # 快速退款订单数
    quick_refund_gmv = FloatField(default=0.0)  # 快速退款GMV
    
    # ROI相关
    order_spend_roi_unified = FloatField(default=0.0)  # 统一订单花费ROI
    order_spend_net_roi = FloatField(default=0.0)  # 净订单花费ROI
    settlement_roi = FloatField(default=0.0)  # 结算ROI
    
    # 平均金额
    avg_pay_amount = FloatField(default=0.0)  # 平均支付金额
    avg_direct_pay_amount = FloatField(default=0.0)  # 平均直接支付金额
    avg_indirect_pay_amount = FloatField(default=0.0)  # 平均间接支付金额
    
    # 多目标数据
    multi_goal_goods_fav_num = IntegerField(default=0)  # 商品收藏数
    multi_goal_mall_fav_num = IntegerField(default=0)  # 店铺收藏数
    multi_goal_inquiry_num = IntegerField(default=0)  # 咨询数
    multi_goal_cost_per_goods_fav = FloatField(default=0.0)  # 商品收藏成本
    multi_goal_cost_per_mall_fav = FloatField(default=0.0)  # 店铺收藏成本
    multi_goal_cost_per_inquiry = FloatField(default=0.0)  # 咨询成本
    
    # 状态和标签
    data_operate_status = IntegerField(null=True)  # 数据操作状态
    data_accumulation_status = IntegerField(null=True)  # 数据积累状态
    scenes_type = IntegerField(null=True)  # 场景类型
    scenes_mode = IntegerField(null=True)  # 场景模式
    ad_tag_code_list = TextField(null=True)  # 广告标签代码列表(JSON)
    
    # 排除退款相关
    exclude_refund_status = IntegerField(null=True)  # 排除退款状态
    exclude_refund_force_switch_finish_time = DateTimeField(null=True)  # 排除退款强制切换完成时间
    
    # 广告组信息
    ad_group_id = CharField(null=True)  # 广告组ID
    ad_group_name = CharField(null=True)  # 广告组名称
    
    # 时间信息
    create_time = DateTimeField(null=True)  # 创建时间
    
    # 其他标志
    is_stick = BooleanField(default=False)  # 是否置顶
    is_traffic_card_ad = BooleanField(default=False)  # 是否流量卡广告
    disable_switch_to_roi = BooleanField(default=False)  # 禁用切换到ROI
    
    # 预算变更
    budget_changed_number_today = IntegerField(default=0)  # 今日预算变更次数
    available_budget_change_number_today = IntegerField(default=0)  # 今日可用预算变更次数
    
    # 原始JSON数据(可选,用于存储完整的API响应)
    raw_data = TextField(null=True)  # 原始JSON数据
    
    # 系统字段
    is_del = BooleanField(default=False)  # 逻辑删除标志
    created_at = DateTimeField(default=datetime.now)  # 记录创建时间
    updated_at = DateTimeField(default=datetime.now)  # 记录更新时间
    
    class Meta:
        table_name = 'pdd_ads'
    
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




# 创建所有表
def create_tables():
    with database:
        database.create_tables([User, JushuitanProduct, Goods, Store, JushuitanCancelProduct, RefundRecord, PddTable])





