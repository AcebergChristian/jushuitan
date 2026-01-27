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
def sync_jushuitan_data():
    """同步聚水潭数据到数据库，根据oid字段处理重复数据"""
    
    # 获取聚水潭API数据
    api_response = get_all_jushuitan_orders()
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
    from ..models.database import Goods
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
    

        # 获取所有未删除的订单数据
        api_response = get_all_jushuitan_orders(sync_date=sync_date)
        if not api_response or 'data' not in api_response:
            raise HTTPException(status_code=400, detail="获取聚水潭API数据失败")

        orders = api_response.get('data', [])

        # 用于存储商品数据的字典，以shopIid为主键
        goods_dict = {}

        for order in orders:
            try:
                # 如果指定了同步日期，则只处理该日期的订单
                if sync_date:
                    order_time_str = order.get('orderTime')
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
                
                # 解析disInnerOrderGoodsViewList字段
                goods_list = order.get('disInnerOrderGoodsViewList')
                
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
                    
                    # 使用shopIid作为唯一键
                    unique_key = shop_iid
                    
                    # 获取商品其他信息 - 使用正确的英文字段名
                    item_name = goods_item.get('itemName', '未知商品')
                    item_code = goods_item.get('itemCode', '')
                    supplier_name = goods_item.get('supplierName', '')
                    pic = goods_item.get('pic', '')
                    properties = goods_item.get('properties', '')
                    price = float(goods_item.get('price', 0) or 0)
                    payAmount = float(goods_item.get('payAmount', 0) or 0)
                    paidAmount = float(goods_item.get('paidAmount', 0) or 0)
                    total_price = float(goods_item.get('totalPrice', 0) or 0)
                    item_count = int(goods_item.get('itemCount', 1) or 1)
                    
                    # 如果指定了同步日期，使用该日期，否则使用订单创建日期
                    if sync_date:
                        order_created_at = datetime.combine(sync_date, datetime.min.time())
                    else:
                        # 获取订单创建时间并转换为日期对象
                        order_created_at_str = order.get('created_at')
                        if order_created_at_str:
                            if isinstance(order_created_at_str, str):
                                order_created_at = datetime.fromisoformat(order_created_at_str.replace('Z', '+00:00'))
                            elif isinstance(order_created_at_str, datetime):
                                order_created_at = order_created_at_str
                            else:
                                order_created_at = datetime.now()
                        else:
                            order_created_at = datetime.now()
                    
                    # 使用shopIid和日期作为组合键，以便区分同一天内的重复与不同日期的数据
                    date_key = order_created_at.date()
                    full_key = (unique_key, date_key)
                    
                    # 初始化商品数据结构
                    goods_dict[full_key] = {
                        'goods_id': shop_iid,  # 商品ID使用shopIid
                        'goods_name': item_name,
                        'store_id': order.get('shopId') or '',
                        'store_name': order.get('shopName') or '未知店铺',
                        'order_id': order.get('oid') or '',
                        'payment_amount': paidAmount,
                        'sales_amount': payAmount,
                        'sales_cost': price * item_count,  # 成本乘以数量
                        'item_count': item_count,
                        'price': price,
                        'total_price': total_price,
                        'supplier_name': supplier_name,
                        'pic': pic,
                        'item_code': item_code,
                        'properties': properties,
                        'creator': 'system',
                        'created_at': order_created_at,
                        'updated_at': datetime.now()
                    }
        
            except Exception as e:
                print(f"Error processing order {order.get('id')}: {e}")

        # 处理数据库中已存在的商品记录
        for full_key, goods_data in goods_dict.items():
            shop_iid = goods_data['goods_id']
            current_date = goods_data['created_at'].date()
            
            # 查询数据库中是否存在相同shopIid的历史记录
            existing_records = Goods.select().where(
                (Goods.goods_id == shop_iid)
            )
            
            records_to_delete = []
            should_insert_new = True
            
            for record in existing_records:
                existing_date = record.created_at.date()
                
                # 如果历史记录的创建日期与当前记录的创建日期相同，则标记为删除
                if existing_date == current_date:
                    records_to_delete.append(record.id)
                # 如果历史记录的创建日期不同，则保留不删除
            
            # 删除同一天的旧记录
            if records_to_delete:
                for record_id in records_to_delete:
                    Goods.delete().where(Goods.id == record_id).execute()
            
            # 插入新的记录
            new_good = Goods.create(
                goods_id=goods_data['goods_id'],
                goods_name=goods_data['goods_name'],
                store_id=goods_data['store_id'],
                store_name=goods_data['store_name'],
                order_id=goods_data['order_id'],
                payment_amount=goods_data['payment_amount'],
                sales_amount=goods_data['sales_amount'],
                sales_cost=goods_data['sales_cost'],
                item_count=goods_data['item_count'],
                price=goods_data['price'],
                total_price=goods_data['total_price'],
                supplier_name=goods_data['supplier_name'],
                pic=goods_data['pic'],
                item_code=goods_data['item_code'],
                properties=goods_data['properties'],
                creator=goods_data['creator'],
                created_at=goods_data['created_at'],
                updated_at=goods_data['updated_at']
            )

        # 计算利润相关指标并更新
        all_updated_goods = Goods.select().where(
            Goods.goods_id.in_([goods_data['goods_id'] for goods_data in goods_dict.values()])
        )
        
        for good_record in all_updated_goods:
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







# 获取商品列表 - 支持分页和模糊查询
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






# 根据当前登录的用户 ，去查他关联的所有商品的id，再去查其店铺的数据，展示
@router.get("/user_goods_stores_data/")
def get_user_goods_stores_data(current_user = Depends(get_current_user)):
    """
    根据当前登录用户的goods_stores字段查询商品及店铺数据
    管理员可查看所有数据，普通用户只能查看自己的数据
    按店铺维度返回汇总数据
    返回包含销售金额、成本、利润等统计信息的数据
    """
    from ..models.database import Goods, User
    
    # 判断是否为管理员
    is_admin = current_user.role == 'admin'
    
    store_data = []
    
    if is_admin:
        # 管理员查看所有商品数据，按店铺分组
        goods_records = Goods.select().where(Goods.is_del == False)
        
        # 按店铺ID分组
        stores_dict = {}
        for record in goods_records:
            store_id = record.store_id
            if store_id not in stores_dict:
                stores_dict[store_id] = []
            stores_dict[store_id].append(record)
        
        # 为每个店铺生成汇总数据
        for store_id, goods_list in stores_dict.items():
            # 计算店铺汇总数据
            total_payment_amount = sum((g.payment_amount or 0.0) for g in goods_list)
            total_sales_amount = sum((g.sales_amount or 0.0) for g in goods_list)
            total_sales_cost = sum((g.sales_cost or 0.0) for g in goods_list)
            total_gross_profit_1_occurred = sum((g.gross_profit_1_occurred or 0.0) for g in goods_list)
            avg_gross_profit_1_rate = (
                sum((g.gross_profit_1_rate or 0.0) for g in goods_list) / len(goods_list) 
                if goods_list else 0
            )
            total_advertising_expenses = sum((g.advertising_expenses or 0.0) for g in goods_list)
            total_advertising_ratio = (
                sum((g.advertising_ratio or 0.0) for g in goods_list) / len(goods_list) 
                if goods_list else 0
            )
            total_gross_profit_3 = sum((g.gross_profit_3 or 0.0) for g in goods_list)
            avg_gross_profit_3_rate = (
                sum((g.gross_profit_3_rate or 0.0) for g in goods_list) / len(goods_list) 
                if goods_list else 0
            )
            total_gross_profit_4 = sum((g.gross_profit_4 or 0.0) for g in goods_list)
            avg_gross_profit_4_rate = (
                sum((g.gross_profit_4_rate or 0.0) for g in goods_list) / len(goods_list) 
                if goods_list else 0
            )
            total_net_profit = sum((g.net_profit or 0.0) for g in goods_list)
            avg_net_profit_rate = (
                sum((g.net_profit_rate or 0.0) for g in goods_list) / len(goods_list) 
                if goods_list else 0
            )
            
            # 获取店铺名称（使用第一个商品的店铺名称）
            store_name = goods_list[0].store_name if goods_list else ""
            
            store_data.append({
                'store_id': store_id,
                'store_name': store_name,
                'goods_count': len(goods_list),
                'payment_amount': total_payment_amount,
                'sales_amount': total_sales_amount,
                'sales_cost': total_sales_cost,
                'gross_profit_1_occurred': total_gross_profit_1_occurred,
                'gross_profit_1_rate': avg_gross_profit_1_rate,
                'advertising_expenses': total_advertising_expenses,
                'advertising_ratio': total_advertising_ratio,
                'gross_profit_3': total_gross_profit_3,
                'gross_profit_3_rate': avg_gross_profit_3_rate,
                'gross_profit_4': total_gross_profit_4,
                'gross_profit_4_rate': avg_gross_profit_4_rate,
                'net_profit': total_net_profit,
                'net_profit_rate': avg_net_profit_rate,
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
        
        # 查询对应的商品数据
        goods_records = []
        if goods_ids:
            goods_records = Goods.select().where(
                (Goods.goods_id.in_(goods_ids)) & (Goods.is_del == False)
            )
        
        # 按店铺ID分组
        stores_dict = {}
        for record in goods_records:
            store_id = record.store_id
            if store_id not in stores_dict:
                stores_dict[store_id] = []
            stores_dict[store_id].append(record)
        
        # 为每个店铺生成汇总数据
        for store_id, goods_list in stores_dict.items():
            # 计算店铺汇总数据
            total_payment_amount = sum((g.payment_amount or 0.0) for g in goods_list)
            total_sales_amount = sum((g.sales_amount or 0.0) for g in goods_list)
            total_sales_cost = sum((g.sales_cost or 0.0) for g in goods_list)
            total_gross_profit_1_occurred = sum((g.gross_profit_1_occurred or 0.0) for g in goods_list)
            avg_gross_profit_1_rate = (
                sum((g.gross_profit_1_rate or 0.0) for g in goods_list) / len(goods_list) 
                if goods_list else 0
            )
            total_advertising_expenses = sum((g.advertising_expenses or 0.0) for g in goods_list)
            total_advertising_ratio = (
                sum((g.advertising_ratio or 0.0) for g in goods_list) / len(goods_list) 
                if goods_list else 0
            )
            total_gross_profit_3 = sum((g.gross_profit_3 or 0.0) for g in goods_list)
            avg_gross_profit_3_rate = (
                sum((g.gross_profit_3_rate or 0.0) for g in goods_list) / len(goods_list) 
                if goods_list else 0
            )
            total_gross_profit_4 = sum((g.gross_profit_4 or 0.0) for g in goods_list)
            avg_gross_profit_4_rate = (
                sum((g.gross_profit_4_rate or 0.0) for g in goods_list) / len(goods_list) 
                if goods_list else 0
            )
            total_net_profit = sum((g.net_profit or 0.0) for g in goods_list)
            avg_net_profit_rate = (
                sum((g.net_profit_rate or 0.0) for g in goods_list) / len(goods_list) 
                if goods_list else 0
            )
            
            store_name = goods_list[0].store_name if goods_list else ""
            
            store_data.append({
                'store_id': store_id,
                'store_name': store_name,
                'goods_count': len(goods_list),
                'payment_amount': total_payment_amount,
                'sales_amount': total_sales_amount,
                'sales_cost': total_sales_cost,
                'gross_profit_1_occurred': total_gross_profit_1_occurred,
                'gross_profit_1_rate': avg_gross_profit_1_rate,
                'advertising_expenses': total_advertising_expenses,
                'advertising_ratio': total_advertising_ratio,
                'gross_profit_3': total_gross_profit_3,
                'gross_profit_3_rate': avg_gross_profit_3_rate,
                'gross_profit_4': total_gross_profit_4,
                'gross_profit_4_rate': avg_gross_profit_4_rate,
                'net_profit': total_net_profit,
                'net_profit_rate': avg_net_profit_rate,
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
            'avg_gross_profit_1_rate': sum(item['gross_profit_1_rate'] for item in store_data) / len(store_data) if store_data else 0,
            'total_advertising_expenses': sum(item['advertising_expenses'] for item in store_data),
            'total_gross_profit_3': sum(item['gross_profit_3'] for item in store_data),
            'avg_gross_profit_3_rate': sum(item['gross_profit_3_rate'] for item in store_data) / len(store_data) if store_data else 0,
            'total_gross_profit_4': sum(item['gross_profit_4'] for item in store_data),
            'avg_gross_profit_4_rate': sum(item['gross_profit_4_rate'] for item in store_data) / len(store_data) if store_data else 0,
            'total_net_profit': sum(item['net_profit'] for item in store_data),
            'avg_net_profit_rate': sum(item['net_profit_rate'] for item in store_data) / len(store_data) if store_data else 0,
            'total_stores': len(store_data),
            'total_goods': sum(item['goods_count'] for item in store_data)
        }
    
    return {
        "message": f"成功获取{'所有' if is_admin else '用户关联'}的店铺汇总数据",
        "data": store_data,
        "summary": summary
    }


# 新增接口：获取特定店铺的商品详情
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
        )
    else:
        # 普通用户只能查看自己关联的店铺商品数据
        user_goods_stores = current_user.get_goods_stores()
        user_store_ids = [item.get('store_id') for item in user_goods_stores if item.get('store_id')]
        
        if store_id not in user_store_ids:
            return {"message": "无权访问此店铺的商品详情", "data": [], "error": True}
        
        goods_records = Goods.select().where(
            (Goods.store_id == store_id) & (Goods.is_del == False)
        )
    
    for record in goods_records:
        goods_data.append({
            'good_id': record.goods_id,
            'good_name': record.goods_name,
            'store_id': record.store_id,
            'store_name': record.store_name,
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
            'created_at': record.created_at.strftime("%Y-%m-%d %H:%M:%S") if record.created_at else "",
            'updated_at': record.updated_at.strftime("%Y-%m-%d %H:%M:%S") if record.updated_at else ""
        })
    
    return {
        "message": "成功获取店铺商品详情",
        "data": goods_data
    }


# 用户-商品 接口（根据当前登录的用户 ，去查他关联的所有商品的数据， 管理员查看所有用户和商品的数据）
@router.get("/user_goods_summary/")
def get_user_goods_summary(current_user = Depends(get_current_user)):
    """
    获取用户商品汇总数据
    管理员可查看所有用户的数据，普通用户只能查看自己的数据
    返回每个用户的关联商品和店铺的汇总信息（仅限最新一天的数据）
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
        
        # 获取最新一天的日期
        # today = date.today()
        
        # 查询对应的商品数据，只查询最新一天的数据
        goods_data = []
        if user_associated_goods_ids:
            # 先获取最新一天的记录
            goods_records = Goods.select().where(
                (Goods.goods_id.in_(user_associated_goods_ids)) & 
                (Goods.is_del == False) 
                # & (fn.DATE(Goods.created_at) == today)  # 只查询今天的数据
            )
            
            for record in goods_records:
                goods_data.append({
                    'good_id': record.goods_id,
                    'good_name': record.goods_name,
                    'store_id': record.store_id,
                    'store_name': record.store_name,
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
                    'created_at': record.created_at.strftime("%Y-%m-%d %H:%M:%S") if record.created_at else "",
                    'updated_at': record.updated_at.strftime("%Y-%m-%d %H:%M:%S") if record.updated_at else ""
                })
        
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
        
        users_summary.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'goods_count': len(goods_data),
            'stores_count': len(store_ids),
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
    
    return {
        "message": f"成功获取{'所有用户' if is_admin else '当前用户'}的商品汇总数据（仅限今日）",
        "data": users_summary
    }


@router.get("/user_goods_detail/{user_id}")
def get_user_goods_detail(user_id: int, current_user = Depends(get_current_user)):
    """
    获取特定用户关联的商品详情
    管理员可查看任意用户的数据，普通用户只能查看自己的数据
    仅返回最新一天的数据
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
    
    # 获取最新一天的日期
    # today = date.today()
    
    # 查询对应的商品数据，只查询最新一天的数据
    goods_data = []
    if goods_ids:
        goods_records = Goods.select().where(
            (Goods.goods_id.in_(goods_ids)) & 
            (Goods.is_del == False)
            # & (fn.DATE(Goods.created_at) == today)  # 只查询今天的数据
        )
        
        for record in goods_records:
            goods_data.append({
                'good_id': record.goods_id,
                'good_name': record.goods_name,
                'store_id': record.store_id,
                'store_name': record.store_name,
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
                'created_at': record.created_at.strftime("%Y-%m-%d %H:%M:%S") if record.created_at else "",
                'updated_at': record.updated_at.strftime("%Y-%m-%d %H:%M:%S") if record.updated_at else ""
            })
    
    return {
        "message": f"成功获取用户 {target_user.username} 的商品详情（仅限今日）",
        "data": goods_data
    }
























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