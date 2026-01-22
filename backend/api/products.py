from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from .. import schemas
from ..services import product_service
from ..database import get_db
from ..models.database import User as UserModel, Product as ProductModel, Store as StoreModel, JushuitanProduct as JushuitanProductModel
import sqlite3
import os

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
    
    # 查询总数
    if search:
        cursor.execute('''SELECT COUNT(*) FROM jushuitan_products 
                         WHERE is_del = 0 
                         AND disInnerOrderGoodsViewList LIKE ?''', (f'%{search}%',))
    else:
        cursor.execute('SELECT COUNT(*) FROM jushuitan_products WHERE is_del = 0')
    
    total_count = cursor.fetchone()[0]
    
    # 查询数据
    if search:
        cursor.execute('''SELECT * FROM jushuitan_products 
                         WHERE is_del = 0 
                         AND disInnerOrderGoodsViewList LIKE ? 
                         LIMIT ? OFFSET ?''', (f'%{search}%', limit, skip))
    else:
        cursor.execute('SELECT * FROM jushuitan_products WHERE is_del = 0 LIMIT ? OFFSET ?', (limit, skip))
    
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

@router.get("/jushuitan_products/type/{data_type}")
def read_jushuitan_products_by_type(data_type: str, skip: int = 0, limit: int = 100):
    """根据数据类型获取聚水潭商品数据"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database.db")
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="数据库不存在")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM jushuitan_products WHERE data_type = ? AND is_del = 0 LIMIT ? OFFSET ?', (data_type, limit, skip))
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
    from ..spiders.jushuitan_api import get_jushuitan_orders
    from datetime import datetime
    
    # 获取聚水潭API数据
    api_response = get_jushuitan_orders()
    if not api_response or 'data' not in api_response:
        raise HTTPException(status_code=400, detail="获取聚水潭API数据失败")
    
    new_data_list = api_response.get('data', [])
    
    if not new_data_list:
        return {"message": "没有获取到新的聚水潭数据"}
    
    # 使用Peewee ORM进行数据库操作
    from ..models.database import JushuitanProduct
    
    # 遍历新数据，按日期分组
    data_by_date = {}
    for item in new_data_list:
        order_time = item.get('orderTime', '')
        # 提取日期部分 (格式如: "2026-01-01 10:30:00")
        date_part = order_time.split(' ')[0] if order_time else 'unknown'
        
        if date_part not in data_by_date:
            data_by_date[date_part] = []
        data_by_date[date_part].append(item)
    
    processed_count = 0
    
    with get_db() as db:
        for date_str, items_for_date in data_by_date.items():
            # 获取当天的所有oid
            oids_for_date = [item['oid'] for item in items_for_date if item.get('oid')]
            
            if oids_for_date:
                # 查找数据库中相同oid的记录
                existing_records = JushuitanProduct.select().where(
                    JushuitanProduct.oid.in_(oids_for_date)
                )
                
                # 删除现有的记录
                for record in existing_records:
                    record.delete_instance()
                
                # 插入新的记录
                for item in items_for_date:
                    # 创建新记录
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