from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from .. import schemas
from ..services import product_service
from ..database import get_db
from ..models.database import JushuitanProduct, Goods
from .auth import get_current_user


import sqlite3
import os
import json
from datetime import datetime, date, timedelta

from ..spiders.jushuitan_api import get_all_jushuitan_orders

router = APIRouter()


# 聚水潭数据相关路由
@router.get("/jushuitan_products/")
def read_jushuitan_products(skip: int = 0, limit: int = 100, search: str = ""):
    """获取聚水潭商品数据列表"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database.db")
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="数据库不存在")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 首先找出最新的日期
    cursor.execute('SELECT MAX(created_at) FROM jushuitan_products WHERE is_del = 0')
    latest_date_result = cursor.fetchone()
    if latest_date_result and latest_date_result[0]:
        latest_date = latest_date_result[0].split(' ')[0]  # 取日期部分，去掉时间
        
        # 查询最新日期的数据总数
        if search:
            cursor.execute('''SELECT COUNT(*) FROM jushuitan_products 
                             WHERE is_del = 0 
                             AND substr(created_at, 1, 10) = ?
                             AND disInnerOrderGoodsViewList LIKE ?''', (latest_date, f'%{search}%'))
        else:
            cursor.execute('SELECT COUNT(*) FROM jushuitan_products WHERE is_del = 0 AND substr(created_at, 1, 10) = ?', (latest_date,))
        
        total_count = cursor.fetchone()[0]
        
        # 查询最新日期的数据
        if search:
            cursor.execute('''SELECT * FROM jushuitan_products 
                             WHERE is_del = 0 
                             AND substr(created_at, 1, 10) = ?
                             AND disInnerOrderGoodsViewList LIKE ? 
                             ORDER BY created_at DESC
                             LIMIT ? OFFSET ?''', (latest_date, f'%{search}%', limit, skip))
        else:
            cursor.execute('SELECT * FROM jushuitan_products WHERE is_del = 0 AND substr(created_at, 1, 10) = ? ORDER BY created_at DESC LIMIT ? OFFSET ?', (latest_date, limit, skip))
    else:
        # 如果没有数据，返回空结果
        total_count = 0
        cursor.execute('SELECT * FROM jushuitan_products WHERE 1=0')  # 返回空结果集
    
    records = cursor.fetchall()
    
    # 获取列名
    column_names = [description[0] for description in cursor.description]
    
    # 将结果转换为字典列表
    result = []
    for row in records:
        record_dict = {}
        for i, col_name in enumerate(column_names):
            record_dict[col_name] = row[i]
        result.append(record_dict)
    
    conn.close()
    
    # 返回包含数据和总数的对象
    return {
        "data": result,
        "total": total_count,
        "skip": skip,
        "limit": limit
    }

# 根据ID获取聚水潭商品数据
@router.get("/jushuitan_products/{record_id}")
def read_jushuitan_product(record_id: int):
    """根据ID获取聚水潭商品数据"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database.db")
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="数据库不存在")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM jushuitan_products WHERE id = ? AND is_del = 0', (record_id,))
    record = cursor.fetchone()
    
    if record is None:
        conn.close()
        raise HTTPException(status_code=404, detail="聚水潭数据不存在")
    
    # 获取列名
    column_names = [description[0] for description in cursor.description]
    
    # 将结果转换为字典
    record_dict = {}
    for i, col_name in enumerate(column_names):
        record_dict[col_name] = record[i]
    
    conn.close()
    return record_dict

# 根据数据类型获取聚水潭商品数据
@router.get("/jushuitan_products/type/{data_type}")
def read_jushuitan_products_by_type(data_type: str, skip: int = 0, limit: int = 100):
    """根据数据类型获取聚水潭商品数据"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database.db")
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="数据库不存在")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 首先找出最新日期的数据
    cursor.execute('SELECT MAX(created_at) FROM jushuitan_products WHERE is_del = 0 AND data_type = ?', (data_type,))
    latest_date_result = cursor.fetchone()
    if latest_date_result and latest_date_result[0]:
        latest_date = latest_date_result[0].split(' ')[0]  # 取日期部分，去掉时间
        
        # 查询最新日期的数据
        cursor.execute('SELECT * FROM jushuitan_products WHERE data_type = ? AND is_del = 0 AND substr(created_at, 1, 10) = ? ORDER BY created_at DESC LIMIT ? OFFSET ?', (data_type, latest_date, limit, skip))
    else:
        # 如果没有数据，返回空结果
        cursor.execute('SELECT * FROM jushuitan_products WHERE 1=0')  # 返回空结果集
    
    records = cursor.fetchall()
    
    # 获取列名
    column_names = [description[0] for description in cursor.description]
    
    # 将结果转换为字典列表
    result = []
    for row in records:
        record_dict = {}
        for i, col_name in enumerate(column_names):
            record_dict[col_name] = row[i]
        result.append(record_dict)
    
    conn.close()
    return result





# 点击获取同步数据进表里
@router.post("/sync_jushuitan_data")
def sync_jushuitan_data(request: dict = None):
    """同步聚水潭数据到数据库，根据oid字段处理重复数据"""
    
    # 获取请求体中的同步日期
    sync_date_str = request.get('sync_date') if request else None
    sync_date = None
    if sync_date_str:
        try:
            sync_date = datetime.strptime(sync_date_str, '%Y-%m-%d').date()
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式不正确，请使用 YYYY-MM-DD 格式")

    # 获取聚水潭API数据
    api_response = get_all_jushuitan_orders(sync_date=sync_date)
    if not api_response or 'data' not in api_response:
        raise HTTPException(status_code=400, detail="获取聚水潭API数据失败")
    
    new_data_list = api_response.get('data', [])
    
    if not new_data_list:
        return {"message": "没有获取到新的聚水潭数据"}
    
    # 使用Peewee ORM进行数据库操作
    from ..models.database import JushuitanProduct
    
    # 获取系统当前日期
    current_system_date = datetime.now().strftime('%Y-%m-%d')
    
    processed_count = 0
    
    with get_db() as db:
        for item in new_data_list:
            oid = item.get('oid')
            
            if oid:  # 如果oid存在
                # 查找数据库中相同oid的记录
                existing_records = JushuitanProduct.select().where(
                    JushuitanProduct.oid == oid
                )

                # 检查是否存在同一天（系统当前日期）的记录 - 检查创建时间而不是订单时间
                same_day_record_exists = False
                for record in existing_records:
                    # 检查记录的创建时间是否为当天
                    record_created_date = record.created_at.strftime('%Y-%m-%d') if hasattr(record.created_at, 'strftime') else str(record.created_at).split(' ')[0]

                    # 如果是系统当前日期，则标记为需要删除
                    if current_system_date == record_created_date:
                        same_day_record_exists = True
                        break

                # 如果存在同一天的记录，则删除它们
                if same_day_record_exists:
                    for record in existing_records:
                        record_created_date = record.created_at.strftime('%Y-%m-%d') if hasattr(record.created_at, 'strftime') else str(record.created_at).split(' ')[0]
                        if current_system_date == record_created_date:
                            record.delete_instance()
                
                # 插入新的记录
                JushuitanProduct.create(
                    oid=item.get('oid'),
                    isSuccess=item.get('isSuccess'),
                    msg=item.get('msg'),
                    purchaseAmt=item.get('purchaseAmt'),
                    totalAmt=item.get('totalAmt'),
                    discountAmt=item.get('discountAmt'),
                    commission=item.get('commission'),
                    freight=item.get('freight'),
                    payAmount=item.get('payAmount'),
                    paidAmount=item.get('paidAmount'),
                    totalPurchasePriceGoods=item.get('totalPurchasePriceGoods'),
                    smallProgramFreight=item.get('smallProgramFreight'),
                    totalTransactionPurchasePrice=item.get('totalTransactionPurchasePrice'),
                    smallProgramCommission=item.get('smallProgramCommission'),
                    smallProgramPaidAmount=item.get('smallProgramPaidAmount'),
                    freightCalcRule=item.get('freightCalcRule'),
                    oaId=item.get('oaId'),
                    soId=item.get('soId'),
                    rawSoId=item.get('rawSoId'),
                    mergeSoIds=item.get('mergeSoIds'),
                    soIdList=str(item.get('soIdList', [])),
                    supplierCoId=item.get('supplierCoId'),
                    supplierName=item.get('supplierName'),
                    channelCoId=item.get('channelCoId'),
                    channelName=item.get('channelName'),
                    shopId=item.get('shopId'),
                    shopType=item.get('shopType'),
                    shopName=item.get('shopName'),
                    disInnerOrderGoodsViewList=str(item.get('disInnerOrderGoodsViewList', [])),
                    orderTime=item.get('orderTime'),
                    payTime=item.get('payTime'),
                    deliveryDate=item.get('deliveryDate'),
                    expressCode=item.get('expressCode'),
                    expressCompany=item.get('expressCompany'),
                    trackNo=item.get('trackNo'),
                    orderStatus=item.get('orderStatus'),
                    errorMsg=item.get('errorMsg'),
                    errorDesc=item.get('errorDesc'),
                    labels=str(item.get('labels', [])),
                    buyerMessage=item.get('buyerMessage'),
                    remark=item.get('remark'),
                    sellerFlag=item.get('sellerFlag'),
                    updated=item.get('updated'),
                    clientPaidAmt=item.get('clientPaidAmt'),
                    goodsQty=item.get('goodsQty'),
                    goodsAmt=item.get('goodsAmt'),
                    freeAmount=item.get('freeAmount'),
                    orderType=item.get('orderType'),
                    isSplit=item.get('isSplit', False),
                    isMerge=item.get('isMerge', False),
                    planDeliveryDate=item.get('planDeliveryDate'),
                    deliverTimeLeft=item.get('deliverTimeLeft'),
                    printCount=item.get('printCount'),
                    ioId=item.get('ioId'),
                    receiverState=item.get('receiverState'),
                    receiverCity=item.get('receiverCity'),
                    receiverDistrict=item.get('receiverDistrict'),
                    weight=item.get('weight'),
                    realWeight=item.get('realWeight'),
                    wmsCoId=item.get('wmsCoId'),
                    wmsCoName=item.get('wmsCoName'),
                    drpAmount=item.get('drpAmount'),
                    shopSite=item.get('shopSite'),
                    isDeliveryPrinted=item.get('isDeliveryPrinted'),
                    fullReceiveData=item.get('fullReceiveData'),
                    fuzzFullReceiverInfo=item.get('fuzzFullReceiverInfo'),
                    shopBuyerId=item.get('shopBuyerId'),
                    logisticsNos=item.get('logisticsNos'),
                    openId=item.get('openId'),
                    printedList=item.get('printedList'),
                    note=item.get('note'),
                    receiverTown=item.get('receiverTown'),
                    solution=item.get('solution'),
                    orderFrom=item.get('orderFrom'),
                    linkOid=item.get('linkOid'),
                    channelOid=item.get('channelOid'),
                    isSupplierInitiatedReissueOrExchange=item.get('isSupplierInitiatedReissueOrExchange'),
                    confirmDate=item.get('confirmDate'),
                    topDrpCoIdFrom=item.get('topDrpCoIdFrom'),
                    topDrpOrderId=item.get('topDrpOrderId'),
                    orderIdentity=item.get('orderIdentity'),
                    originalSoId=item.get('originalSoId'),
                    isVirtualShipment=item.get('isVirtualShipment', False),
                    relationshipBySoIdMd5=item.get('relationshipBySoIdMd5'),
                    online=item.get('online', False),
                    data_type='regular' if item.get('orderStatus') not in ['Cancelled', 'Refunded', 'Closed'] else 'cancel',
                    is_del=False
                )
                processed_count += 1
    
    return {
        "message": f"成功同步聚水潭数据，处理了 {processed_count} 条记录",
        "processed_count": processed_count
    }


# 同步订单数据 - 查出商品数 - insert到goods表
@router.post("/sync_goods/")
def sync_goods(request: dict = None):
    """
    同步订单数据中的商品信息到goods表
    - 提取disInnerOrderGoodsViewList中的商品数据
    - 按shopIid聚合相同商品的金额
    - 计算各种利润指标
    - 支持按指定日期同步数据
    """
    from datetime import datetime, date
    from ..models.database import Goods, JushuitanProduct
    from ..spiders.jushuitan_api import get_all_jushuitan_orders
    
    try:
        # 检查是否提供了同步日期
        sync_date_str = request.get('sync_date') if request else None
        sync_date = None
        if sync_date_str:
            try:
                sync_date = datetime.strptime(sync_date_str, '%Y-%m-%d').date()
            except ValueError:
                raise HTTPException(status_code=400, detail="日期格式不正确，请使用 YYYY-MM-DD 格式")

        # 直接从数据库中的JushuitanProduct表获取订单数据
        # 查询未删除的订单记录
        order_query = JushuitanProduct.select().where(JushuitanProduct.is_del == False)
        
        # 如果指定了同步日期，则添加日期筛选
        if sync_date:
            # 将sync_date转换为当天的开始和结束时间
            start_of_day = datetime.combine(sync_date, datetime.min.time())
            end_of_day = datetime.combine(sync_date, datetime.max.time())
            order_query = order_query.where(
                (JushuitanProduct.created_at >= start_of_day) & 
                (JushuitanProduct.created_at <= end_of_day)
            )
        
        orders = list(order_query)
        
        # 如果数据库中没有订单数据，再从API获取
        if not orders:
            api_response = get_all_jushuitan_orders(sync_date=sync_date)
            if not api_response or 'data' not in api_response:
                raise HTTPException(status_code=400, detail="获取聚水潭API数据失败或数据库中没有可用订单数据")
            orders = api_response.get('data', [])

        # 用于存储商品数据的字典，以shopIid和订单时间为唯一键进行区分
        goods_dict = {}

        for order in orders:
            # 如果是从数据库获取的订单对象，需要转换为字典
            if hasattr(order, 'disInnerOrderGoodsViewList'):
                # 从数据库获取的订单对象
                order_dict = {
                    'oid': order.oid,
                    'payAmount': order.payAmount,
                    'paidAmount': order.paidAmount,
                    'drpAmount': order.drpAmount,
                    'shopId': order.shopId,
                    'shopName': order.shopName,
                    'orderTime': order.orderTime,
                    'disInnerOrderGoodsViewList': order.disInnerOrderGoodsViewList,
                    'created_at': order.created_at
                }
                order_obj = order
            else:
                # 从API获取的订单字典
                order_dict = order
                order_obj = None
            
            try:
                # 如果指定了同步日期，则只处理该日期的订单
                if sync_date and order_obj is None:  # 只有从API获取的订单需要检查时间
                    order_time_str = order_dict.get('orderTime')
                    if order_time_str:
                        try:
                            # 解析订单时间，提取日期部分
                            if 'T' in order_time_str:
                                order_datetime = datetime.fromisoformat(order_time_str.replace('Z', '+00:00'))
                                order_date = order_datetime.date()
                            else:
                                # 如果只是日期字符串
                                order_date = datetime.strptime(order_time_str.split(' ')[0], '%Y-%m-%d').date()
                            
                            # 只处理指定日期的订单
                            if order_date != sync_date:
                                continue
                        except:
                            # 如果解析失败，跳过该订单
                            continue
                
                payAmount = float(order_dict.get('payAmount', 0) or 0)
                paidAmount = float(order_dict.get('paidAmount', 0) or 0)
                drpAmount = float(order_dict.get('drpAmount', 0) or 0)

                # 解析disInnerOrderGoodsViewList字段
                goods_list_raw = order_dict.get('disInnerOrderGoodsViewList')
                
                # 解析JSON字符串
                import json
                try:
                    if isinstance(goods_list_raw, str):
                        goods_list = json.loads(goods_list_raw)
                    else:
                        goods_list = goods_list_raw
                except json.JSONDecodeError:
                    print(f"无法解析disInnerOrderGoodsViewList: {goods_list_raw}")
                    continue
                
                # 根据项目规范，确保目标字段为list类型
                if not isinstance(goods_list, list):
                    if goods_list is None:
                        goods_list = []
                    else:
                        goods_list = [goods_list]  # 强制转换为list
                
                # 遍历订单中的每个商品
                for goods_item in goods_list:
                    if not isinstance(goods_item, dict):
                        continue
                    
                    # 获取商品的关键信息 - 使用正确的英文字段名
                    shop_iid = goods_item.get('shopIid')
                    if not shop_iid:  # 如果没有shopIid，则跳过
                        continue
                    
                    # 使用shopIid + 订单时间作为唯一键，保留订单时间维度
                    order_time_str = order_dict.get('orderTime')
                    order_datetime = None
                    if order_time_str:
                        try:
                            if 'T' in order_time_str:
                                order_datetime = datetime.fromisoformat(order_time_str.replace('Z', '+00:00'))
                            else:
                                # 如果只是日期时间字符串
                                order_datetime = datetime.strptime(order_time_str, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            try:
                                # 尝试其他常见格式
                                order_datetime = datetime.strptime(order_time_str, '%Y-%m-%d')
                            except ValueError:
                                # 如果解析失败，使用当前时间
                                order_datetime = datetime.now()
                    else:
                        # 如果没有订单时间，使用当前时间
                        order_datetime = datetime.now()
                    
                    # 使用shopIid + 订单时间作为唯一键
                    unique_key = f"{shop_iid}_{order_datetime.strftime('%Y%m%d%H%M%S')}"
                    
                    # 获取商品其他信息 - 使用正确的英文字段名
                    item_name = goods_item.get('itemName', '未知商品')
                    item_code = goods_item.get('itemCode', '')
                    supplier_name = goods_item.get('supplierName', '')
                    pic = goods_item.get('pic', '')
                    properties = goods_item.get('properties', '')
                    price = float(goods_item.get('price', 0) or 0)
                    total_price = float(goods_item.get('totalPrice', 0) or 0)
                    item_count = int(goods_item.get('itemCount', 1) or 1)
                    
                    # 如果指定了同步日期，使用该日期，否则使用订单创建日期
                    if sync_date:
                        order_created_at = datetime.combine(sync_date, datetime.min.time())
                    else:
                        # 获取订单创建时间并转换为日期对象
                        if order_obj:
                            order_created_at = order_obj.created_at
                        else:
                            order_created_at_str = order_dict.get('created_at')
                            if order_created_at_str:
                                if isinstance(order_created_at_str, str):
                                    order_created_at = datetime.fromisoformat(order_created_at_str.replace('Z', '+00:00'))
                                elif isinstance(order_created_at_str, datetime):
                                    order_created_at = order_created_at_str
                                else:
                                    order_created_at = datetime.now()
                            else:
                                order_created_at = datetime.now()
                    
                    # 初始化商品数据结构
                    goods_dict[unique_key] = {
                        'goods_id': shop_iid,  # 商品ID使用shopIid
                        'goods_name': item_name,
                        'store_id': order_dict.get('shopId') or '',
                        'store_name': order_dict.get('shopName') or '未知店铺',
                        'order_id': order_dict.get('oid') or '',
                        'payment_amount': paidAmount,  # 使用订单的paidAmount
                        'sales_amount': payAmount,    # 使用订单的payAmount
                        'sales_cost': drpAmount,      # 使用订单的drpAmount
                        'item_count': item_count,
                        'price': price,
                        'total_price': total_price,
                        'supplier_name': supplier_name,
                        'pic': pic,
                        'item_code': item_code,
                        'properties': properties,
                        'creator': 'system',
                        'created_at': order_created_at,
                        'goodorder_time': order_datetime,  # 保留订单时间
                        'updated_at': datetime.now()
                    }
        
            except Exception as e:
                print(f"Error processing order {order_dict.get('id') if order_dict else 'unknown'}: {e}")

        # 删除之前同步的相同日期的数据（避免重复）
        if sync_date:
            start_of_day = datetime.combine(sync_date, datetime.min.time())
            end_of_day = datetime.combine(sync_date, datetime.max.time())
            Goods.delete().where(
                (Goods.goodorder_time >= start_of_day) & 
                (Goods.goodorder_time <= end_of_day)
            ).execute()
        else:
            # 如果没有指定日期，删除所有数据重新插入（或可以考虑更精确的清理策略）
            Goods.delete().execute()

        # 插入新的商品记录
        for full_key, goods_data in goods_dict.items():
            new_good = Goods.create(**goods_data)

        # 计算利润相关指标并更新
        all_new_goods = list(Goods.select())
        
        for good_record in all_new_goods:
            # 确保所有数值字段都不为None
            sales_amount = good_record.sales_amount or 0.0
            cost_amount = good_record.sales_cost or 0.0
            
            # 计算各种利润指标
            gross_profit_1_occurred = sales_amount - cost_amount
            gross_profit_1_rate = round(((sales_amount - cost_amount) / sales_amount) * 100, 2) if sales_amount > 0 else 0
            
            # 获取广告费用，如果为None则默认为0
            ad_cost = getattr(good_record, 'advertising_expenses', 0) or 0
            advertising_ratio = round((ad_cost / sales_amount) * 100, 2) if sales_amount > 0 else 0
            
            gross_profit_3 = sales_amount - cost_amount - ad_cost
            gross_profit_3_rate = round(((sales_amount - cost_amount - ad_cost) / sales_amount) * 100, 2) if sales_amount > 0 else 0
            
            gross_profit_4 = sales_amount - cost_amount - ad_cost  # 可能还有其他费用
            gross_profit_4_rate = round(((sales_amount - cost_amount - ad_cost) / sales_amount) * 100, 2) if sales_amount > 0 else 0
            
            net_profit = sales_amount - cost_amount - ad_cost  # 净利润可能还要扣除其他费用
            net_profit_rate = round(((sales_amount - cost_amount - ad_cost) / sales_amount) * 100, 2) if sales_amount > 0 else 0
            
            # 更新利润相关字段
            good_record.gross_profit_1_occurred = gross_profit_1_occurred
            good_record.gross_profit_1_rate = gross_profit_1_rate
            good_record.advertising_ratio = advertising_ratio
            good_record.gross_profit_3 = gross_profit_3
            good_record.gross_profit_3_rate = gross_profit_3_rate
            good_record.gross_profit_4 = gross_profit_4
            good_record.gross_profit_4_rate = gross_profit_4_rate
            good_record.net_profit = net_profit
            good_record.net_profit_rate = net_profit_rate
            good_record.updated_at = datetime.now()
            good_record.save()
        
        # 统计处理结果
        processed_count = len(goods_dict)
        
        # 根据是否指定了同步日期返回不同的消息
        if sync_date:
            message_text = f"成功同步指定日期 {sync_date_str} 的商品数据，处理了 {processed_count} 条商品记录"
        else:
            message_text = f"成功同步商品数据，处理了 {processed_count} 条商品记录"

        return {
            "message": message_text
        }
        
    except Exception as e:
        print(f"同步商品数据时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"同步商品数据失败: {str(e)}")











# 商品台账查询接口 - 支持分页和模糊查询
@router.get("/goods/")
def get_goods_list(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回的记录数"),
    search: str = Query("", description="商品名称模糊查询")
):
    """
    获取商品列表，支持分页和商品名称模糊查询
    """
    from ..models.database import Goods
    
    try:
        # 构建查询
        query = Goods.select()
        
        # 如果有搜索条件，添加模糊查询
        if search:
            query = query.where(Goods.goods_name.contains(search))
        
        # 排除已删除的记录
        query = query.where(Goods.is_del == False)  # False
        
        # 按创建时间降序排列
        query = query.order_by(Goods.created_at.desc())

        # 获取总数
        total_count = query.count()
        
        # 应用分页
        goods_list = query.offset(skip).limit(limit).execute()
        
        # 转换为字典列表
        result = []
        for good in goods_list:
            good_dict = {
                'id': good.id,
                'goods_id': good.goods_id,
                'goods_name': good.goods_name,
                'store_id': good.store_id,
                'store_name': good.store_name,
                'order_id': good.order_id,
                'payment_amount': good.payment_amount,
                'sales_amount': good.sales_amount,
                'sales_cost': good.sales_cost,
                'gross_profit_1_occurred': good.gross_profit_1_occurred,
                'gross_profit_1_rate': good.gross_profit_1_rate,
                'advertising_expenses': good.advertising_expenses,
                'gross_profit_3': good.gross_profit_3,
                'gross_profit_3_rate': good.gross_profit_3_rate,
                'gross_profit_4': good.gross_profit_4,
                'gross_profit_4_rate': good.gross_profit_4_rate,
                'net_profit': good.net_profit,
                'net_profit_rate': good.net_profit_rate,
                'is_del': good.is_del,
                'creator': good.creator,
                'goodorder_time': good.goodorder_time.strftime("%Y-%m-%d %H:%M:%S"),
                'created_at': good.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                'updated_at': good.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            result.append(good_dict)
        
        return {
            "data": result,
            "total": total_count,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        print(f"获取商品列表时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取商品列表失败: {str(e)}")






# 店铺管理分页查询接口
@router.get("/stores_data/")
def get_user_goods_stores_data(
    start_date: str = Query(None, description="开始日期，格式：YYYY-MM-DD"),
    end_date: str = Query(None, description="结束日期，格式：YYYY-MM-DD"),
    current_user = Depends(get_current_user)
):
    """
    根据当前登录用户的goods_stores字段查询商品及店铺数据
    管理员可查看所有数据，普通用户只能查看自己的数据
    按店铺维度返回汇总数据
    返回包含销售金额、成本、利润等统计信息的数据
    支持按日期范围查询
    """
    from ..models.database import Goods, User
    from datetime import datetime
    
    # 判断是否为管理员
    is_admin = current_user.role == 'admin'
    
    store_data = []
    
    # 构建查询条件
    query_conditions = [Goods.is_del == False]
    
    # 如果提供了日期范围，则添加日期筛选条件
    if start_date and end_date:
        try:
            # 正确解析 YYYY-MM-DD 格式的日期
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            # 将开始日期设置为当天的开始（00:00:00）
            start_dt = start_dt.replace(hour=0, minute=0, second=0)
            # 将结束日期设置为当天的结束（00:00:00），以包含整个结束日期
            end_dt = end_dt.replace(hour=0, minute=0, second=0)
            # 使用goodorder_time字段进行日期筛选（这是实际的订单时间）
            query_conditions.append((Goods.goodorder_time >= start_dt) & (Goods.goodorder_time <= end_dt))
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式不正确，请使用 YYYY-MM-DD 格式")
    
    if is_admin:
        # 管理员查看所有商品数据，按店铺分组
        goods_records = Goods.select().where(*query_conditions)
        
        # 按店铺ID分组
        stores_dict = {}
        for record in goods_records:
            store_id = record.store_id
            if store_id not in stores_dict:
                stores_dict[store_id] = []
            stores_dict[store_id].append(record)
        
        # 为每个店铺生成汇总数据
        for store_id, goods_list in stores_dict.items():
            # 不再进行商品去重，而是保留每个订单项的完整信息
            # 计算店铺汇总数据
            total_payment_amount = sum(g.payment_amount or 0.0 for g in goods_list)
            total_sales_amount = sum(g.sales_amount or 0.0 for g in goods_list)
            total_sales_cost = sum(g.sales_cost or 0.0 for g in goods_list)
            total_gross_profit_1_occurred = sum(g.gross_profit_1_occurred or 0.0 for g in goods_list)
            total_advertising_expenses = sum(g.advertising_expenses or 0.0 for g in goods_list)
            total_gross_profit_3 = sum(g.gross_profit_3 or 0.0 for g in goods_list)
            total_gross_profit_4 = sum(g.gross_profit_4 or 0.0 for g in goods_list)
            total_net_profit = sum(g.net_profit or 0.0 for g in goods_list)
            
            # 重新计算比率（基于汇总数据）
            avg_gross_profit_1_rate = (
                (total_gross_profit_1_occurred / total_sales_amount * 100) if total_sales_amount != 0 else 0
            )
            total_advertising_ratio = (
                (total_advertising_expenses / total_sales_amount * 100) if total_sales_amount != 0 else 0
            )
            avg_gross_profit_3_rate = (
                (total_gross_profit_3 / total_sales_amount * 100) if total_sales_amount != 0 else 0
            )
            avg_gross_profit_4_rate = (
                (total_gross_profit_4 / total_sales_amount * 100) if total_sales_amount != 0 else 0
            )
            avg_net_profit_rate = (
                (total_net_profit / total_sales_amount * 100) if total_sales_amount != 0 else 0
            )
            
            # 获取店铺名称（使用第一个商品的店铺名称）
            store_name = goods_list[0].store_name if goods_list else ""
            
            store_data.append({
                'store_id': store_id,
                'store_name': store_name,
                'goods_count': len(goods_list),  # 保留所有商品记录的数量（不是去重后的数量）
                'payment_amount': total_payment_amount,
                'sales_amount': total_sales_amount,
                'sales_cost': total_sales_cost,
                'gross_profit_1_occurred': total_gross_profit_1_occurred,
                'gross_profit_1_rate': round(avg_gross_profit_1_rate, 2),
                'advertising_expenses': total_advertising_expenses,
                'advertising_ratio': round(total_advertising_ratio, 2),
                'gross_profit_3': total_gross_profit_3,
                'gross_profit_3_rate': round(avg_gross_profit_3_rate, 2),
                'gross_profit_4': total_gross_profit_4,
                'gross_profit_4_rate': round(avg_gross_profit_4_rate, 2),
                'net_profit': total_net_profit,
                'net_profit_rate': round(avg_net_profit_rate, 2),
                'created_at': goods_list[0].created_at.strftime("%Y-%m-%d %H:%M:%S") if goods_list and goods_list[0].created_at else "",
                'updated_at': goods_list[0].updated_at.strftime("%Y-%m-%d %H:%M:%S") if goods_list and goods_list[0].updated_at else ""
            })
    else:
        # 普通用户查看自己关联的商品和店铺信息
        user_goods_stores = current_user.get_goods_stores()
        
        if not user_goods_stores:
            return {
                "message": "当前用户未关联任何商品和店铺",
                "data": [],
                "summary": {}
            }
        
        # 提取商品ID列表
        goods_ids = [item.get('good_id') for item in user_goods_stores if item.get('good_id')]
        
        # 构建查询条件（包含日期筛选）
        user_query_conditions = query_conditions.copy()
        if goods_ids:
            user_query_conditions.append(Goods.goods_id.in_(goods_ids))
        
        # 查询对应的商品数据
        goods_records = Goods.select().where(*user_query_conditions)
        
        # 按店铺ID分组
        stores_dict = {}
        for record in goods_records:
            store_id = record.store_id
            if store_id not in stores_dict:
                stores_dict[store_id] = []
            stores_dict[store_id].append(record)
        
        # 为每个店铺生成汇总数据
        for store_id, goods_list in stores_dict.items():
            # 不再进行商品去重，而是保留每个订单项的完整信息
            # 计算店铺汇总数据
            total_payment_amount = sum(g.payment_amount or 0.0 for g in goods_list)
            total_sales_amount = sum(g.sales_amount or 0.0 for g in goods_list)
            total_sales_cost = sum(g.sales_cost or 0.0 for g in goods_list)
            total_gross_profit_1_occurred = sum(g.gross_profit_1_occurred or 0.0 for g in goods_list)
            total_advertising_expenses = sum(g.advertising_expenses or 0.0 for g in goods_list)
            total_gross_profit_3 = sum(g.gross_profit_3 or 0.0 for g in goods_list)
            total_gross_profit_4 = sum(g.gross_profit_4 or 0.0 for g in goods_list)
            total_net_profit = sum(g.net_profit or 0.0 for g in goods_list)
            
            # 重新计算比率（基于汇总数据）
            avg_gross_profit_1_rate = (
                (total_gross_profit_1_occurred / total_sales_amount * 100) if total_sales_amount != 0 else 0
            )
            total_advertising_ratio = (
                (total_advertising_expenses / total_sales_amount * 100) if total_sales_amount != 0 else 0
            )
            avg_gross_profit_3_rate = (
                (total_gross_profit_3 / total_sales_amount * 100) if total_sales_amount != 0 else 0
            )
            avg_gross_profit_4_rate = (
                (total_gross_profit_4 / total_sales_amount * 100) if total_sales_amount != 0 else 0
            )
            avg_net_profit_rate = (
                (total_net_profit / total_sales_amount * 100) if total_sales_amount != 0 else 0
            )
            
            store_name = goods_list[0].store_name if goods_list else ""
            
            store_data.append({
                'store_id': store_id,
                'store_name': store_name,
                'goods_count': len(goods_list),  # 保留所有商品记录的数量（不是去重后的数量）
                'payment_amount': total_payment_amount,
                'sales_amount': total_sales_amount,
                'sales_cost': total_sales_cost,
                'gross_profit_1_occurred': total_gross_profit_1_occurred,
                'gross_profit_1_rate': round(avg_gross_profit_1_rate, 2),
                'advertising_expenses': total_advertising_expenses,
                'advertising_ratio': round(total_advertising_ratio, 2),
                'gross_profit_3': total_gross_profit_3,
                'gross_profit_3_rate': round(avg_gross_profit_3_rate, 2),
                'gross_profit_4': total_gross_profit_4,
                'gross_profit_4_rate': round(avg_gross_profit_4_rate, 2),
                'net_profit': total_net_profit,
                'net_profit_rate': round(avg_net_profit_rate, 2),
                'created_at': goods_list[0].created_at.strftime("%Y-%m-%d %H:%M:%S") if goods_list and goods_list[0].created_at else "",
                'updated_at': goods_list[0].updated_at.strftime("%Y-%m-%d %H:%M:%S") if goods_list and goods_list[0].updated_at else ""
            })
    
    # 计算汇总统计数据
    summary = {}
    if store_data:
        summary = {
            'total_payment_amount': sum(item['payment_amount'] for item in store_data),
            'total_sales_amount': sum(item['sales_amount'] for item in store_data),
            'total_sales_cost': sum(item['sales_cost'] for item in store_data),
            'total_gross_profit_1_occurred': sum(item['gross_profit_1_occurred'] for item in store_data),
            'total_advertising_expenses': sum(item['advertising_expenses'] for item in store_data),
            'total_gross_profit_3': sum(item['gross_profit_3'] for item in store_data),
            'total_gross_profit_4': sum(item['gross_profit_4'] for item in store_data),
            'total_net_profit': sum(item['net_profit'] for item in store_data),
            'total_stores': len(store_data),
            'total_goods': sum(item['goods_count'] for item in store_data)
        }
        
        # 重新计算总体比率
        total_sales_amount = summary['total_sales_amount']
        if total_sales_amount != 0:
            summary['avg_gross_profit_1_rate'] = round(summary['total_gross_profit_1_occurred'] / total_sales_amount * 100, 2)
            summary['avg_advertising_ratio'] = round(summary['total_advertising_expenses'] / total_sales_amount * 100, 2)
            summary['avg_gross_profit_3_rate'] = round(summary['total_gross_profit_3'] / total_sales_amount * 100, 2)
            summary['avg_gross_profit_4_rate'] = round(summary['total_gross_profit_4'] / total_sales_amount * 100, 2)
            summary['avg_net_profit_rate'] = round(summary['total_net_profit'] / total_sales_amount * 100, 2)
        else:
            summary['avg_gross_profit_1_rate'] = 0
            summary['avg_advertising_ratio'] = 0
            summary['avg_gross_profit_3_rate'] = 0
            summary['avg_gross_profit_4_rate'] = 0
            summary['avg_net_profit_rate'] = 0
    
    # 根据是否有日期筛选添加适当的消息
    date_msg = f"（{start_date} 至 {end_date}）" if start_date and end_date else ""
    return {
        "message": f"成功获取{'所有' if is_admin else '用户关联'}的店铺汇总数据{date_msg}",
        "data": store_data,
        "summary": summary
    }











# 获取特定店铺的商品详情
@router.get("/store_goods_detail/{store_id}")
def get_store_goods_detail(store_id: str, current_user = Depends(get_current_user)):
    """
    获取特定店铺的商品详情
    """
    from ..models.database import Goods, User
    
    # 判断是否为管理员
    is_admin = current_user.role == 'admin'
    
    goods_data = []
    
    if is_admin:
        # 管理员可以查看任意店铺的商品数据
        goods_records = Goods.select().where(
            (Goods.store_id == store_id) & (Goods.is_del == False)
        ).order_by(Goods.goodorder_time.desc())  # 按订单时间倒序排列
    else:
        # 普通用户只能查看自己关联的店铺商品数据
        user_goods_stores = current_user.get_goods_stores()
        user_store_ids = [item.get('store_id') for item in user_goods_stores if item.get('store_id')]
        
        if store_id not in user_store_ids:
            return {"message": "无权访问此店铺的商品详情", "data": [], "error": True}
        
        goods_records = Goods.select().where(
            (Goods.store_id == store_id) & (Goods.is_del == False)
        ).order_by(Goods.goodorder_time.desc())  # 按订单时间倒序排列
    
    # 按good_id进行分组并汇总数据
    grouped_goods = {}
    for record in goods_records:
        good_id = record.goods_id
        
        if good_id not in grouped_goods:
            # 初始化商品数据
            grouped_goods[good_id] = {
                'id': record.id,  # 使用第一条记录的ID
                'good_id': record.goods_id,
                'good_name': record.goods_name,
                'store_id': record.store_id,
                'store_name': record.store_name,
                'order_ids': [record.order_id] if record.order_id else [],  # 收集所有订单号
                'payment_amount': record.payment_amount or 0.0,
                'sales_amount': record.sales_amount or 0.0,
                'sales_cost': record.sales_cost or 0.0,
                'gross_profit_1_occurred': record.gross_profit_1_occurred or 0.0,
                'gross_profit_1_rate': record.gross_profit_1_rate or 0.0,
                'advertising_expenses': record.advertising_expenses or 0.0,
                'advertising_ratio': record.advertising_ratio or 0.0,
                'gross_profit_3': record.gross_profit_3 or 0.0,
                'gross_profit_3_rate': record.gross_profit_3_rate or 0.0,
                'gross_profit_4': record.gross_profit_4 or 0.0,
                'gross_profit_4_rate': record.gross_profit_4_rate or 0.0,
                'net_profit': record.net_profit or 0.0,
                'net_profit_rate': record.net_profit_rate or 0.0,
                'first_goodorder_time': record.goodorder_time,  # 最早订单时间
                'latest_goodorder_time': record.goodorder_time,  # 最晚订单时间
                'created_at': record.created_at,
                'updated_at': record.updated_at,
                'order_count': 1  # 订单数量
            }
        else:
            # 累加数值字段
            existing = grouped_goods[good_id]
            existing['payment_amount'] += record.payment_amount or 0.0
            existing['sales_amount'] += record.sales_amount or 0.0
            existing['sales_cost'] += record.sales_cost or 0.0
            existing['gross_profit_1_occurred'] += record.gross_profit_1_occurred or 0.0
            existing['advertising_expenses'] += record.advertising_expenses or 0.0
            existing['advertising_ratio'] += record.advertising_ratio or 0.0
            existing['gross_profit_3'] += record.gross_profit_3 or 0.0
            existing['gross_profit_4'] += record.gross_profit_4 or 0.0
            existing['net_profit'] += record.net_profit or 0.0
            
            # 更新订单ID列表
            if record.order_id:
                existing['order_ids'].append(record.order_id)
            
            # 更新时间范围
            if record.goodorder_time and (not existing['latest_goodorder_time'] or record.goodorder_time > existing['latest_goodorder_time']):
                existing['latest_goodorder_time'] = record.goodorder_time
            if record.goodorder_time and (not existing['first_goodorder_time'] or record.goodorder_time < existing['first_goodorder_time']):
                existing['first_goodorder_time'] = record.goodorder_time
            
            # 更新更新时间
            if record.updated_at > existing['updated_at']:
                existing['updated_at'] = record.updated_at
            
            existing['order_count'] += 1
    
    # 将分组结果转换为前端需要的格式
    for good_id, data in grouped_goods.items():
        # 计算平均利润率（如果需要的话）
        if data['sales_amount'] != 0:
            data['gross_profit_1_rate'] = (data['gross_profit_1_occurred'] / data['sales_amount']) * 100 if data['sales_amount'] else 0.0
            data['gross_profit_3_rate'] = (data['gross_profit_3'] / data['sales_amount']) * 100 if data['sales_amount'] else 0.0
            data['gross_profit_4_rate'] = (data['gross_profit_4'] / data['sales_amount']) * 100 if data['sales_amount'] else 0.0
            data['net_profit_rate'] = (data['net_profit'] / data['sales_amount']) * 100 if data['sales_amount'] else 0.0
            data['advertising_ratio'] = (data['advertising_expenses'] / data['sales_amount']) * 100 if data['sales_amount'] else 0.0
        
        # 格式化时间
        first_time_str = data['first_goodorder_time'].strftime("%Y-%m-%d %H:%M:%S") if data['first_goodorder_time'] else ""
        latest_time_str = data['latest_goodorder_time'].strftime("%Y-%m-%d %H:%M:%S") if data['latest_goodorder_time'] else ""
        
        goods_data.append({
            'id': data['id'],
            'good_id': data['good_id'],
            'good_name': data['good_name'],
            'store_id': data['store_id'],
            'store_name': data['store_name'],
            'order_ids': ', '.join(data['order_ids']),  # 将订单号用逗号连接
            'order_count': data['order_count'],  # 订单数量
            'payment_amount': round(data['payment_amount'], 2),
            'sales_amount': round(data['sales_amount'], 2),
            'sales_cost': round(data['sales_cost'], 2),
            'gross_profit_1_occurred': round(data['gross_profit_1_occurred'], 2),
            'gross_profit_1_rate': round(data['gross_profit_1_rate'], 2),
            'advertising_expenses': round(data['advertising_expenses'], 2),
            'advertising_ratio': round(data['advertising_ratio'], 2),
            'gross_profit_3': round(data['gross_profit_3'], 2),
            'gross_profit_3_rate': round(data['gross_profit_3_rate'], 2),
            'gross_profit_4': round(data['gross_profit_4'], 2),
            'gross_profit_4_rate': round(data['gross_profit_4_rate'], 2),
            'net_profit': round(data['net_profit'], 2),
            'net_profit_rate': round(data['net_profit_rate'], 2),
            'first_order_time': first_time_str,  # 最早订单时间
            'latest_order_time': latest_time_str,  # 最晚订单时间
            'created_at': data['created_at'].strftime("%Y-%m-%d %H:%M:%S") if data['created_at'] else "",
            'updated_at': data['updated_at'].strftime("%Y-%m-%d %H:%M:%S") if data['updated_at'] else ""
        })
    
    return {
        "message": "成功获取店铺商品详情",
        "data": goods_data
    }









# 用户-商品 接口（根据当前登录的用户 ，去查他关联的所有商品的数据， 管理员查看所有用户和商品的数据）
@router.get("/user_goods_summary/")
def get_user_goods_summary(
    start_date: str = Query(None, description="开始日期，格式：YYYY-MM-DD"),
    end_date: str = Query(None, description="结束日期，格式：YYYY-MM-DD"),
    current_user = Depends(get_current_user)
):
    """
    获取用户商品汇总数据
    管理员可查看所有用户的数据，普通用户只能查看自己的数据
    返回每个用户的关联商品和店铺的汇总信息
    支持按日期范围查询
    """
    from ..models.database import Goods, User
    from peewee import fn
    from datetime import datetime, date
    
    # 判断是否为管理员
    is_admin = current_user.role == 'admin'
    
    users_summary = []
    
    if is_admin:
        # 管理员查看所有用户
        users = User.select().where(User.is_del == False)
    else:
        # 普通用户只能查看自己的信息
        users = [current_user]
    
    for user in users:
        # 获取用户关联的商品和店铺信息
        user_goods_stores = user.get_goods_stores()
        
        if not user_goods_stores:
            # 如果用户没有关联任何商品和店铺，仍需返回用户基本信息
            users_summary.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'goods_count': 0,
                'stores_count': 0,
                'orders_count': 0,  # 订单数量
                'payment_amount': 0.0,
                'sales_amount': 0.0,
                'sales_cost': 0.0,
                'gross_profit_1_occurred': 0.0,
                'gross_profit_1_rate': 0.0,
                'advertising_expenses': 0.0,
                'advertising_ratio': 0.0,
                'gross_profit_3': 0.0,
                'gross_profit_3_rate': 0.0,
                'gross_profit_4': 0.0,
                'gross_profit_4_rate': 0.0,
                'net_profit': 0.0,
                'net_profit_rate': 0.0,
                'created_at': user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else "",
                'updated_at': user.updated_at.strftime("%Y-%m-%d %H:%M:%S") if user.updated_at else ""
            })
            continue
        
        # 提取用户关联的商品ID列表
        user_associated_goods_ids = [item.get('good_id') for item in user_goods_stores if item.get('good_id')]
        
        # 如果用户没有关联任何商品ID，返回空结果
        if not user_associated_goods_ids:
            users_summary.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'goods_count': 0,
                'stores_count': 0,
                'orders_count': 0,
                'payment_amount': 0.0,
                'sales_amount': 0.0,
                'sales_cost': 0.0,
                'gross_profit_1_occurred': 0.0,
                'gross_profit_1_rate': 0.0,
                'advertising_expenses': 0.0,
                'advertising_ratio': 0.0,
                'gross_profit_3': 0.0,
                'gross_profit_3_rate': 0.0,
                'gross_profit_4': 0.0,
                'gross_profit_4_rate': 0.0,
                'net_profit': 0.0,
                'net_profit_rate': 0.0,
                'created_at': user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else "",
                'updated_at': user.updated_at.strftime("%Y-%m-%d %H:%M:%S") if user.updated_at else ""
            })
            continue
        
        # 构建查询条件
        query_conditions = [
            Goods.is_del == False,
            Goods.goods_id.in_(user_associated_goods_ids)  # 限制为用户关联的商品ID
        ]
        
        # 如果提供了日期范围，则添加日期筛选条件
        if start_date and end_date:
            try:
                # 正确解析 YYYY-MM-DD 格式的日期
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                # 将开始日期设置为当天的开始（00:00:00）
                start_dt = start_dt.replace(hour=0, minute=0, second=0)
                # 将结束日期设置为当天的结束（23:59:59），以包含整个结束日期
                end_dt = end_dt.replace(hour=0, minute=0, second=0)
                # 使用goodorder_time字段进行日期筛选（这是实际的订单时间）
                query_conditions.append((Goods.goodorder_time >= start_dt) & (Goods.goodorder_time <= end_dt))
            except ValueError:
                raise HTTPException(status_code=400, detail="日期格式不正确，请使用 YYYY-MM-DD 格式")
        
        # 查询用户关联的商品数据
        goods_records = Goods.select().where(*query_conditions)
        
        # 按商品ID分组，汇总相同商品的数据
        goods_by_id = {}
        for record in goods_records:
            goods_id = record.goods_id
            if goods_id not in goods_by_id:
                goods_by_id[goods_id] = {
                    'good_id': record.goods_id,
                    'good_name': record.goods_name,
                    'store_id': record.store_id,
                    'store_name': record.store_name,
                    'payment_amount': 0.0,
                    'sales_amount': 0.0,
                    'sales_cost': 0.0,
                    'gross_profit_1_occurred': 0.0,
                    'gross_profit_1_rate': 0.0,
                    'advertising_expenses': 0.0,
                    'advertising_ratio': 0.0,
                    'gross_profit_3': 0.0,
                    'gross_profit_3_rate': 0.0,
                    'gross_profit_4': 0.0,
                    'gross_profit_4_rate': 0.0,
                    'net_profit': 0.0,
                    'net_profit_rate': 0.0,
                    'order_ids': set(),  # 记录涉及的订单ID集合
                    'created_at': record.created_at,
                    'updated_at': record.updated_at
                }
            
            # 累加数值字段
            goods_by_id[goods_id]['payment_amount'] += record.payment_amount or 0.0
            goods_by_id[goods_id]['sales_amount'] += record.sales_amount or 0.0
            goods_by_id[goods_id]['sales_cost'] += record.sales_cost or 0.0
            goods_by_id[goods_id]['gross_profit_1_occurred'] += record.gross_profit_1_occurred or 0.0
            goods_by_id[goods_id]['advertising_expenses'] += record.advertising_expenses or 0.0
            goods_by_id[goods_id]['gross_profit_3'] += record.gross_profit_3 or 0.0
            goods_by_id[goods_id]['gross_profit_4'] += record.gross_profit_4 or 0.0
            goods_by_id[goods_id]['net_profit'] += record.net_profit or 0.0
            
            # 记录订单ID
            if record.order_id:
                goods_by_id[goods_id]['order_ids'].add(record.order_id)
        
        # 转换为列表格式
        goods_data = []
        for goods_info in goods_by_id.values():
            # 重新计算比率
            sales_amount = goods_info['sales_amount']
            if sales_amount != 0:
                goods_info['gross_profit_1_rate'] = round(goods_info['gross_profit_1_occurred'] / sales_amount * 100, 2)
                goods_info['advertising_ratio'] = round(goods_info['advertising_expenses'] / sales_amount * 100, 2)
                goods_info['gross_profit_3_rate'] = round(goods_info['gross_profit_3'] / sales_amount * 100, 2)
                goods_info['gross_profit_4_rate'] = round(goods_info['gross_profit_4'] / sales_amount * 100, 2)
                goods_info['net_profit_rate'] = round(goods_info['net_profit'] / sales_amount * 100, 2)
            else:
                goods_info['gross_profit_1_rate'] = 0
                goods_info['advertising_ratio'] = 0
                goods_info['gross_profit_3_rate'] = 0
                goods_info['gross_profit_4_rate'] = 0
                goods_info['net_profit_rate'] = 0
            
            goods_info['orders_count'] = len(goods_info['order_ids'])  # 订单数量
            del goods_info['order_ids']  # 删除临时字段
            goods_data.append(goods_info)

        # 计算汇总数据
        if goods_data:
            total_payment_amount = sum(item['payment_amount'] for item in goods_data)
            total_sales_amount = sum(item['sales_amount'] for item in goods_data)
            total_sales_cost = sum(item['sales_cost'] for item in goods_data)
            total_gross_profit_1_occurred = sum(item['gross_profit_1_occurred'] for item in goods_data)
            avg_gross_profit_1_rate = (
                sum(item['gross_profit_1_rate'] for item in goods_data) / len(goods_data) 
                if goods_data else 0
            )
            total_advertising_expenses = sum(item['advertising_expenses'] for item in goods_data)
            avg_advertising_ratio = (
                sum(item['advertising_ratio'] for item in goods_data) / len(goods_data) 
                if goods_data else 0
            )
            total_gross_profit_3 = sum(item['gross_profit_3'] for item in goods_data)
            avg_gross_profit_3_rate = (
                sum(item['gross_profit_3_rate'] for item in goods_data) / len(goods_data) 
                if goods_data else 0
            )
            total_gross_profit_4 = sum(item['gross_profit_4'] for item in goods_data)
            avg_gross_profit_4_rate = (
                sum(item['gross_profit_4_rate'] for item in goods_data) / len(goods_data) 
                if goods_data else 0
            )
            total_net_profit = sum(item['net_profit'] for item in goods_data)
            avg_net_profit_rate = (
                sum(item['net_profit_rate'] for item in goods_data) / len(goods_data) 
                if goods_data else 0
            )
            
            # 统计不同的店铺数量
            store_ids = set(item['store_id'] for item in goods_data if item['store_id'])
            
            # 统计总的订单数量（所有商品涉及的订单总数）
            total_orders_count = sum(item.get('orders_count', 0) for item in goods_data)
        else:
            total_payment_amount = 0.0
            total_sales_amount = 0.0
            total_sales_cost = 0.0
            total_gross_profit_1_occurred = 0.0
            avg_gross_profit_1_rate = 0.0
            total_advertising_expenses = 0.0
            avg_advertising_ratio = 0.0
            total_gross_profit_3 = 0.0
            avg_gross_profit_3_rate = 0.0
            total_gross_profit_4 = 0.0
            avg_gross_profit_4_rate = 0.0
            total_net_profit = 0.0
            avg_net_profit_rate = 0.0
            store_ids = set()
            total_orders_count = 0

        users_summary.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'goods_count': len(goods_data),  # 汇总后的商品种类数量
            'stores_count': len(store_ids),
            'orders_count': total_orders_count,  # 总订单数量
            'payment_amount': total_payment_amount,
            'sales_amount': total_sales_amount,
            'sales_cost': total_sales_cost,
            'gross_profit_1_occurred': total_gross_profit_1_occurred,
            'gross_profit_1_rate': avg_gross_profit_1_rate,
            'advertising_expenses': total_advertising_expenses,
            'advertising_ratio': avg_advertising_ratio,
            'gross_profit_3': total_gross_profit_3,
            'gross_profit_3_rate': avg_gross_profit_3_rate,
            'gross_profit_4': total_gross_profit_4,
            'gross_profit_4_rate': avg_gross_profit_4_rate,
            'net_profit': total_net_profit,
            'net_profit_rate': avg_net_profit_rate,
            'created_at': user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else "",
            'updated_at': user.updated_at.strftime("%Y-%m-%d %H:%M:%S") if user.updated_at else ""
        })
    
    # 根据是否有日期筛选添加适当的消息
    date_msg = f"（{start_date} 至 {end_date}）" if start_date and end_date else ""
    return {
        "message": f"成功获取{'所有用户' if is_admin else '当前用户'}的商品汇总数据{date_msg}",
        "data": users_summary
    }



# 用户商品详情
@router.get("/user_goods_detail/{user_id}")
def get_user_goods_detail(
    user_id: int, 
    start_date: str = Query(None, description="开始日期，格式：YYYY-MM-DD"),
    end_date: str = Query(None, description="结束日期，格式：YYYY-MM-DD"),
    current_user = Depends(get_current_user)
):
    """
    获取特定用户关联的商品详情
    管理员可查看任意用户的数据，普通用户只能查看自己的数据
    支持按日期范围查询
    """
    from ..models.database import Goods, User
    from peewee import fn
    from datetime import datetime, date
    
    # 判断是否为管理员
    is_admin = current_user.role == 'admin'
    
    # 获取目标用户
    target_user = User.get_or_none(User.id == user_id)
    if not target_user:
        return {"message": "用户不存在", "data": [], "error": True}
    
    # 权限检查
    if not is_admin and current_user.id != user_id:
        return {"message": "无权访问此用户的数据", "data": [], "error": True}
    
    # 获取用户关联的商品和店铺信息
    user_goods_stores = target_user.get_goods_stores()
    
    if not user_goods_stores:
        return {"message": "该用户未关联任何商品和店铺", "data": [], "error": False}
    
    # 提取商品ID列表
    goods_ids = [item.get('good_id') for item in user_goods_stores if item.get('good_id')]
    
    # 如果用户没有关联任何商品ID，返回空结果
    if not goods_ids:
        return {"message": "该用户未关联任何商品ID", "data": [], "error": False}
    
    # 构建查询条件
    query_conditions = [
        Goods.is_del == False,
        Goods.goods_id.in_(goods_ids)  # 限制为用户关联的商品ID
    ]
    
    # 如果提供了日期范围，则添加日期筛选条件
    if start_date and end_date:
        try:
            # 正确解析 YYYY-MM-DD 格式的日期
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            # 将开始日期设置为当天的开始（00:00:00）
            start_dt = start_dt.replace(hour=0, minute=0, second=0)
            # 将结束日期设置为当天的结束（23:59:59），以包含整个结束日期
            end_dt = end_dt.replace(hour=23, minute=59, second=59)
            # 使用goodorder_time字段进行日期筛选（这是实际的订单时间）
            query_conditions.append((Goods.goodorder_time >= start_dt) & (Goods.goodorder_time <= end_dt))
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式不正确，请使用 YYYY-MM-DD 格式")
    
    # 查询对应的商品数据
    goods_records = Goods.select().where(*query_conditions).order_by(Goods.goodorder_time.desc())  # 按订单时间倒序排列
    
    # 按good_id进行分组并汇总数据
    grouped_goods = {}
    for record in goods_records:
        good_id = record.goods_id
        
        if good_id not in grouped_goods:
            # 初始化商品数据
            grouped_goods[good_id] = {
                'id': record.id,  # 使用第一条记录的ID
                'good_id': record.goods_id,
                'good_name': record.goods_name,
                'store_id': record.store_id,
                'store_name': record.store_name,
                'order_ids': [record.order_id] if record.order_id else [],  # 收集所有订单号
                'payment_amount': record.payment_amount or 0.0,
                'sales_amount': record.sales_amount or 0.0,
                'sales_cost': record.sales_cost or 0.0,
                'gross_profit_1_occurred': record.gross_profit_1_occurred or 0.0,
                'gross_profit_1_rate': record.gross_profit_1_rate or 0.0,
                'advertising_expenses': record.advertising_expenses or 0.0,
                'advertising_ratio': record.advertising_ratio or 0.0,
                'gross_profit_3': record.gross_profit_3 or 0.0,
                'gross_profit_3_rate': record.gross_profit_3_rate or 0.0,
                'gross_profit_4': record.gross_profit_4 or 0.0,
                'gross_profit_4_rate': record.gross_profit_4_rate or 0.0,
                'net_profit': record.net_profit or 0.0,
                'net_profit_rate': record.net_profit_rate or 0.0,
                'first_goodorder_time': record.goodorder_time,  # 最早订单时间
                'latest_goodorder_time': record.goodorder_time,  # 最晚订单时间
                'created_at': record.created_at,
                'updated_at': record.updated_at,
                'order_count': 1  # 订单数量
            }
        else:
            # 累加数值字段
            existing = grouped_goods[good_id]
            existing['payment_amount'] += record.payment_amount or 0.0
            existing['sales_amount'] += record.sales_amount or 0.0
            existing['sales_cost'] += record.sales_cost or 0.0
            existing['gross_profit_1_occurred'] += record.gross_profit_1_occurred or 0.0
            existing['advertising_expenses'] += record.advertising_expenses or 0.0
            existing['advertising_ratio'] += record.advertising_ratio or 0.0
            existing['gross_profit_3'] += record.gross_profit_3 or 0.0
            existing['gross_profit_4'] += record.gross_profit_4 or 0.0
            existing['net_profit'] += record.net_profit or 0.0
            
            # 更新订单ID列表
            if record.order_id:
                existing['order_ids'].append(record.order_id)
            
            # 更新时间范围
            if record.goodorder_time and (not existing['latest_goodorder_time'] or record.goodorder_time > existing['latest_goodorder_time']):
                existing['latest_goodorder_time'] = record.goodorder_time
            if record.goodorder_time and (not existing['first_goodorder_time'] or record.goodorder_time < existing['first_goodorder_time']):
                existing['first_goodorder_time'] = record.goodorder_time
            
            # 更新更新时间
            if record.updated_at > existing['updated_at']:
                existing['updated_at'] = record.updated_at
            
            existing['order_count'] += 1
    
    # 将分组结果转换为前端需要的格式
    goods_data = []
    for good_id, data in grouped_goods.items():
        # 计算平均利润率（如果需要的话）
        if data['sales_amount'] != 0:
            data['gross_profit_1_rate'] = (data['gross_profit_1_occurred'] / data['sales_amount']) * 100 if data['sales_amount'] else 0.0
            data['gross_profit_3_rate'] = (data['gross_profit_3'] / data['sales_amount']) * 100 if data['sales_amount'] else 0.0
            data['gross_profit_4_rate'] = (data['gross_profit_4'] / data['sales_amount']) * 100 if data['sales_amount'] else 0.0
            data['net_profit_rate'] = (data['net_profit'] / data['sales_amount']) * 100 if data['sales_amount'] else 0.0
            data['advertising_ratio'] = (data['advertising_expenses'] / data['sales_amount']) * 100 if data['sales_amount'] else 0.0
        
        # 格式化时间
        first_time_str = data['first_goodorder_time'].strftime("%Y-%m-%d %H:%M:%S") if data['first_goodorder_time'] else ""
        latest_time_str = data['latest_goodorder_time'].strftime("%Y-%m-%d %H:%M:%S") if data['latest_goodorder_time'] else ""
        
        goods_data.append({
            'id': data['id'],
            'good_id': data['good_id'],
            'good_name': data['good_name'],
            'store_id': data['store_id'],
            'store_name': data['store_name'],
            'order_ids': ', '.join([oid for oid in data['order_ids'] if oid]),  # 将订单号用逗号连接
            'order_count': data['order_count'],  # 订单数量
            'payment_amount': round(data['payment_amount'], 2),
            'sales_amount': round(data['sales_amount'], 2),
            'sales_cost': round(data['sales_cost'], 2),
            'gross_profit_1_occurred': round(data['gross_profit_1_occurred'], 2),
            'gross_profit_1_rate': round(data['gross_profit_1_rate'], 2),
            'advertising_expenses': round(data['advertising_expenses'], 2),
            'advertising_ratio': round(data['advertising_ratio'], 2),
            'gross_profit_3': round(data['gross_profit_3'], 2),
            'gross_profit_3_rate': round(data['gross_profit_3_rate'], 2),
            'gross_profit_4': round(data['gross_profit_4'], 2),
            'gross_profit_4_rate': round(data['gross_profit_4_rate'], 2),
            'net_profit': round(data['net_profit'], 2),
            'net_profit_rate': round(data['net_profit_rate'], 2),
            'first_order_time': first_time_str,  # 最早订单时间
            'latest_order_time': latest_time_str,  # 最晚订单时间
            'created_at': data['created_at'].strftime("%Y-%m-%d %H:%M:%S") if data['created_at'] else "",
            'updated_at': data['updated_at'].strftime("%Y-%m-%d %H:%M:%S") if data['updated_at'] else ""
        })

    # 根据是否有日期筛选添加适当的消息
    date_msg = f"（{start_date} 至 {end_date}）" if start_date and end_date else ""
    return {
        "message": f"成功获取用户 {target_user.username} 的商品详情{date_msg}",
        "data": goods_data
    }


# 用户去关联商品的字典 接口
@router.get("/goods_dict/")
def get_goods_dict():
    """
    查询goods表形成字典接口
    返回商品名和商品ID的选项数组，用于前端下拉选择
    """
    from ..models.database import Goods
    
    try:
        # 查询所有未删除的商品，使用group_by去重并按商品ID排序
        goods_records = Goods.select(
            Goods.goods_id,
            Goods.goods_name
        ).where(
            Goods.is_del == False
        ).group_by(Goods.goods_id)  # 使用group_by去重相同的商品ID
        
        # 构建字典数组
        goods_dict = []
        for record in goods_records:
            if record.goods_id and record.goods_name:  # 确保ID和名称都不为空
                goods_dict.append({
                    'label': record.goods_name,
                    'value': record.goods_id
                })
        
        # 按商品名称排序，便于用户查找
        goods_dict.sort(key=lambda x: x['label'])
        
        return {
            "message": "成功获取商品字典数据",
            "data": goods_dict
        }
        
    except Exception as e:
        print(f"获取商品字典数据时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取商品字典数据失败: {str(e)}")













# ********* 拼多多数据相关路由 *********
@router.get("/pdd_products/")
def read_pdd_products(skip: int = 0, limit: int = 100):
    """获取拼多多商品数据列表"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database.db")
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="数据库不存在")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM pdd_products WHERE is_del = 0 LIMIT ? OFFSET ?', (limit, skip))
    records = cursor.fetchall()
    
    # 获取列名
    column_names = [description[0] for description in cursor.description]
    
    # 将结果转换为字典列表
    result = []
    for row in records:
        record_dict = {}
        for i, col_name in enumerate(column_names):
            record_dict[col_name] = row[i]
        result.append(record_dict)
    
    conn.close()
    return result







# 店铺相关路由
@router.get("/stores/", response_model=List[schemas.Store])
def read_stores(skip: int = 0, limit: int = 100):
    """获取店铺列表"""
    with get_db() as db:
        stores = product_service.get_stores(db, skip=skip, limit=limit)
        return list(stores)