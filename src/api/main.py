"""
后端API服务主文件
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import pandas as pd
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import os
import sys
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

load_dotenv()

from src.database.models import student_model
from src.llm.llm_client import llm_client
from src.llm.text2sql import text2sql
from src.visualization.chart_generator import chart_generator
from src.utils.student_generator import student_generator

# ===== Lifespan 管理器 =====
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理：启动时初始化数据库，关闭时清理资源（如有）"""
    try:
        # 启动时：初始化学生信息表
        student_model.create_table()
        print("数据库初始化完成")
    except Exception as e:
        print(f"数据库初始化失败: {e}")
    
    # 应用运行中（处理请求）
    yield
    
    # 关闭时：可在此处添加资源清理逻辑（如关闭连接池等）
    # 例如：await some_db.close()
    print("API 服务正在关闭...")


# 创建 FastAPI 应用（使用 lifespan）
app = FastAPI(
    title="学生信息管理助手API",
    description="基于大语言模型的学生信息管理助手后端服务",
    version="1.0.0",
    lifespan=lifespan
)

# 配置 CORS（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === 请求模型 ===
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class StudentRequest(BaseModel):
    student_id: str
    name: str
    class_name: str
    college: str
    major: str
    grade: str
    gender: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

class StudentUpdateRequest(BaseModel):
    student_id: str
    update_data: Dict[str, Any]

class QueryRequest(BaseModel):
    query: str

class ChartRequest(BaseModel):
    data: List[Dict[str, Any]]
    chart_type: str = "auto"
    title: str = "数据可视化"

# 全局会话存储（简单内存存储，生产环境建议用 Redis）
chat_sessions: Dict[str, List[Dict[str, str]]] = {}

# === 路由 ===
@app.get("/")
async def root():
    """根路径"""
    return {"message": "学生信息管理助手API服务运行中"}

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "学生信息管理助手"}

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    智能对话接口
    """
    try:
        session_id = request.session_id or "default"
        if session_id not in chat_sessions:
            chat_sessions[session_id] = []
        
        if llm_client.is_student_management_query(request.message):
            result = text2sql.execute_query(request.message)
            if result['success']:
                if result['operation'] in ['SELECT', 'AGGREGATE']:
                    response_text = llm_client.generate_natural_response(
                        f"查询：{request.message}", 
                        f"找到{result['count']}条记录"
                    )
                    return {
                        "type": "query_result",
                        "response": response_text,
                        "data": result['data'],
                        "sql": result['sql'],
                        "count": result['count'],
                        "session_id": session_id
                    }
                else:
                    return {
                        "type": "operation_result",
                        "response": result['message'],
                        "sql": result['sql'],
                        "session_id": session_id
                    }
            else:
                return {
                    "type": "error",
                    "response": result['message'],
                    "session_id": session_id
                }
        else:
            response = llm_client.simple_chat(request.message)
            return {
                "type": "chat",
                "response": response or "抱歉，我现在无法回应。",
                "session_id": session_id
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def execute_query(request: QueryRequest):
    """执行自然语言查询"""
    try:
        result = text2sql.execute_query(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/students")
async def create_student(request: StudentRequest):
    """添加学生信息"""
    try:
        student_data = request.model_dump()
        insert_id = student_model.insert(student_data)
        if insert_id:
            return {
                "success": True,
                "message": "学生信息添加成功",
                "student_id": insert_id
            }
        else:
            raise HTTPException(status_code=400, detail="添加学生信息失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/students")
async def get_students(limit: Optional[int] = None):
    """获取学生列表"""
    try:
        students = student_model.select_all(limit)
        return {
            "success": True,
            "data": students,
            "count": len(students)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/students/{student_id}")
async def get_student(student_id: str):
    """根据学号获取学生信息"""
    try:
        student = student_model.select_by_id(student_id)
        if student:
            return {
                "success": True,
                "data": student
            }
        else:
            raise HTTPException(status_code=404, detail="学生信息未找到")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/students/{student_id}")
async def update_student(student_id: str, request: StudentUpdateRequest):
    """更新学生信息"""
    try:
        success = student_model.update(student_id, request.update_data)
        if success:
            return {
                "success": True,
                "message": "学生信息更新成功"
            }
        else:
            raise HTTPException(status_code=400, detail="更新学生信息失败")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/students/{student_id}")
async def delete_student(student_id: str):
    """删除学生信息"""
    try:
        success = student_model.delete(student_id)
        if success:
            return {
                "success": True,
                "message": "学生信息删除成功"
            }
        else:
            raise HTTPException(status_code=400, detail="删除学生信息失败")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/statistics")
async def get_statistics():
    """获取学生统计信息"""
    try:
        stats = student_model.get_statistics()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/charts")
async def generate_chart(request: ChartRequest):
    """生成图表（HTML）"""
    try:
        chart_html = chart_generator.generate_chart_from_data(
            request.data,
            request.chart_type,
            request.title
        )
        return HTMLResponse(content=chart_html)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/charts/statistics")
async def generate_statistics_charts():
    """生成学生统计图表"""
    try:
        stats = student_model.get_statistics()
        charts = chart_generator.generate_student_statistics_charts(stats)
        return {
            "success": True,
            "charts": charts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract_student_info")
async def extract_student_info(request: dict):
    """从文本中提取学生信息"""
    try:
        text = request.get("text", "")
        student_info = llm_client.extract_student_info(text)
        return {
            "success": True,
            "data": student_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chart_types")
async def get_chart_types():
    """获取支持的图表类型"""
    return {
        "chart_types": [
            {"value": "auto", "label": "自动选择"},
            {"value": "bar", "label": "柱状图"},
            {"value": "pie", "label": "饼图"},
            {"value": "line", "label": "折线图"},
            {"value": "scatter", "label": "散点图"},
            {"value": "histogram", "label": "直方图"},
            {"value": "box", "label": "箱线图"},
            {"value": "heatmap", "label": "热力图"},
            {"value": "violin", "label": "小提琴图"},
            {"value": "sunburst", "label": "旭日图"},
            {"value": "treemap", "label": "树状图"}
        ]
    }

class ChartSuggestionRequest(BaseModel):
    query: str
    data: List[Dict[str, Any]]

@app.post("/charts/suggest")
async def suggest_chart(request: ChartSuggestionRequest):
    """
    使用 LLM 分析查询语义，推荐最佳图表类型
    """
    print("=== 调试: 请求数据 ===")
    print("Query:", request.query)
    print("Data sample:", request.data[:2] if request.data else "Empty")
    print("Data keys:", list(request.data[0].keys()) if request.data else "N/A")
    try:     
        # 调用 LLM 客户端进行推荐（需实现 llm_client.suggest_chart）
        suggestion = llm_client.suggest_chart(
            query=request.query,
            data=request.data
        )
        
        return {
            "success": True,
            "chart_type": suggestion.get("chart_type", "auto"),
            "title": suggestion.get("title", "数据可视化"),
            "reason": suggestion.get("reason", "基于数据特征自动推荐")
        }
    except Exception as e:
        # 如果 LLM 不可用，回退到规则引擎
        try:
            from src.visualization.chart_generator import chart_generator
            df = pd.DataFrame(request.data)
            chart_type = chart_generator._suggest_chart_type(df, request.query)
            
            # 自动生成标题
            title = "数据可视化"
            if "分布" in request.query or "统计" in request.query:
                if "学院" in request.query:
                    title = "各学院学生分布"
                elif "年级" in request.query:
                    title = "年级分布"
                elif "性别" in request.query:
                    title = "性别分布"
            
            return {
                "success": True,
                "chart_type": chart_type,
                "title": title,
                "reason": "基于数据特征规则推荐（LLM 不可用）"
            }
        except Exception as fallback_e:
            return {
                "success": False,
                "error": str(fallback_e)
            }
    

# === 启动入口 ===
if __name__ == "__main__":
    import uvicorn

    host = os.getenv("APP_HOST", "localhost")
    port = int(os.getenv("APP_PORT", 8000))  # 默认 8000，避免与 Streamlit(8501) 冲突

    print(f"启动API服务：http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)
