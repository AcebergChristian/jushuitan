from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from .. import schemas
from ..services import product_service
from ..database import get_db
from ..models.database import JushuitanProduct, Goods


import sqlite3
import os
import json
from datetime import datetime, date, timedelta

from ..spiders.jushuitan_api import get_jushuitan_orders

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
    api_response = get_jushuitan_orders()
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
@router.get("/sync_goods/")
def sync_goods():
    """
    同步订单数据中的商品信息到goods表
    - 提取disInnerOrderGoodsViewList中的商品数据
    - 按shopIid聚合相同商品的金额
    - 计算各种利润指标
    """
    
    try:
        # 获取所有未删除的订单数据
        api_response = get_jushuitan_orders()
        if not api_response or 'data' not in api_response:
            raise HTTPException(status_code=400, detail="获取聚水潭API数据失败")
    
        orders = api_response.get('data', [])
        print("Total orders:", len(orders), type(orders))

        # 用于存储商品数据的字典，以shopIid为主键
        goods_dict = {}
        
        for order in orders:
            try:
                # 解析disInnerOrderGoodsViewList字段
                goods_list = order.get('disInnerOrderGoodsViewList')
                
                if not isinstance(goods_list, list):
                    continue
                
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
                    total_price = float(goods_item.get('totalPrice', 0) or 0)
                    item_count = int(goods_item.get('itemCount', 1) or 1)
                    
                    # 初始化商品数据结构或累加已有数据
                    if unique_key not in goods_dict:
                        goods_dict[unique_key] = {
                            'goods_id': shop_iid,  # 商品ID使用shopIid
                            'goods_name': item_name,
                            'store_id': order.get('shopId') or '',
                            'store_name': order.get('shopName') or '未知店铺',
                            'order_id': order.get('oid') or '',
                            'payment_amount': total_price,
                            'sales_amount': total_price,
                            'sales_cost': price * item_count,  # 成本乘以数量
                            'item_count': item_count,
                            'price': price,
                            'total_price': total_price,
                            'supplier_name': supplier_name,
                            'pic': pic,
                            'item_code': item_code,
                            'properties': properties,
                            'creator': 'system',
                            'created_at': order.get('created_at') if hasattr(order, 'created_at') else datetime.now(),
                            'updated_at': datetime.now()
                        }
                    else:
                        # 如果已存在相同的shopIid，执行聚合计算
                        goods_dict[unique_key]['payment_amount'] += total_price
                        goods_dict[unique_key]['sales_amount'] += total_price
                        goods_dict[unique_key]['sales_cost'] += price * item_count
                        goods_dict[unique_key]['item_count'] += item_count
                        # 更新商品名称（保持最新或最常用）
                        if item_name != '未知商品':
                            goods_dict[unique_key]['goods_name'] = item_name
                        # 更新供应商名称（保持最新或最常用）
                        if supplier_name:
                            goods_dict[unique_key]['supplier_name'] = supplier_name
            
            except Exception as e:
                print(f"Error processing order {order.get('id')}: {e}")

        # 计算利润相关指标
        for unique_key in goods_dict:
            goods_data = goods_dict[unique_key]
            sales_amount = goods_data['sales_amount']
            cost_amount = goods_data['sales_cost']
            
            # 计算各种利润指标
            goods_data['gross_profit_1_occurred'] = sales_amount - cost_amount
            goods_data['gross_profit_1_rate'] = round(((sales_amount - cost_amount) / sales_amount) * 100, 2) if sales_amount > 0 else 0
            
            # 假设广告费是销售额的一个固定比例，或者从其他地方获取
            ad_cost = goods_data.get('advertising_expenses', 0)
            goods_data['advertising_ratio'] = round((ad_cost / sales_amount) * 100, 2) if sales_amount > 0 else 0
            
            goods_data['gross_profit_3'] = sales_amount - cost_amount - ad_cost
            goods_data['gross_profit_3_rate'] = round(((sales_amount - cost_amount - ad_cost) / sales_amount) * 100, 2) if sales_amount > 0 else 0
            
            goods_data['gross_profit_4'] = sales_amount - cost_amount - ad_cost  # 可能还有其他费用
            goods_data['gross_profit_4_rate'] = round(((sales_amount - cost_amount - ad_cost) / sales_amount) * 100, 2) if sales_amount > 0 else 0
            
            goods_data['net_profit'] = sales_amount - cost_amount - ad_cost  # 净利润可能还要扣除其他费用
            goods_data['net_profit_rate'] = round(((sales_amount - cost_amount - ad_cost) / sales_amount) * 100, 2) if sales_amount > 0 else 0
        
        # 将汇总后的商品数据插入到goods表
        processed_count = 0
        created_count = 0
        updated_count = 0
        
        for unique_key, goods_data in goods_dict.items():
            # 检查是否已存在相同的商品记录
            existing_goods = Goods.select().where(
                (Goods.goods_id == goods_data['goods_id'])
            ).first()
            
            if existing_goods:
                # 如果存在，则更新记录
                query = Goods.update(
                    goods_name=goods_data['goods_name'],
                    store_id=goods_data['store_id'],
                    store_name=goods_data['store_name'],
                    order_id=goods_data['order_id'],
                    payment_amount=goods_data['payment_amount'],
                    sales_amount=goods_data['sales_amount'],
                    sales_cost=goods_data['sales_cost'],
                    gross_profit_1_occurred=goods_data['gross_profit_1_occurred'],
                    gross_profit_1_rate=goods_data['gross_profit_1_rate'],
                    advertising_expenses=goods_data.get('advertising_expenses', 0),
                    advertising_ratio=goods_data['advertising_ratio'],
                    gross_profit_3=goods_data['gross_profit_3'],
                    gross_profit_3_rate=goods_data['gross_profit_3_rate'],
                    gross_profit_4=goods_data['gross_profit_4'],
                    gross_profit_4_rate=goods_data['gross_profit_4_rate'],
                    net_profit=goods_data['net_profit'],
                    net_profit_rate=goods_data['net_profit_rate'],
                    updated_at=goods_data['updated_at']
                ).where(Goods.id == existing_goods.id)
                query.execute()
                updated_count += 1
            else:
                # 如果不存在，则创建新记录
                Goods.create(
                    goods_id=goods_data['goods_id'],
                    goods_name=goods_data['goods_name'],
                    store_id=goods_data['store_id'],
                    store_name=goods_data['store_name'],
                    order_id=goods_data['order_id'],
                    payment_amount=goods_data['payment_amount'],
                    sales_amount=goods_data['sales_amount'],
                    sales_cost=goods_data['sales_cost'],
                    gross_profit_1_occurred=goods_data['gross_profit_1_occurred'],
                    gross_profit_1_rate=goods_data['gross_profit_1_rate'],
                    advertising_expenses=goods_data.get('advertising_expenses', 0),
                    advertising_ratio=goods_data['advertising_ratio'],
                    gross_profit_3=goods_data['gross_profit_3'],
                    gross_profit_3_rate=goods_data['gross_profit_3_rate'],
                    gross_profit_4=goods_data['gross_profit_4'],
                    gross_profit_4_rate=goods_data['gross_profit_4_rate'],
                    net_profit=goods_data['net_profit'],
                    net_profit_rate=goods_data['net_profit_rate'],
                    creator=goods_data['creator'],
                    created_at=goods_data['created_at'],
                    updated_at=goods_data['updated_at']
                )
                created_count += 1
            
            processed_count += 1

        return {
            "message": f"成功同步商品数据，处理了 {processed_count} 条商品记录，新增 {created_count} 条，更新 {updated_count} 条"
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
                'created_at': good.created_at,
                'updated_at': good.updated_at
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