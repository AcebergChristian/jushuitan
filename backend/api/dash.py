from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from ..models.database import User as UserModel, Goods, JushuitanProduct
from .auth import get_current_user
from datetime import datetime, timedelta
from peewee import fn

router = APIRouter()

@router.get("/dashboard/stats")
def get_dashboard_stats(current_user = Depends(get_current_user)):
    """
    获取仪表盘统计数据
    包括用户数、商品数、店铺数、销售额等
    """
    try:
        # 统计用户数（排除已删除的用户）
        total_users = UserModel.select().where(UserModel.is_del == 0).count()
        
        # 统计商品数（未删除的商品）
        total_goods = Goods.select().where(Goods.is_del == False).count()
        
        # 统计店铺数（从商品表中获取不重复的店铺）
        distinct_stores = Goods.select(Goods.store_id).where(Goods.is_del == False).distinct()
        total_stores = distinct_stores.count()
        
        # 统计销售额（使用sales_amount字段）
        total_sales_amount = Goods.select(
            fn.SUM(Goods.sales_amount)
        ).where(Goods.is_del == False).scalar() or 0.0
        
        # 统计今日销售额
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        today_sales = Goods.select(
            fn.SUM(Goods.sales_amount)
        ).where(
            (Goods.is_del == False) &
            (Goods.created_at >= today_start) &
            (Goods.created_at <= today_end)
        ).scalar() or 0.0
        
        # 统计本周销售额
        week_start = today - timedelta(days=today.weekday())  # 本周一
        week_start_dt = datetime.combine(week_start, datetime.min.time())
        
        week_sales = Goods.select(
            fn.SUM(Goods.sales_amount)
        ).where(
            (Goods.is_del == False) &
            (Goods.created_at >= week_start_dt)
        ).scalar() or 0.0
        
        # 统计本月销售额
        month_start = today.replace(day=1)
        month_start_dt = datetime.combine(month_start, datetime.min.time())
        
        month_sales = Goods.select(
            fn.SUM(Goods.sales_amount)
        ).where(
            (Goods.is_del == False) &
            (Goods.created_at >= month_start_dt)
        ).scalar() or 0.0
        
        # 统计商品类型数（使用商品名称去重）
        total_good_types = Goods.select(Goods.goods_name).where(Goods.is_del == False).distinct().count()
        
        # 统计活跃用户数（最近30天内有活动的用户，这里简化为最近登录的用户）
        # 由于没有登录时间字段，暂时返回总用户数
        active_users = total_users
        
        # 统计订单数（从聚水潭产品表中获取）
        total_orders = JushuitanProduct.select().where(JushuitanProduct.is_del == 0).count()
        
        # 计算平均客单价
        avg_order_value = 0.0
        if total_orders > 0 and total_sales_amount > 0:
            avg_order_value = total_sales_amount / total_orders
        
        # 返回统计数据
        return {
            "status": "success",
            "data": {
                "total_users": total_users,
                "total_goods": total_goods,
                "total_stores": total_stores,
                "total_sales_amount": round(float(total_sales_amount), 2),
                "today_sales": round(float(today_sales), 2),
                "week_sales": round(float(week_sales), 2),
                "month_sales": round(float(month_sales), 2),
                "total_good_types": total_good_types,
                "active_users": active_users,
                "total_orders": total_orders,
                "avg_order_value": round(avg_order_value, 2),
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取仪表盘统计数据失败: {str(e)}")


@router.get("/dashboard/chart-data")
def get_dashboard_chart_data(current_user = Depends(get_current_user)):
    """
    获取仪表盘图表数据（最近7天的销售趋势）
    """
    try:
        # 获取最近7天的销售数据
        chart_data = []
        today = datetime.now().date()
        
        for i in range(6, -1, -1):  # 从7天前到今天
            target_date = today - timedelta(days=i)
            start_of_day = datetime.combine(target_date, datetime.min.time())
            end_of_day = datetime.combine(target_date, datetime.max.time())
            
            # 获取当天的销售额
            day_sales = Goods.select(
                fn.SUM(Goods.sales_amount)
            ).where(
                (Goods.is_del == False) &
                (Goods.created_at >= start_of_day) &
                (Goods.created_at <= end_of_day)
            ).scalar() or 0.0
            
            # 获取当天的订单数
            day_orders = JushuitanProduct.select().where(
                (JushuitanProduct.is_del == 0) &
                (JushuitanProduct.created_at >= start_of_day) &
                (JushuitanProduct.created_at <= end_of_day)
            ).count()
            
            chart_data.append({
                "date": target_date.strftime("%m-%d"),
                "sales": round(float(day_sales), 2),
                "orders": day_orders,
                "day_of_week": target_date.strftime("%a")
            })
        
        return {
            "status": "success",
            "data": chart_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取图表数据失败: {str(e)}")


@router.get("/dashboard/recent-activities")
def get_recent_activities(current_user = Depends(get_current_user)):
    """
    获取最近活动数据
    """
    try:
        # 获取最近的商品更新记录
        recent_goods = Goods.select().where(
            Goods.is_del == False
        ).order_by(Goods.updated_at.desc()).limit(4)
        
        activities = []
        for good in recent_goods:
            activities.append({
                "user": getattr(good, 'creator', 'System'),
                "action": f"更新了商品 \"{good.goods_name}\"",
                "time": good.updated_at.strftime("%m-%d %H:%M") if good.updated_at else "未知时间",
                "avatar_color": "blue"  # 默认颜色
            })
        
        # 如果商品不足4个，补充一些虚拟数据
        while len(activities) < 4:
            activities.append({
                "user": "系统",
                "action": "执行了数据同步任务",
                "time": "刚刚",
                "avatar_color": "green"
            })
        
        return {
            "status": "success",
            "data": activities[:4]  # 确保最多返回4条
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取最近活动失败: {str(e)}")