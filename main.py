from fastapi import FastAPI
from pydantic import BaseModel

# 创建 FastAPI 实例
app = FastAPI(title="我的第一个 FastAPI 项目", version="1.0")

# 测试接口
@app.get("/")
def home():
    return {"message": "欢迎访问 FastAPI 服务！"}

# 获取用户信息接口
@app.get("/api/user")
def get_user():
    return {
        "username": "python_student",
        "age": 24,
        "skill": "FastAPI + Pandas + MySQL"
    }

# 模拟接收数据
class Item(BaseModel):
    name: str
    price: float

@app.post("/api/item")
def create_item(item: Item):
    return {
        "msg": "数据添加成功",
        "data": item.dict()
    }