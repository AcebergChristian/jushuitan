import sqlite3
from pathlib import Path
import os
from datetime import datetime
from typing import List

class DataToDB:
    def __init__(self, db_path: str = "jushuitan.db"):
        """初始化数据库连接"""
        self.db_path = db_path
        self.init_tables()
    
    def init_tables(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 删除旧的jushuitan_products表（如果存在）
        cursor.execute('DROP TABLE IF EXISTS jushuitan_products')
        
        # 创建新的聚水潭商品数据表，包含isdel字段
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jushuitan_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                oid TEXT,
                isSuccess TEXT,
                msg TEXT,
                purchaseAmt REAL,
                totalAmt REAL,
                discountAmt REAL,
                commission REAL,
                freight REAL,
                payAmount REAL,
                paidAmount REAL,
                totalPurchasePriceGoods REAL,
                smallProgramFreight REAL,
                totalTransactionPurchasePrice REAL,
                smallProgramCommission REAL,
                smallProgramPaidAmount REAL,
                freightCalcRule TEXT,
                oaId TEXT,
                soId TEXT,
                rawSoId TEXT,
                mergeSoIds TEXT,
                soIdList TEXT,
                supplierCoId TEXT,
                supplierName TEXT,
                channelCoId TEXT,
                channelName TEXT,
                shopId TEXT,
                shopType TEXT,
                shopName TEXT,
                disInnerOrderGoodsViewList TEXT,
                orderTime TEXT,
                payTime TEXT,
                deliveryDate TEXT,
                expressCode TEXT,
                expressCompany TEXT,
                trackNo TEXT,
                orderStatus TEXT,
                errorMsg TEXT,
                errorDesc TEXT,
                labels TEXT,
                buyerMessage TEXT,
                remark TEXT,
                sellerFlag INTEGER,
                updated TEXT,
                clientPaidAmt REAL,
                goodsQty INTEGER,
                goodsAmt REAL,
                freeAmount REAL,
                orderType TEXT,
                isSplit BOOLEAN,
                isMerge BOOLEAN,
                planDeliveryDate TEXT,
                deliverTimeLeft TEXT,
                printCount INTEGER,
                ioId TEXT,
                receiverState TEXT,
                receiverCity TEXT,
                receiverDistrict TEXT,
                weight TEXT,
                realWeight TEXT,
                wmsCoId TEXT,
                wmsCoName TEXT,
                drpAmount REAL,
                shopSite TEXT,
                isDeliveryPrinted TEXT,
                fullReceiveData TEXT,
                fuzzFullReceiverInfo TEXT,
                shopBuyerId TEXT,
                logisticsNos TEXT,
                openId TEXT,
                printedList TEXT,
                note TEXT,
                receiverTown TEXT,
                solution TEXT,
                orderFrom TEXT,
                linkOid TEXT,
                channelOid TEXT,
                isSupplierInitiatedReissueOrExchange TEXT,
                confirmDate TEXT,
                topDrpCoIdFrom TEXT,
                topDrpOrderId TEXT,
                orderIdentity TEXT,
                originalSoId TEXT,
                isVirtualShipment BOOLEAN,
                relationshipBySoIdMd5 TEXT,
                online BOOLEAN,
                data_type TEXT,
                isdel BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 修改pdd_products表，添加isdel字段
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pdd_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goods_id TEXT,
                name TEXT,
                price REAL,
                stock INTEGER,
                order_number TEXT,
                shop_name TEXT,
                buyer_nickname TEXT,
                supplier TEXT,
                status TEXT,
                shipping_company TEXT,
                customer_quantity INTEGER,
                customer_amount REAL,
                buyer_message TEXT,
                seller_remark TEXT,
                placing_time TEXT,
                payment_time TEXT,
                shipping_time TEXT,
                distributor TEXT,
                shipping_warehouse TEXT,
                platform TEXT,
                data_type TEXT,
                isdel BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_jushuitan_data(self, products_data: list):
        """
        插入聚水潭数据到数据库
        :param products_data: 聚水潭API返回的完整数据列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        all_data = []
        
        for item in products_data:
            # 根据订单状态判断是否为取消订单
            order_status = item.get('orderStatus', '')
            data_type = 'cancel' if order_status in ['Cancelled', 'Refunded', 'Closed'] else 'regular'
            
            # 将disInnerOrderGoodsViewList转换为字符串存储
            dis_inner_list_str = str(item.get('disInnerOrderGoodsViewList', []))
            
            # 将soIdList转换为字符串存储
            so_id_list_str = str(item.get('soIdList', []))
            
            # 将labels转换为字符串存储
            labels_str = str(item.get('labels', []))
            
            data_tuple = (
                item.get('oid', ''),                    # oid
                item.get('isSuccess', ''),              # isSuccess
                item.get('msg', ''),                    # msg
                item.get('purchaseAmt', 0),             # purchaseAmt
                item.get('totalAmt', 0),                # totalAmt
                item.get('discountAmt', 0),             # discountAmt
                item.get('commission', 0),              # commission
                item.get('freight', 0),                 # freight
                item.get('payAmount', 0),               # payAmount
                item.get('paidAmount', 0),              # paidAmount
                item.get('totalPurchasePriceGoods', 0), # totalPurchasePriceGoods
                item.get('smallProgramFreight', 0),     # smallProgramFreight
                item.get('totalTransactionPurchasePrice', 0), # totalTransactionPurchasePrice
                item.get('smallProgramCommission', 0),  # smallProgramCommission
                item.get('smallProgramPaidAmount', 0),  # smallProgramPaidAmount
                item.get('freightCalcRule', ''),        # freightCalcRule
                item.get('oaId', ''),                   # oaId
                item.get('soId', ''),                   # soId
                item.get('rawSoId', ''),                # rawSoId
                so_id_list_str,                         # soIdList (字符串)
                item.get('mergeSoIds', ''),             # mergeSoIds
                item.get('supplierCoId', ''),           # supplierCoId
                item.get('supplierName', ''),           # supplierName
                item.get('channelCoId', ''),            # channelCoId
                item.get('channelName', ''),            # channelName
                item.get('shopId', ''),                 # shopId
                item.get('shopType', ''),               # shopType
                item.get('shopName', ''),               # shopName
                dis_inner_list_str,                     # disInnerOrderGoodsViewList (字符串)
                item.get('orderTime', ''),              # orderTime
                item.get('payTime', ''),                # payTime
                item.get('deliveryDate', ''),           # deliveryDate
                item.get('expressCode', ''),            # expressCode
                item.get('expressCompany', ''),         # expressCompany
                item.get('trackNo', ''),                # trackNo
                item.get('orderStatus', ''),            # orderStatus
                item.get('errorMsg', ''),               # errorMsg
                item.get('errorDesc', ''),              # errorDesc
                labels_str,                             # labels (字符串)
                item.get('buyerMessage', ''),           # buyerMessage
                item.get('remark', ''),                 # remark
                item.get('sellerFlag', 0),              # sellerFlag
                item.get('updated', ''),                # updated
                item.get('clientPaidAmt', 0),           # clientPaidAmt
                item.get('goodsQty', 0),                # goodsQty
                item.get('goodsAmt', 0),                # goodsAmt
                item.get('freeAmount', 0),              # freeAmount
                item.get('orderType', ''),              # orderType
                item.get('isSplit', False),             # isSplit
                item.get('isMerge', False),             # isMerge
                item.get('planDeliveryDate', ''),       # planDeliveryDate
                item.get('deliverTimeLeft', ''),        # deliverTimeLeft
                item.get('printCount', 0),              # printCount
                item.get('ioId', ''),                   # ioId
                item.get('receiverState', ''),          # receiverState
                item.get('receiverCity', ''),           # receiverCity
                item.get('receiverDistrict', ''),       # receiverDistrict
                item.get('weight', ''),                 # weight
                item.get('realWeight', ''),             # realWeight
                item.get('wmsCoId', ''),                # wmsCoId
                item.get('wmsCoName', ''),              # wmsCoName
                item.get('drpAmount', 0),               # drpAmount
                item.get('shopSite', ''),               # shopSite
                item.get('isDeliveryPrinted', ''),      # isDeliveryPrinted
                item.get('fullReceiveData', ''),        # fullReceiveData
                item.get('fuzzFullReceiverInfo', ''),   # fuzzFullReceiverInfo
                item.get('shopBuyerId', ''),            # shopBuyerId
                item.get('logisticsNos', ''),           # logisticsNos
                item.get('openId', ''),                 # openId
                item.get('printedList', ''),            # printedList
                item.get('note', ''),                   # note
                item.get('receiverTown', ''),           # receiverTown
                item.get('solution', ''),               # solution
                item.get('orderFrom', ''),              # orderFrom
                item.get('linkOid', ''),                # linkOid
                item.get('channelOid', ''),             # channelOid
                item.get('isSupplierInitiatedReissueOrExchange', ''), # isSupplierInitiatedReissueOrExchange
                item.get('confirmDate', ''),            # confirmDate
                item.get('topDrpCoIdFrom', ''),         # topDrpCoIdFrom
                item.get('topDrpOrderId', ''),          # topDrpOrderId
                item.get('orderIdentity', ''),          # orderIdentity
                item.get('originalSoId', ''),           # originalSoId
                item.get('isVirtualShipment', False),   # isVirtualShipment
                item.get('relationshipBySoIdMd5', ''),  # relationshipBySoIdMd5
                item.get('online', False),              # online
                data_type,                              # data_type (regular/cancel)
                0                                       # isdel (默认为0，表示未删除)
            )
            all_data.append(data_tuple)
        
        # 批量插入数据
        if all_data:
            cursor.executemany('''
                INSERT INTO jushuitan_products (
                    oid, isSuccess, msg, purchaseAmt, totalAmt, discountAmt, 
                    commission, freight, payAmount, paidAmount, totalPurchasePriceGoods, 
                    smallProgramFreight, totalTransactionPurchasePrice, 
                    smallProgramCommission, smallProgramPaidAmount, 
                    freightCalcRule, oaId, soId, rawSoId, soIdList, mergeSoIds, 
                    supplierCoId, supplierName, channelCoId, channelName, 
                    shopId, shopType, shopName, disInnerOrderGoodsViewList, 
                    orderTime, payTime, deliveryDate, expressCode, expressCompany, 
                    trackNo, orderStatus, errorMsg, errorDesc, labels, 
                    buyerMessage, remark, sellerFlag, updated, clientPaidAmt, 
                    goodsQty, goodsAmt, freeAmount, orderType, isSplit, isMerge, 
                    planDeliveryDate, deliverTimeLeft, printCount, ioId, 
                    receiverState, receiverCity, receiverDistrict, weight, 
                    realWeight, wmsCoId, wmsCoName, drpAmount, shopSite, 
                    isDeliveryPrinted, fullReceiveData, fuzzFullReceiverInfo, 
                    shopBuyerId, logisticsNos, openId, printedList, note, 
                    receiverTown, solution, orderFrom, linkOid, channelOid, 
                    isSupplierInitiatedReissueOrExchange, confirmDate, 
                    topDrpCoIdFrom, topDrpOrderId, orderIdentity, originalSoId, 
                    isVirtualShipment, relationshipBySoIdMd5, online, 
                    data_type, isdel
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,......
            ''', all_data)
        
        conn.commit()
        conn.close()
        print(f"成功插入 {len(all_data)} 条聚水潭数据到数据库")
    
    def insert_pdd_data(self, pdd_products: List):
        """
        插入拼多多数据到数据库
        :param pdd_products: 拼多多商品数据列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        all_data = []
        for product in pdd_products:
            data_tuple = (
                getattr(product, 'goods_id', ''),
                getattr(product, 'name', ''),
                getattr(product, 'price', 0),
                getattr(product, 'stock', 0),
                getattr(product, 'order_number', ''),
                getattr(product, 'shop_name', ''),
                getattr(product, 'buyer_nickname', ''),
                getattr(product, 'supplier', ''),
                getattr(product, 'status', ''),
                getattr(product, 'shipping_company', ''),
                getattr(product, 'customer_quantity', 0),
                getattr(product, 'customer_amount', 0),
                getattr(product, 'buyer_message', ''),
                getattr(product, 'seller_remark', ''),
                getattr(product, 'placing_time', ''),
                getattr(product, 'payment_time', ''),
                getattr(product, 'shipping_time', ''),
                getattr(product, 'distributor', ''),
                getattr(product, 'shipping_warehouse', ''),
                getattr(product, 'platform', 'pinduoduo'),
                getattr(product, 'data_type', 'regular'),
                0  # isdel (默认为0，表示未删除)
            )
            all_data.append(data_tuple)
        
        # 批量插入数据
        if all_data:
            cursor.executemany('''
                INSERT INTO pdd_products (
                    goods_id, name, price, stock, order_number, shop_name, 
                    buyer_nickname, supplier, status, shipping_company, 
                    customer_quantity, customer_amount, buyer_message, 
                    seller_remark, placing_time, payment_time, shipping_time, 
                    distributor, shipping_warehouse, platform, data_type, isdel
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', all_data)
        
        conn.commit()
        conn.close()
        print(f"成功插入 {len(all_data)} 条拼多多数据到数据库")
    
    def clear_table(self, table_name: str):
        """清空指定表的数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f'DELETE FROM {table_name}')
        conn.commit()
        conn.close()
        print(f"已清空 {table_name} 表")
    
    def soft_delete_record(self, table_name: str, record_id: int):
        """软删除记录（设置isdel字段为1）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f'UPDATE {table_name} SET isdel = 1 WHERE id = ?', (record_id,))
        conn.commit()
        conn.close()
        print(f"已软删除 {table_name} 表中ID为 {record_id} 的记录")
    
    def get_records_by_type(self, table_name: str, data_type: str):
        """根据数据类型获取记录（排除已删除的记录）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM {table_name} WHERE data_type = ? AND isdel = 0', (data_type,))
        records = cursor.fetchall()
        conn.close()
        return records
    
    def get_all_active_records(self, table_name: str):
        """获取所有未删除的记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM {table_name} WHERE isdel = 0')
        records = cursor.fetchall()
        conn.close()
        return records


# 使用示例
if __name__ == "__main__":
    # 示例：如何使用
    db_manager = DataToDB()
#     
#     # 假设你有从爬虫获取的数据
#     # jushuitan_data = [...]  # 聚水潭API返回的数据列表
#     # db_manager.insert_jushuitan_data(jushuitan_data)
#     
#     # pdd_products = [...]  # 拼多多商品数据
#     # db_manager.insert_pdd_data(pdd_products)