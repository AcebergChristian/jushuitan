from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import List
import os
import json
from datetime import datetime, date, timedelta
import traceback
from peewee import fn


from .. import schemas
from ..services import product_service
from ..database import get_db
from ..models.database import JushuitanProduct, Goods, User, Store
from .auth import get_current_user
from ..spiders.jushuitan_api import get_all_jushuitan_orders



router = APIRouter()


# 聚水潭数据相关路由
@router.get("/jushuitan_products/")
def read_jushuitan_products(search: str = ""):
    """获取聚水潭商品数据列表"""
    try:
        with get_db() as db:
            # 构建查询
            query = JushuitanProduct.select().where(JushuitanProduct.is_del == False)
            
            # 如果有搜索条件，添加搜索过滤
            if search:
                query = query.where(JushuitanProduct.disInnerOrderGoodsViewList.contains(search))
            
            # 获取总数
            total_count = query.count()
            
            # 按创建时间降序排序
            query = query.order_by(JushuitanProduct.created_at.desc())
            
            # 将结果转换为字典列表
            result = []
            for record in query:
                record_dict = {}
                for field in JushuitanProduct._meta.fields.values():
                    field_value = getattr(record, field.name)
                    # 将datetime转换为字符串
                    if isinstance(field_value, datetime):
                        record_dict[field.name] = field_value.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        record_dict[field.name] = field_value
                result.append(record_dict)
            
            # 返回包含数据和总数的对象
            return {
                "data": result,
                "total": total_count
            }
    except Exception as e:
        print(f"查询聚水潭商品数据失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"查询聚水潭商品数据失败: {str(e)}")





# 点击获取同步数据进表里
@router.post("/sync_jushuitan_data")
def sync_jushuitan_data(request: dict = None):
    """同步聚水潭数据到数据库，根据oid字段处理重复数据 - 使用批量操作优化性能"""

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
    
    # 获取系统当前日期
    current_system_date = datetime.now().date()
    start_of_day = datetime.combine(current_system_date, datetime.min.time())
    end_of_day = datetime.combine(current_system_date, datetime.max.time())
    
    processed_count = 0
    
    with get_db() as db:
        with db.atomic():
            # 步骤1: 批量删除当天的重复记录
            # 收集所有新数据的oid
            new_oids = [item.get('oid') for item in new_data_list if item.get('oid')]
            
            if new_oids:
                # 批量删除当天已存在的相同oid记录
                delete_count = (JushuitanProduct
                    .delete()
                    .where(
                        (JushuitanProduct.oid.in_(new_oids)) &
                        (JushuitanProduct.created_at >= start_of_day) &
                        (JushuitanProduct.created_at <= end_of_day)
                    )
                    .execute())
                
                print(f"批量删除了 {delete_count} 条当天的重复记录")
            
            # 步骤2: 准备批量插入的数据
            batch_data = []
            for item in new_data_list:
                if item.get('oid'):  # 只处理有oid的记录
                    batch_data.append({
                        'oid': item.get('oid'),
                        'isSuccess': item.get('isSuccess'),
                        'msg': item.get('msg'),
                        'purchaseAmt': item.get('purchaseAmt'),
                        'totalAmt': item.get('totalAmt'),
                        'discountAmt': item.get('discountAmt'),
                        'commission': item.get('commission'),
                        'freight': item.get('freight'),
                        'payAmount': item.get('payAmount'),
                        'paidAmount': item.get('paidAmount'),
                        'totalPurchasePriceGoods': item.get('totalPurchasePriceGoods'),
                        'smallProgramFreight': item.get('smallProgramFreight'),
                        'totalTransactionPurchasePrice': item.get('totalTransactionPurchasePrice'),
                        'smallProgramCommission': item.get('smallProgramCommission'),
                        'smallProgramPaidAmount': item.get('smallProgramPaidAmount'),
                        'freightCalcRule': item.get('freightCalcRule'),
                        'oaId': item.get('oaId'),
                        'soId': item.get('soId'),
                        'rawSoId': item.get('rawSoId'),
                        'mergeSoIds': item.get('mergeSoIds'),
                        'soIdList': str(item.get('soIdList', [])),
                        'supplierCoId': item.get('supplierCoId'),
                        'supplierName': item.get('supplierName'),
                        'channelCoId': item.get('channelCoId'),
                        'channelName': item.get('channelName'),
                        'shopId': item.get('shopId'),
                        'shopType': item.get('shopType'),
                        'shopName': item.get('shopName'),
                        'disInnerOrderGoodsViewList': str(item.get('disInnerOrderGoodsViewList', [])),
                        'orderTime': item.get('orderTime'),
                        'payTime': item.get('payTime'),
                        'deliveryDate': item.get('deliveryDate'),
                        'expressCode': item.get('expressCode'),
                        'expressCompany': item.get('expressCompany'),
                        'trackNo': item.get('trackNo'),
                        'orderStatus': item.get('orderStatus'),
                        'errorMsg': item.get('errorMsg'),
                        'errorDesc': item.get('errorDesc'),
                        'labels': json.dumps(item.get('labels', []), ensure_ascii=False),
                        'buyerMessage': item.get('buyerMessage'),
                        'remark': item.get('remark'),
                        'sellerFlag': item.get('sellerFlag'),
                        'updated': item.get('updated'),
                        'clientPaidAmt': item.get('clientPaidAmt'),
                        'goodsQty': item.get('goodsQty'),
                        'goodsAmt': item.get('goodsAmt'),
                        'freeAmount': item.get('freeAmount'),
                        'orderType': item.get('orderType'),
                        'isSplit': item.get('isSplit', False),
                        'isMerge': item.get('isMerge', False),
                        'planDeliveryDate': item.get('planDeliveryDate'),
                        'deliverTimeLeft': item.get('deliverTimeLeft'),
                        'printCount': item.get('printCount'),
                        'ioId': item.get('ioId'),
                        'receiverState': item.get('receiverState'),
                        'receiverCity': item.get('receiverCity'),
                        'receiverDistrict': item.get('receiverDistrict'),
                        'weight': item.get('weight'),
                        'realWeight': item.get('realWeight'),
                        'wmsCoId': item.get('wmsCoId'),
                        'wmsCoName': item.get('wmsCoName'),
                        'drpAmount': item.get('drpAmount'),
                        'shopSite': item.get('shopSite'),
                        'isDeliveryPrinted': item.get('isDeliveryPrinted'),
                        'fullReceiveData': item.get('fullReceiveData'),
                        'fuzzFullReceiverInfo': item.get('fuzzFullReceiverInfo'),
                        'shopBuyerId': item.get('shopBuyerId'),
                        'logisticsNos': item.get('logisticsNos'),
                        'openId': item.get('openId'),
                        'printedList': item.get('printedList'),
                        'note': item.get('note'),
                        'receiverTown': item.get('receiverTown'),
                        'solution': item.get('solution'),
                        'orderFrom': item.get('orderFrom'),
                        'linkOid': item.get('linkOid'),
                        'channelOid': item.get('channelOid'),
                        'isSupplierInitiatedReissueOrExchange': item.get('isSupplierInitiatedReissueOrExchange'),
                        'confirmDate': item.get('confirmDate'),
                        'topDrpCoIdFrom': item.get('topDrpCoIdFrom'),
                        'topDrpOrderId': item.get('topDrpOrderId'),
                        'orderIdentity': item.get('orderIdentity'),
                        'originalSoId': item.get('originalSoId'),
                        'isVirtualShipment': item.get('isVirtualShipment', False),
                        'relationshipBySoIdMd5': item.get('relationshipBySoIdMd5'),
                        'online': item.get('online', False),
                        'data_type': 'regular' if item.get('orderStatus') not in ['Cancelled', 'Refunded', 'Closed'] else 'cancel',
                        'is_del': False,
                        'created_at': datetime.now(),
                        'updated_at': datetime.now()
                    })
            
            # 步骤3: 批量插入新记录（分批处理，每批500条）
            batch_size = 500
            for i in range(0, len(batch_data), batch_size):
                batch = batch_data[i:i + batch_size]
                JushuitanProduct.insert_many(batch).execute()
                processed_count += len(batch)
                print(f"已批量插入 {len(batch)} 条记录，总计 {processed_count}/{len(batch_data)}")
    
    try:
        # 同步商品和店铺数据
        goods_processed_count, _ = sync_goods(sync_date, new_data_list)
        store_processed_count, _ = sync_stores(sync_date, new_data_list)
        
    except Exception as e:
        print(f"同步商品数据时发生错误: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"同步商品数据失败: {str(e)}")

    return {
        "message": f"成功同步聚水潭数据，处理了 {processed_count} 条订单记录、{goods_processed_count} 条商品记录和 {store_processed_count} 条店铺记录",
        "processed_count": processed_count,
        "goods_processed_count": goods_processed_count,
        "stores_processed_count": store_processed_count
    }









# 批量新增商品台账方法
def sync_goods(sync_date, orders):
    """
    同步订单数据中的商品信息到goods表
    - 从两个不同的API获取销售金额和销售成本数据
    - 提取disInnerOrderGoodsViewList中的商品数据
    - 按shopIid聚合相同商品的金额
    - 支持按指定日期同步数据
    """

    try:
        # 导入新的API方法
        from backend.spiders.jushuitan_api import get_jushuitan_orders_for_sales_amount, get_jushuitan_orders_for_sales_cost
        
        # 获取销售金额数据（包含所有状态）
        print(f"正在获取销售金额数据，日期: {sync_date}")
        sales_amount_data = get_jushuitan_orders_for_sales_amount(sync_date=sync_date)
        
        # 获取销售成本数据（不包含已取消和被拆分）
        print(f"正在获取销售成本数据，日期: {sync_date}")
        sales_cost_data = get_jushuitan_orders_for_sales_cost(sync_date=sync_date)
        
        if not sales_amount_data or 'data' not in sales_amount_data:
            raise HTTPException(status_code=400, detail="获取销售金额数据失败")
        
        if not sales_cost_data or 'data' not in sales_cost_data:
            raise HTTPException(status_code=400, detail="获取销售成本数据失败")
        
        # 构建销售金额映射表：key = shopIid, value = payAmount
        sales_amount_map = {}
        for order in sales_amount_data.get('data', []):
            try:
                payAmount = float(order.get('payAmount', 0) or 0)
                
                # 解析商品列表
                goods_list_raw = order.get('disInnerOrderGoodsViewList')
                try:
                    if isinstance(goods_list_raw, str):
                        goods_list = json.loads(goods_list_raw)
                    else:
                        goods_list = goods_list_raw
                except json.JSONDecodeError:
                    continue
                
                if not isinstance(goods_list, list):
                    if goods_list is None:
                        goods_list = []
                    else:
                        goods_list = [goods_list]
                
                # 遍历商品，累加销售金额
                for goods_item in goods_list:
                    if not isinstance(goods_item, dict):
                        continue
                    
                    shop_iid = goods_item.get('shopIid')
                    if not shop_iid:
                        continue
                    
                    # 获取订单时间
                    order_time_str = order.get('orderTime')
                    order_datetime = None
                    if order_time_str:
                        try:
                            if 'T' in order_time_str:
                                order_datetime = datetime.fromisoformat(order_time_str.replace('Z', '+00:00'))
                            else:
                                order_datetime = datetime.strptime(order_time_str, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            try:
                                order_datetime = datetime.strptime(order_time_str, '%Y-%m-%d')
                            except ValueError:
                                order_datetime = datetime.now()
                    else:
                        order_datetime = datetime.now()
                    
                    # 使用shopIid + 订单时间作为唯一键
                    unique_key = f"{shop_iid}_{order_datetime.strftime('%Y%m%d%H%M%S')}"
                    
                    if unique_key not in sales_amount_map:
                        sales_amount_map[unique_key] = {
                            'shop_iid': shop_iid,
                            'item_name': goods_item.get('itemName', '未知商品'),
                            'shop_id': order.get('shopId') or '',
                            'shop_name': order.get('shopName') or '未知店铺',
                            'order_id': order.get('oid') or '',
                            'so_id': order.get('soId') or '',  # 线上订单号
                            'order_time': order_datetime,
                            'sales_amount': payAmount
                        }
                    else:
                        sales_amount_map[unique_key]['sales_amount'] += payAmount
                        
            except Exception as e:
                print(f"处理销售金额订单时出错: {e}")
                continue
        
        # 构建销售成本映射表：key = shopIid, value = drpAmount
        sales_cost_map = {}
        for order in sales_cost_data.get('data', []):
            try:
                drpAmount = float(order.get('drpAmount', 0) or 0)
                
                # 解析商品列表
                goods_list_raw = order.get('disInnerOrderGoodsViewList')
                try:
                    if isinstance(goods_list_raw, str):
                        goods_list = json.loads(goods_list_raw)
                    else:
                        goods_list = goods_list_raw
                except json.JSONDecodeError:
                    continue
                
                if not isinstance(goods_list, list):
                    if goods_list is None:
                        goods_list = []
                    else:
                        goods_list = [goods_list]
                
                # 遍历商品，累加销售成本
                for goods_item in goods_list:
                    if not isinstance(goods_item, dict):
                        continue
                    
                    shop_iid = goods_item.get('shopIid')
                    if not shop_iid:
                        continue
                    
                    # 获取订单时间
                    order_time_str = order.get('orderTime')
                    order_datetime = None
                    if order_time_str:
                        try:
                            if 'T' in order_time_str:
                                order_datetime = datetime.fromisoformat(order_time_str.replace('Z', '+00:00'))
                            else:
                                order_datetime = datetime.strptime(order_time_str, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            try:
                                order_datetime = datetime.strptime(order_time_str, '%Y-%m-%d')
                            except ValueError:
                                order_datetime = datetime.now()
                    else:
                        order_datetime = datetime.now()
                    
                    # 使用shopIid + 订单时间作为唯一键
                    unique_key = f"{shop_iid}_{order_datetime.strftime('%Y%m%d%H%M%S')}"
                    
                    if unique_key not in sales_cost_map:
                        sales_cost_map[unique_key] = drpAmount
                    else:
                        sales_cost_map[unique_key] += drpAmount
                        
            except Exception as e:
                print(f"处理销售成本订单时出错: {e}")
                continue
        
        # 合并两个映射表，构建最终的商品数据
        goods_dict = {}
        for unique_key, sales_data in sales_amount_map.items():
            # 获取对应的销售成本
            sales_cost = sales_cost_map.get(unique_key, 0.0)
            
            # 如果指定了同步日期，使用该日期，否则使用订单创建日期
            if sync_date:
                order_created_at = datetime.combine(sync_date, datetime.min.time())
            else:
                order_created_at = datetime.now()
            
            goods_dict[unique_key] = {
                'goods_id': sales_data['shop_iid'],
                'goods_name': sales_data['item_name'],
                'store_id': sales_data['shop_id'],
                'store_name': sales_data['shop_name'],
                'order_id': sales_data['order_id'],
                'soId': sales_data['so_id'],  # 线上订单号
                'payment_amount': 0.0,  # 暂不使用
                'sales_amount': sales_data['sales_amount'],
                'refund_amount': 0.0,  # 暂不使用
                'sales_cost': sales_cost,
                'creator': 'system',
                'created_at': order_created_at,
                'goodorder_time': sales_data['order_time'],
                'updated_at': datetime.now()
            }
        
        # 删除之前同步的相同日期的数据（避免重复）
        if sync_date:
            start_of_day = datetime.combine(sync_date, datetime.min.time())
            end_of_day = datetime.combine(sync_date, datetime.max.time())
            Goods.delete().where(
                (Goods.goodorder_time >= start_of_day) & 
                (Goods.goodorder_time <= end_of_day)
            ).execute()
        else:
            Goods.delete().execute()

        # 使用insert_many批量插入新的商品记录
        goods_data_list = list(goods_dict.values())
        if goods_data_list:
            with get_db() as db:
                with db.atomic():
                    Goods.insert_many(goods_data_list).execute()

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
            
            gross_profit_4 = sales_amount - cost_amount - ad_cost
            gross_profit_4_rate = round(((sales_amount - cost_amount - ad_cost) / sales_amount) * 100, 2) if sales_amount > 0 else 0
            
            net_profit = sales_amount - cost_amount - ad_cost
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
            message_text = f"成功同步指定日期 {sync_date} 的商品数据，处理了 {processed_count} 条商品记录"
        else:
            message_text = f"成功同步商品数据，处理了 {processed_count} 条商品记录"

        return processed_count, message_text
        
    except Exception as e:
        print(f"同步商品数据时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"同步商品数据失败: {str(e)}")





# 批量新增店铺表数据
def sync_stores(sync_date, orders):
    """
    同步订单数据中的店铺信息到stores表
    - 从两个不同的API获取销售金额和销售成本数据
    - 按shopId聚合店铺数据
    - 计算各种利润指标和汇总数据
    - 支持按指定日期同步数据
    """
    
    try:
        # 导入新的API方法
        from backend.spiders.jushuitan_api import get_jushuitan_orders_for_sales_amount, get_jushuitan_orders_for_sales_cost
        
        # 获取销售金额数据（包含所有状态）
        print(f"正在获取店铺销售金额数据，日期: {sync_date}")
        sales_amount_data = get_jushuitan_orders_for_sales_amount(sync_date=sync_date)
        
        # 获取销售成本数据（不包含已取消和被拆分）
        print(f"正在获取店铺销售成本数据，日期: {sync_date}")
        sales_cost_data = get_jushuitan_orders_for_sales_cost(sync_date=sync_date)
        
        if not sales_amount_data or 'data' not in sales_amount_data:
            raise HTTPException(status_code=400, detail="获取店铺销售金额数据失败")
        
        if not sales_cost_data or 'data' not in sales_cost_data:
            raise HTTPException(status_code=400, detail="获取店铺销售成本数据失败")
        
        # 用于存储店铺数据的字典，以store_id和日期为唯一键
        stores_dict = {}
        
        # 处理销售金额数据
        for order in sales_amount_data.get('data', []):
            try:
                store_id = order.get('shopId')
                store_name = order.get('shopName', '未知店铺')
                
                if not store_id:
                    continue
                
                # 如果指定了同步日期，将日期加入store_id以确保唯一性
                if sync_date:
                    unique_store_id = f"{store_id}_{sync_date.strftime('%Y%m%d')}"
                else:
                    unique_store_id = store_id
                
                payAmount = float(order.get('payAmount', 0) or 0)
                
                # 解析商品列表
                goods_list_raw = order.get('disInnerOrderGoodsViewList')
                try:
                    if isinstance(goods_list_raw, str):
                        goods_list = json.loads(goods_list_raw)
                    else:
                        goods_list = goods_list_raw
                except json.JSONDecodeError:
                    continue
                
                if not isinstance(goods_list, list):
                    if goods_list is None:
                        goods_list = []
                    else:
                        goods_list = [goods_list]
                
                # 获取订单时间
                order_time_str = order.get('orderTime')
                order_datetime = None
                if order_time_str:
                    try:
                        if 'T' in order_time_str:
                            order_datetime = datetime.fromisoformat(order_time_str.replace('Z', '+00:00'))
                        else:
                            order_datetime = datetime.strptime(order_time_str, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        try:
                            order_datetime = datetime.strptime(order_time_str, '%Y-%m-%d')
                        except ValueError:
                            order_datetime = datetime.now()
                else:
                    order_datetime = datetime.now()
                
                # 如果指定了同步日期，使用该日期，否则使用当前时间
                if sync_date:
                    created_at = datetime.combine(sync_date, datetime.min.time())
                else:
                    created_at = datetime.now()
                
                # 初始化或累加店铺数据
                if unique_store_id not in stores_dict:
                    stores_dict[unique_store_id] = {
                        'store_id': unique_store_id,
                        'store_name': store_name,
                        'total_payment_amount': 0.0,
                        'total_sales_amount': 0.0,
                        'total_refund_amount': 0.0,
                        'total_sales_cost': 0.0,
                        'total_gross_profit_1_occurred': 0.0,
                        'total_advertising_expenses': 0.0,
                        'total_gross_profit_3': 0.0,
                        'total_gross_profit_4': 0.0,
                        'total_net_profit': 0.0,
                        'goods_count': 0,
                        'order_count': 0,
                        'creator': 'system',
                        'last_order_time': order_datetime,
                        'created_at': created_at,
                        'updated_at': datetime.now()
                    }
                
                # 累加销售金额
                store_data = stores_dict[unique_store_id]
                store_data['total_sales_amount'] += payAmount
                store_data['goods_count'] += len(goods_list)
                store_data['order_count'] += 1
                
                # 更新最后订单时间
                if order_datetime and (not store_data['last_order_time'] or order_datetime > store_data['last_order_time']):
                    store_data['last_order_time'] = order_datetime
                
            except Exception as e:
                print(f"处理店铺销售金额订单时出错: {e}")
                continue
        
        # 处理销售成本数据
        for order in sales_cost_data.get('data', []):
            try:
                store_id = order.get('shopId')
                
                if not store_id:
                    continue
                
                # 如果指定了同步日期，将日期加入store_id以确保唯一性
                if sync_date:
                    unique_store_id = f"{store_id}_{sync_date.strftime('%Y%m%d')}"
                else:
                    unique_store_id = store_id
                
                drpAmount = float(order.get('drpAmount', 0) or 0)
                
                # 累加销售成本
                if unique_store_id in stores_dict:
                    stores_dict[unique_store_id]['total_sales_cost'] += drpAmount
                
            except Exception as e:
                print(f"处理店铺销售成本订单时出错: {e}")
                continue
        
        # 删除之前同步的相同日期的数据（避免重复）
        if sync_date:
            start_of_day = datetime.combine(sync_date, datetime.min.time())
            end_of_day = datetime.combine(sync_date, datetime.max.time())
            
            Store.delete().where(
                (Store.created_at >= start_of_day) & 
                (Store.created_at <= end_of_day)
            ).execute()
        else:
            Store.delete().execute()

        # 使用insert_many批量插入新的店铺记录
        stores_data_list = list(stores_dict.values())
        if stores_data_list:
            with get_db() as db:
                with db.atomic():
                    Store.insert_many(stores_data_list).execute()

        # 计算利润相关指标并更新
        all_new_stores = list(Store.select())
        
        for store_record in all_new_stores:
            # 确保所有数值字段都不为None
            sales_amount = store_record.total_sales_amount or 0.0
            cost_amount = store_record.total_sales_cost or 0.0
            
            # 计算各种利润指标
            gross_profit_1_occurred = sales_amount - cost_amount
            avg_gross_profit_1_rate = round(((sales_amount - cost_amount) / sales_amount) * 100, 2) if sales_amount > 0 else 0
            
            # 获取广告费用，如果为None则默认为0
            ad_cost = store_record.total_advertising_expenses or 0
            avg_advertising_ratio = round((ad_cost / sales_amount) * 100, 2) if sales_amount > 0 else 0
            
            gross_profit_3 = sales_amount - cost_amount - ad_cost
            avg_gross_profit_3_rate = round(((sales_amount - cost_amount - ad_cost) / sales_amount) * 100, 2) if sales_amount > 0 else 0
            
            gross_profit_4 = sales_amount - cost_amount - ad_cost
            avg_gross_profit_4_rate = round(((sales_amount - cost_amount - ad_cost) / sales_amount) * 100, 2) if sales_amount > 0 else 0
            
            net_profit = sales_amount - cost_amount - ad_cost
            avg_net_profit_rate = round(((sales_amount - cost_amount - ad_cost) / sales_amount) * 100, 2) if sales_amount > 0 else 0
            
            # 更新利润相关字段
            store_record.total_gross_profit_1_occurred = gross_profit_1_occurred
            store_record.avg_gross_profit_1_rate = avg_gross_profit_1_rate
            store_record.avg_advertising_ratio = avg_advertising_ratio
            store_record.total_gross_profit_3 = gross_profit_3
            store_record.avg_gross_profit_3_rate = avg_gross_profit_3_rate
            store_record.total_gross_profit_4 = gross_profit_4
            store_record.avg_gross_profit_4_rate = avg_gross_profit_4_rate
            store_record.total_net_profit = net_profit
            store_record.avg_net_profit_rate = avg_net_profit_rate
            store_record.updated_at = datetime.now()
            store_record.save()
        
        # 统计处理结果
        processed_count = len(stores_dict)
        
        # 根据是否指定了同步日期返回不同的消息
        if sync_date:
            message_text = f"成功同步指定日期 {sync_date} 的店铺数据，处理了 {processed_count} 条店铺记录"
        else:
            message_text = f"成功同步店铺数据，处理了 {processed_count} 条店铺记录"

        return processed_count, message_text
        
    except Exception as e:
        print(f"同步店铺数据时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"同步店铺数据失败: {str(e)}")






# 商品台账查询接口 - 支持分页和模糊查询
@router.get("/goods/")
def get_goods_list(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回的记录数"),
    search: str = Query("", description="商品名称模糊查询")
):
    """
    获取商品列表，支持分页和商品名称模糊查询
    关联 pdd_ads 表获取广告费，关联 pdd_bill_records 表获取退款金额
    """
    
    try:
        from backend.models.database import PddTable, PddBillRecord
        
        # 构建查询
        query = Goods.select()
        
        # 如果有搜索条件，添加模糊查询
        if search:
            query = query.where(Goods.goods_name.contains(search))
        
        # 排除已删除的记录
        query = query.where(Goods.is_del == False)
        
        # 按创建时间降序排列
        query = query.order_by(Goods.created_at.desc())

        # 获取总数
        total_count = query.count()
        
        # 应用分页
        goods_list = query.offset(skip).limit(limit).execute()
        
        # 转换为字典列表，并关联广告费和退款金额
        result = []
        for good in goods_list:
            # 关联 pdd_ads 表获取广告费（按 goods_id 和 store_id 匹配）
            advertising_expenses = 0.0
            if good.goods_id and good.store_id:
                # 查询该商品的广告费总和
                pdd_ads = PddTable.select(fn.SUM(PddTable.orderSpendNetCostPerOrder).alias('total_ad_cost')).where(
                    (PddTable.goods_id == good.goods_id) &
                    (PddTable.store_id == good.store_id) &
                    (PddTable.is_del == False)
                ).scalar()
                advertising_expenses = float(pdd_ads) if pdd_ads else 0.0
            
            # 关联 pdd_bill_records 表获取退款金额（按 shop_id 和 order_sn 匹配）
            refund_amount = 0.0
            if good.store_id and good.order_id:
                # 查询该订单的退款金额总和
                bill_refund = PddBillRecord.select(fn.SUM(PddBillRecord.amount).alias('total_refund')).where(
                    (PddBillRecord.shop_id == good.store_id) &
                    (PddBillRecord.order_sn == good.order_id) &
                    (PddBillRecord.is_del == False)
                ).scalar()
                refund_amount = float(bill_refund) if bill_refund else 0.0
            
            # 使用关联查询的值，如果没有则使用商品表中的值
            final_advertising_expenses = advertising_expenses if advertising_expenses > 0 else (good.advertising_expenses or 0.0)
            final_refund_amount = refund_amount if refund_amount > 0 else (good.refund_amount or 0.0)
            
            # 重新计算利润指标（使用关联后的广告费和退款金额）
            sales_amount = good.sales_amount or 0.0
            sales_cost = good.sales_cost or 0.0
            
            gross_profit_1_occurred = sales_amount - sales_cost
            gross_profit_1_rate = (gross_profit_1_occurred / sales_amount * 100) if sales_amount > 0 else 0.0
            
            advertising_ratio = (final_advertising_expenses / sales_amount * 100) if sales_amount > 0 else 0.0
            
            gross_profit_3 = sales_amount - sales_cost - final_advertising_expenses
            gross_profit_3_rate = (gross_profit_3 / sales_amount * 100) if sales_amount > 0 else 0.0
            
            gross_profit_4 = gross_profit_3  # 可以根据需要添加其他费用
            gross_profit_4_rate = (gross_profit_4 / sales_amount * 100) if sales_amount > 0 else 0.0
            
            net_profit = gross_profit_3  # 净利润
            net_profit_rate = (net_profit / sales_amount * 100) if sales_amount > 0 else 0.0
            
            good_dict = {
                'id': good.id,
                'goods_id': good.goods_id,
                'goods_name': good.goods_name,
                'store_id': good.store_id,
                'store_name': good.store_name,
                'order_id': good.order_id,
                'payment_amount': good.payment_amount,
                'sales_amount': sales_amount,
                'refund_amount': round(final_refund_amount, 2),  # 使用关联查询的退款金额
                'sales_cost': sales_cost,
                'gross_profit_1_occurred': round(gross_profit_1_occurred, 2),
                'gross_profit_1_rate': round(gross_profit_1_rate, 2),
                'advertising_expenses': round(final_advertising_expenses, 2),  # 使用关联查询的广告费
                'advertising_ratio': round(advertising_ratio, 2),
                'gross_profit_3': round(gross_profit_3, 2),
                'gross_profit_3_rate': round(gross_profit_3_rate, 2),
                'gross_profit_4': round(gross_profit_4, 2),
                'gross_profit_4_rate': round(gross_profit_4_rate, 2),
                'net_profit': round(net_profit, 2),
                'net_profit_rate': round(net_profit_rate, 2),
                'is_del': good.is_del,
                'creator': good.creator,
                'goodorder_time': good.goodorder_time.strftime("%Y-%m-%d %H:%M:%S") if good.goodorder_time else "",
                'created_at': good.created_at.strftime("%Y-%m-%d %H:%M:%S") if good.created_at else "",
                'updated_at': good.updated_at.strftime("%Y-%m-%d %H:%M:%S") if good.updated_at else ""
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
def get_store_goods(
    start_date: str = Query(None, description="开始日期，格式：YYYY-MM-DD"),
    end_date: str = Query(None, description="结束日期，格式：YYYY-MM-DD"),
    current_user = Depends(get_current_user)
):
    """
    根据当前登录用户的goods_stores字段查询店铺数据
    管理员可查看所有数据，普通用户只能查看自己的数据
    直接查询店铺表，返回汇总数据
    关联 pdd_ads 表获取广告费，关联 pdd_bill_records 表获取退款金额
    返回包含销售金额、成本、利润等统计信息的数据
    支持按日期范围查询
    """
    
    from backend.models.database import PddTable, PddBillRecord

    # 判断是否为管理员
    is_admin = current_user.role == 'admin'
    
    # 构建查询条件
    query_conditions = [Store.is_del == False]
    
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
            # 使用last_order_time字段进行日期筛选
            query_conditions.append((Store.last_order_time >= start_dt) & (Store.last_order_time <= end_dt))
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式不正确，请使用 YYYY-MM-DD 格式")
    
    if is_admin:
        # 管理员查看所有店铺数据
        store_records = Store.select().where(*query_conditions)
    else:
        # 普通用户查看自己关联的店铺信息
        user_goods_stores = current_user.get_goods_stores()
        
        if not user_goods_stores:
            return {
                "message": "当前用户未关联任何商品和店铺",
                "data": [],
                "summary": {}
            }
        
        # 提取商品ID列表，然后通过商品表找到对应的店铺ID
        goods_ids = [item.get('good_id') for item in user_goods_stores if item.get('good_id')]
        
        if not goods_ids:
            return {
                "message": "当前用户未关联任何有效商品",
                "data": [],
                "summary": {}
            }
        
        # 通过商品表获取用户关联的店铺ID
        user_store_ids = list(set([
            goods.store_id for goods in Goods.select(Goods.store_id).where(
                (Goods.goods_id.in_(goods_ids)) & (Goods.is_del == False)
            ) if goods.store_id
        ]))
        
        if not user_store_ids:
            return {
                "message": "当前用户关联的商品未找到对应店铺",
                "data": [],
                "summary": {}
            }
        
        # 添加店铺ID筛选条件
        query_conditions.append(Store.store_id.in_(user_store_ids))
        store_records = Store.select().where(*query_conditions)
    
    # 构建返回数据，并关联PDD表
    store_data = []
    for store in store_records:
        # 提取真实的店铺ID（去掉日期后缀）
        # Store表中的ID格式: shopId_YYYYMMDD (如: 18582224_20260126)
        real_store_id = store.store_id.split('_')[0] if '_' in store.store_id else store.store_id
        
        # 关联 pdd_ads 表获取该店铺的总广告费（按日期匹配）
        advertising_expenses_from_pdd = 0.0
        if store.last_order_time:
            # 提取 last_order_time 的日期部分 (YYYY-MM-DD)
            order_date = store.last_order_time.date()
            # 查询同一天的广告费
            pdd_ads = PddTable.select(fn.SUM(PddTable.orderSpendNetCostPerOrder).alias('total_ad_cost')).where(
                (PddTable.store_id == real_store_id) &
                (PddTable.data_date == order_date) &
                (PddTable.is_del == False)
            ).scalar()
            advertising_expenses_from_pdd = float(pdd_ads) if pdd_ads else 0.0
        
        # 关联 pdd_bill_records 表获取该店铺的总退款金额
        # 店铺级别：按 shop_id 和日期匹配（bill_date = last_order_time的日期部分）
        refund_amount_from_pdd = 0.0
        if store.last_order_time:
            # 提取 last_order_time 的日期部分 (YYYY-MM-DD)
            order_date = store.last_order_time.date()
            # 查询同一天的退款金额，使用 ABS 转换为正数
            bill_refund = PddBillRecord.select(fn.SUM(fn.ABS(PddBillRecord.amount)).alias('total_refund')).where(
                (PddBillRecord.shop_id == real_store_id) &
                (PddBillRecord.bill_date == order_date) &
                (PddBillRecord.is_del == False)
            ).scalar()
            refund_amount_from_pdd = float(bill_refund) if bill_refund else 0.0
        
        # 使用关联查询的值，如果没有则使用Store表中的值
        final_advertising_expenses = advertising_expenses_from_pdd if advertising_expenses_from_pdd > 0 else (store.total_advertising_expenses or 0.0)
        final_refund_amount = refund_amount_from_pdd if refund_amount_from_pdd > 0 else (store.total_refund_amount or 0.0)
        
        # 重新计算利润指标（使用关联后的广告费和退款金额）
        sales_amount = store.total_sales_amount or 0.0
        sales_cost = store.total_sales_cost or 0.0
        
        gross_profit_1_occurred = sales_amount - sales_cost
        gross_profit_1_rate = (gross_profit_1_occurred / sales_amount * 100) if sales_amount > 0 else 0.0
        
        advertising_ratio = (final_advertising_expenses / sales_amount * 100) if sales_amount > 0 else 0.0
        
        gross_profit_3 = sales_amount - sales_cost - final_advertising_expenses
        gross_profit_3_rate = (gross_profit_3 / sales_amount * 100) if sales_amount > 0 else 0.0
        
        gross_profit_4 = gross_profit_3
        gross_profit_4_rate = (gross_profit_4 / sales_amount * 100) if sales_amount > 0 else 0.0
        
        net_profit = gross_profit_3
        net_profit_rate = (net_profit / sales_amount * 100) if sales_amount > 0 else 0.0
        
        store_data.append({
            'store_id': store.store_id,
            'store_name': store.store_name,
            'goods_count': store.goods_count,
            'order_count': store.order_count,
            'payment_amount': store.total_payment_amount,
            'sales_amount': sales_amount,
            'refund_amount': round(final_refund_amount, 2),  # 使用关联查询的退款金额
            'sales_cost': sales_cost,
            'gross_profit_1_occurred': round(gross_profit_1_occurred, 2),
            'gross_profit_1_rate': round(gross_profit_1_rate, 2),
            'advertising_expenses': round(final_advertising_expenses, 2),  # 使用关联查询的广告费
            'advertising_ratio': round(advertising_ratio, 2),
            'gross_profit_3': round(gross_profit_3, 2),
            'gross_profit_3_rate': round(gross_profit_3_rate, 2),
            'gross_profit_4': round(gross_profit_4, 2),
            'gross_profit_4_rate': round(gross_profit_4_rate, 2),
            'net_profit': round(net_profit, 2),
            'net_profit_rate': round(net_profit_rate, 2),
            'last_order_time': store.last_order_time.strftime("%Y-%m-%d %H:%M:%S") if store.last_order_time else "",
            'created_at': store.created_at.strftime("%Y-%m-%d %H:%M:%S") if store.created_at else "",
            'updated_at': store.updated_at.strftime("%Y-%m-%d %H:%M:%S") if store.updated_at else ""
        })
    
    # 计算汇总统计数据
    summary = {}
    if store_data:
        summary = {
            'total_payment_amount': sum(item['payment_amount'] for item in store_data),
            'total_sales_amount': sum(item['sales_amount'] for item in store_data),
            'total_sales_cost': sum(item['sales_cost'] for item in store_data),
            'total_refund_amount': sum(item['refund_amount'] for item in store_data),
            'total_gross_profit_1_occurred': sum(item['gross_profit_1_occurred'] for item in store_data),
            'total_advertising_expenses': sum(item['advertising_expenses'] for item in store_data),
            'total_gross_profit_3': sum(item['gross_profit_3'] for item in store_data),
            'total_gross_profit_4': sum(item['gross_profit_4'] for item in store_data),
            'total_net_profit': sum(item['net_profit'] for item in store_data),
            'total_stores': len(store_data),
            'total_goods': sum(item['goods_count'] for item in store_data),
            'total_orders': sum(item['order_count'] for item in store_data)
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
    
    print(f"=== Debug: 查询店铺商品详情 ===")
    print(f"原始店铺ID: {store_id}")
    
    # 提取真实的店铺ID（去掉日期后缀）
    # Store表中的ID格式: shopId_YYYYMMDD (如: 18582224_20260126)
    # Goods表中的ID格式: shopId (如: 18582224)
    real_store_id = store_id.split('_')[0] if '_' in store_id else store_id
    print(f"提取后的店铺ID: {real_store_id}")
    print(f"用户: {current_user.username}, 角色: {current_user.role}")

    # 判断是否为管理员
    is_admin = current_user.role == 'admin'
    
    goods_data = []
    
    if is_admin:
        # 管理员可以查看任意店铺的商品数据
        print(f"管理员模式：查询店铺 {real_store_id} 的商品")
        goods_records = Goods.select().where(
            (Goods.store_id == real_store_id) & (Goods.is_del == False)
        ).order_by(Goods.goodorder_time.desc())
    else:
        # 普通用户只能查看自己关联的店铺商品数据
        user_goods_stores = current_user.get_goods_stores()
        # 提取用户关联的真实店铺ID（去掉日期后缀）
        user_store_ids = [item.get('store_id').split('_')[0] if '_' in item.get('store_id', '') else item.get('store_id') 
                         for item in user_goods_stores if item.get('store_id')]
        
        print(f"普通用户模式：用户关联的店铺IDs: {user_store_ids}")
        
        if real_store_id not in user_store_ids:
            print(f"权限检查失败：店铺 {real_store_id} 不在用户关联列表中")
            return {"message": "无权访问此店铺的商品详情", "data": [], "error": True}
        
        goods_records = Goods.select().where(
            (Goods.store_id == real_store_id) & (Goods.is_del == False)
        ).order_by(Goods.goodorder_time.desc())
    
    # 转换为列表以便调试
    goods_records_list = list(goods_records)
    print(f"查询到的商品记录数: {len(goods_records_list)}")
    
    # 如果没有记录，检查数据库中是否有该店铺的数据
    if len(goods_records_list) == 0:
        # 检查是否有该店铺的任何数据（包括已删除的）
        all_records = Goods.select().where(Goods.store_id == real_store_id)
        all_count = all_records.count()
        print(f"该店铺在数据库中的总记录数（包括已删除）: {all_count}")
        
        # 检查数据库中所有不同的店铺ID
        distinct_stores = Goods.select(Goods.store_id).distinct()
        store_ids_in_db = [s.store_id for s in distinct_stores if s.store_id]
        print(f"数据库中存在的店铺IDs: {store_ids_in_db[:10]}...")  # 只显示前10个
        
        # 检查store_id的类型和格式
        print(f"查询的store_id类型: {type(real_store_id)}, 值: '{real_store_id}'")
        if store_ids_in_db:
            print(f"数据库中第一个store_id类型: {type(store_ids_in_db[0])}, 值: '{store_ids_in_db[0]}'")
        
        return {
            "message": f"该店铺暂无商品数据。数据库中该店铺总记录数: {all_count}",
            "data": [],
            "debug": {
                "original_store_id": store_id,
                "real_store_id": real_store_id,
                "store_id_type": str(type(real_store_id)),
                "total_records_in_db": all_count,
                "sample_store_ids": store_ids_in_db[:5]
            }
        }

    # 导入PDD相关表
    from backend.models.database import PddTable, PddBillRecord
    
    # 按good_id进行分组并汇总数据
    grouped_goods = {}
    for record in goods_records_list:
        good_id = record.goods_id
        
        if good_id not in grouped_goods:
            # 初始化商品数据
            grouped_goods[good_id] = {
                'id': record.id,
                'good_id': record.goods_id,
                'good_name': record.goods_name,
                'store_id': record.store_id,
                'store_name': record.store_name,
                'order_ids': [record.order_id] if record.order_id else [],
                'so_ids': [record.soId] if record.soId else [],  # 收集线上订单号
                'payment_amount': record.payment_amount or 0.0,
                'sales_amount': record.sales_amount or 0.0,
                'sales_cost': record.sales_cost or 0.0,
                'refund_amount': record.refund_amount or 0.0,
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
                'first_goodorder_time': record.goodorder_time,
                'latest_goodorder_time': record.goodorder_time,
                'created_at': record.created_at,
                'updated_at': record.updated_at,
                'order_count': 1
            }
        else:
            # 累加数值字段
            existing = grouped_goods[good_id]
            existing['payment_amount'] += record.payment_amount or 0.0
            existing['sales_amount'] += record.sales_amount or 0.0
            existing['sales_cost'] += record.sales_cost or 0.0
            existing['refund_amount'] += record.refund_amount or 0.0
            existing['gross_profit_1_occurred'] += record.gross_profit_1_occurred or 0.0
            existing['advertising_expenses'] += record.advertising_expenses or 0.0
            existing['advertising_ratio'] += record.advertising_ratio or 0.0
            existing['gross_profit_3'] += record.gross_profit_3 or 0.0
            existing['gross_profit_4'] += record.gross_profit_4 or 0.0
            existing['net_profit'] += record.net_profit or 0.0
            
            # 更新订单ID列表
            if record.order_id:
                existing['order_ids'].append(record.order_id)
            # 更新线上订单号列表
            if record.soId:
                existing['so_ids'].append(record.soId)
            
            # 更新时间范围
            if record.goodorder_time and (not existing['latest_goodorder_time'] or record.goodorder_time > existing['latest_goodorder_time']):
                existing['latest_goodorder_time'] = record.goodorder_time
            if record.goodorder_time and (not existing['first_goodorder_time'] or record.goodorder_time < existing['first_goodorder_time']):
                existing['first_goodorder_time'] = record.goodorder_time
            
            # 更新更新时间
            if record.updated_at > existing['updated_at']:
                existing['updated_at'] = record.updated_at
            
            existing['order_count'] += 1
    
    print(f"分组后的商品数量: {len(grouped_goods)}")
    
    # 将分组结果转换为前端需要的格式，并关联PDD表数据
    for good_id, data in grouped_goods.items():
        # 关联 pdd_ads 表获取广告费（按 goods_id、store_id 和日期匹配）
        advertising_expenses_from_pdd = 0.0
        if good_id and data['store_id'] and data['latest_goodorder_time']:
            # 提取订单日期
            order_date = data['latest_goodorder_time'].date()
            pdd_ads = PddTable.select(fn.SUM(PddTable.orderSpendNetCostPerOrder).alias('total_ad_cost')).where(
                (PddTable.goods_id == good_id) &
                (PddTable.store_id == data['store_id']) &
                (PddTable.data_date == order_date) &
                (PddTable.is_del == False)
            ).scalar()
            advertising_expenses_from_pdd = float(pdd_ads) if pdd_ads else 0.0
        
        # 关联 pdd_bill_records 表获取退款金额（按 shop_id、so_ids 和日期匹配，使用ABS转正数）
        refund_amount_from_pdd = 0.0
        if data['store_id'] and data['so_ids'] and data['latest_goodorder_time']:
            # 提取订单日期
            order_date = data['latest_goodorder_time'].date()
            # 查询所有线上订单号的退款金额总和，使用ABS转换为正数
            bill_refund = PddBillRecord.select(fn.SUM(fn.ABS(PddBillRecord.amount)).alias('total_refund')).where(
                (PddBillRecord.shop_id == data['store_id']) &
                (PddBillRecord.order_sn.in_(data['so_ids'])) &
                (PddBillRecord.bill_date == order_date) &
                (PddBillRecord.is_del == False)
            ).scalar()
            refund_amount_from_pdd = float(bill_refund) if bill_refund else 0.0
        
        # 使用关联查询的值，如果没有则使用累加的值
        final_advertising_expenses = advertising_expenses_from_pdd if advertising_expenses_from_pdd > 0 else data['advertising_expenses']
        final_refund_amount = refund_amount_from_pdd if refund_amount_from_pdd > 0 else data['refund_amount']
        
        # 重新计算利润指标（使用关联后的广告费和退款金额）
        sales_amount = data['sales_amount']
        sales_cost = data['sales_cost']
        
        gross_profit_1_occurred = sales_amount - sales_cost
        gross_profit_1_rate = (gross_profit_1_occurred / sales_amount * 100) if sales_amount > 0 else 0.0
        
        advertising_ratio = (final_advertising_expenses / sales_amount * 100) if sales_amount > 0 else 0.0
        
        gross_profit_3 = sales_amount - sales_cost - final_advertising_expenses
        gross_profit_3_rate = (gross_profit_3 / sales_amount * 100) if sales_amount > 0 else 0.0
        
        gross_profit_4 = gross_profit_3
        gross_profit_4_rate = (gross_profit_4 / sales_amount * 100) if sales_amount > 0 else 0.0
        
        net_profit = gross_profit_3
        net_profit_rate = (net_profit / sales_amount * 100) if sales_amount > 0 else 0.0
        
        # 格式化时间
        first_time_str = data['first_goodorder_time'].strftime("%Y-%m-%d %H:%M:%S") if data['first_goodorder_time'] else ""
        latest_time_str = data['latest_goodorder_time'].strftime("%Y-%m-%d %H:%M:%S") if data['latest_goodorder_time'] else ""
        
        goods_data.append({
            'id': data['id'],
            'good_id': data['good_id'],
            'good_name': data['good_name'],
            'store_id': data['store_id'],
            'store_name': data['store_name'],
            'order_ids': ', '.join([oid for oid in data['order_ids'] if oid]),
            'so_ids': ', '.join([sid for sid in data['so_ids'] if sid]),  # 线上订单号
            'order_count': data['order_count'],
            'payment_amount': round(data['payment_amount'], 2),
            'sales_amount': round(sales_amount, 2),
            'sales_cost': round(sales_cost, 2),
            'refund_amount': round(final_refund_amount, 2),  # 使用关联查询的退款金额
            'gross_profit_1_occurred': round(gross_profit_1_occurred, 2),
            'gross_profit_1_rate': round(gross_profit_1_rate, 2),
            'advertising_expenses': round(final_advertising_expenses, 2),  # 使用关联查询的广告费
            'advertising_ratio': round(advertising_ratio, 2),
            'gross_profit_3': round(gross_profit_3, 2),
            'gross_profit_3_rate': round(gross_profit_3_rate, 2),
            'gross_profit_4': round(gross_profit_4, 2),
            'gross_profit_4_rate': round(data['gross_profit_4_rate'], 2),
            'net_profit': round(data['net_profit'], 2),
            'net_profit_rate': round(data['net_profit_rate'], 2),
            'first_order_time': first_time_str,
            'latest_order_time': latest_time_str,
            'created_at': data['created_at'].strftime("%Y-%m-%d %H:%M:%S") if data['created_at'] else "",
            'updated_at': data['updated_at'].strftime("%Y-%m-%d %H:%M:%S") if data['updated_at'] else ""
        })
    
    print(f"最终返回的商品数据数量: {len(goods_data)}")
    
    return {
        "message": "成功获取店铺商品详情",
        "data": goods_data
    }


# 调试端点：查看数据库中的店铺ID列表
@router.get("/debug/store_ids")
def debug_store_ids(current_user = Depends(get_current_user)):
    """
    调试端点：查看数据库中所有的店铺ID
    """
    try:
        # 从Goods表获取所有不同的店铺ID
        goods_stores = Goods.select(Goods.store_id, Goods.store_name).distinct()
        goods_store_list = [{'store_id': s.store_id, 'store_name': s.store_name} for s in goods_stores if s.store_id]
        
        # 从Store表获取所有店铺ID
        store_records = Store.select(Store.store_id, Store.store_name).where(Store.is_del == False)
        store_list = [{'store_id': s.store_id, 'store_name': s.store_name} for s in store_records]
        
        # 统计Goods表中的记录数
        total_goods = Goods.select().where(Goods.is_del == False).count()
        
        return {
            "message": "调试信息",
            "data": {
                "goods_table_stores": goods_store_list,
                "store_table_stores": store_list,
                "total_goods_records": total_goods
            }
        }
    except Exception as e:
        print(f"调试端点出错: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"调试失败: {str(e)}")





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
                'refund_amount': 0.0,
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
                'refund_amount': 0.0,
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
                    'refund_amount': 0.0,
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
            goods_by_id[goods_id]['refund_amount'] += record.refund_amount or 0.0
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
            total_refund_amount = sum(item['refund_amount'] for item in goods_data)
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
            total_refund_amount = 0.0
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
            'refund_amount': total_refund_amount,
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
                'refund_amount': record.refund_amount or 0.0,
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
            existing['refund_amount'] += record.refund_amount or 0.0
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
            'refund_amount': round(data['refund_amount'], 2),
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
# Note: pdd_products table is deprecated. Use PddTable (pdd_ads) or PddBillRecord instead.
# @router.get("/pdd_products/")
# def read_pdd_products(skip: int = 0, limit: int = 100):
#     """获取拼多多商品数据列表 - DEPRECATED"""
#     # This endpoint is deprecated as pdd_products table no longer exists
#     # Use /pdd/promotion or /pdd/bill endpoints instead
#     raise HTTPException(status_code=410, detail="此接口已废弃，请使用 /pdd/promotion 或 /pdd/bill 接口")






# 拼多多推广数据相关路由
@router.post("/pdd/promotion")
def get_pdd_promotion(request: dict):
    """
    获取拼多多推广数据
    
    请求参数:
        date: 日期字符串，格式为 YYYY-MM-DD
    
    返回:
        {
            "success": bool,
            "data": list,
            "total": int,
            "message": str
        }
    """
    # 获取请求中的日期参数
    date_str = request.get('date')
    
    if not date_str:
        raise HTTPException(status_code=400, detail="缺少日期参数")
    
    # 验证日期格式
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式不正确，请使用 YYYY-MM-DD 格式")
    
    # 调用拼多多API获取数据
    result = get_pdd_promotion_data(date_str)
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result['message'])
    
    return result
