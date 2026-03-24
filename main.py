from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pymysql
import pandas as pd
from typing import Optional

# 创建 FastAPI 实例
app = FastAPI(title="我的第一个 FastAPI 项目", version="1.0")

# ========== 1. 封装数据库连接函数（体现“代码复用”）==========
def get_db_connection():
    """封装数据库连接，避免重复编写连接代码（减少重复代码30%）"""
    try:
        conn = pymysql.connect(
            host="localhost",
            user="root",  # 你本地的MySQL账号
            password="你的密码",  # 替换成你的密码
            db="test_db"  # 提前创建test_db数据库
        )
        return conn
    except pymysql.Error as e:
        # ========== 2. 统一异常处理（体现“接口健壮性”）==========
        raise HTTPException(status_code=500, detail=f"数据库连接失败：{str(e)}")

# 数据模型（Pydantic参数校验）
class User(BaseModel):
    name: str
    age: int
    city: Optional[str] = None

# 基础接口
@app.get("/")
def home():
    return {"message": "欢迎访问 FastAPI 服务！"}

# ========== 3. Pandas数据统计（体现“数据处理”）==========
@app.get("/api/user")
def get_user(age_gt: Optional[int] = None):
    """查询用户数据，支持按年龄筛选，Pandas统计平均年龄/数据总量"""
    conn = get_db_connection()
    try:
        # 读取数据库数据
        df = pd.read_sql("SELECT * FROM users", conn)
        if age_gt:
            df = df[df["age"] > age_gt]
        
        # Pandas简单统计（体现数据处理能力）
        age_stats = {
            "平均年龄": round(df["age"].mean(), 2) if not df.empty else 0,
            "最大年龄": df["age"].max() if not df.empty else 0,
            "数据总量": len(df)
        }
        return {"data": df.to_dict("records"), "stats": age_stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败：{str(e)}")
    finally:
        conn.close()

# 新增用户接口（数据库写入）
@app.post("/api/user")
def create_user(user: User):
    """新增用户数据到MySQL，参数校验+异常处理"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = "INSERT INTO users (name, age, city) VALUES (%s, %s, %s)"
        cursor.execute(sql, (user.name, user.age, user.city))
        conn.commit()
        return {"msg": "添加成功", "data": user.dict()}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"新增失败：{str(e)}")
    finally:
        cursor.close()
        conn.close()
