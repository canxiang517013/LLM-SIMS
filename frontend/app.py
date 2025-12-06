"""
学生信息管理助手 - Streamlit前端界面（优化版）
"""
import streamlit as st
import requests
import pandas as pd
from typing import Dict, Any, List, Optional
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# 配置页面
st.set_page_config(
    page_title="学生信息管理助手",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API配置
API_BASE_URL = "http://localhost:8000"


class StudentManagementApp:
    """学生管理应用主类"""
    
    def __init__(self):
        self.api_base_url = API_BASE_URL
        self.init_session_state()
    
    def init_session_state(self):
        """初始化会话状态"""
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'current_data' not in st.session_state:
            st.session_state.current_data = []
        if 'current_stats' not in st.session_state:
            st.session_state.current_stats = {}
        if 'last_query' not in st.session_state:
            st.session_state.last_query = ""
        if 'current_sql' not in st.session_state:
            st.session_state.current_sql = ""
        if 'current_chart' not in st.session_state:
            st.session_state.current_chart = None
            
    def api_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """发送API请求"""
        url = f"{self.api_base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url)
            elif method == "POST":
                response = requests.post(url, json=data)
            elif method == "PUT":
                response = requests.put(url, json=data)
            elif method == "DELETE":
                response = requests.delete(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"API请求失败: {response.status_code}")
                return {"success": False}
        
        except requests.exceptions.RequestException as e:
            st.error(f"连接错误: {str(e)}")
            return {"success": False}
    
    def render_sidebar(self):
        """渲染侧边栏"""
        with st.sidebar:
            st.title("🎓 学生管理助手")
            st.markdown("---")
            
            # 功能选择（移除了“数据查询”）
            page = st.selectbox(
                "选择功能",
                ["智能查询", "学生管理", "设置"],
                index=0
            )
            
            # 快速统计
            if st.button("🔄 刷新数据"):
                self.refresh_data()
            
            if st.session_state.current_stats:
                st.markdown("### 📊 快速统计")
                stats = st.session_state.current_stats
                st.metric("总学生数", stats.get('total_students', 0))
                st.metric("学院数", len(stats.get('by_college', {})))
                st.metric("年级数", len(stats.get('by_grade', {})))
        
        return page
    
    def _generate_chart(self, chart_data: dict):
        """统一封装图表生成请求"""
        try:
            response = requests.post(
                f"{self.api_base_url}/charts",
                json=chart_data,
                timeout=15
            )
            if response.status_code == 200:
                st.session_state.current_chart = response.text
            else:
                st.error(f"图表生成失败: HTTP {response.status_code}")
        except Exception as e:
            st.error(f"图表生成错误: {str(e)}")
            
    def render_intelligent_query(self):
        """渲染统一智能查询界面"""
        st.header("🤖 智能查询系统")
        
        st.markdown("""
        **使用自然语言查询学生信息** - 支持各种复杂查询和统计分析
        """)
        
        # 查询输入区域
        query = st.text_area(
            "输入查询语句",
            placeholder="例如：\n• 查询计算机学院2021级的学生\n• 统计各年级的男女比例\n• 查询姓张的学生信息\n• 统计每个学院的学生数量\n• 查询2022级的女生",
            height=100,
            value=st.session_state.last_query,
            key="main_query_input"
        )

        # 按钮区域
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            execute_button = st.button("🔍 执行查询", type="primary")
        
        with col2:
            clear_button = st.button("🗑️ 清空结果")
        
        with col3:
            auto_chart_button = st.button("🤖 智能图表", disabled=not st.session_state.current_data)
        
        # 清空结果
        if clear_button:
            st.session_state.current_data = []
            st.session_state.current_sql = ""
            st.session_state.current_chart = None
            st.session_state.last_query = ""
            st.rerun()
        
        # 执行查询
        if execute_button and query.strip():
            st.session_state.last_query = query.strip()
            with st.spinner("正在分析查询并生成SQL..."):
                response = self.api_request("POST", "/query", {"query": query.strip()})
                
                if response.get("success"):
                    st.success(f"✅ 查询成功！找到 {response.get('count', 0)} 条记录")
                    st.session_state.current_data = response.get("data", [])
                    st.session_state.current_sql = response.get("sql", "")
                else:
                    st.error(f"❌ 查询失败: {response.get('message', '未知错误')}")
        
        # 显示查询结果
        if st.session_state.current_data:
            st.subheader("📋 查询结果")
            df = pd.DataFrame(st.session_state.current_data)
            st.dataframe(df, use_container_width=True)
            
            if st.session_state.current_sql:
                with st.expander("🔧 生成的SQL语句"):
                    st.code(st.session_state.current_sql, language="sql")
        
        # 智能图表生成
        if auto_chart_button and st.session_state.current_data and st.session_state.last_query:
            with st.spinner("🧠 AI 正在分析数据并推荐最佳图表..."):
                try:
                    suggest_resp = requests.post(
                        f"{self.api_base_url}/charts/suggest",
                        json={
                            "query": st.session_state.last_query,
                            "data": st.session_state.current_data
                        },
                        timeout=10
                    )
                    if suggest_resp.status_code == 200:
                        suggestion = suggest_resp.json()
                        if suggestion.get("success"):
                            st.info(f"📈 AI 推荐: {suggestion['reason']}")
                            chart_data = {
                                "data": st.session_state.current_data,
                                "chart_type": suggestion["chart_type"],
                                "title": suggestion["title"]
                            }
                            self._generate_chart(chart_data)
                        else:
                            st.warning("AI 推荐失败，使用默认图表")
                            self._generate_chart({
                                "data": st.session_state.current_data,
                                "chart_type": "auto",
                                "title": "数据可视化"
                            })
                    else:
                        st.error("AI 图表推荐服务不可用")
                except Exception as e:
                    st.error(f"AI 推荐请求失败: {str(e)}")
        
        # 显示图表
        if st.session_state.current_chart:
            st.subheader("📊 数据可视化")
            st.components.v1.html(st.session_state.current_chart, height=500)
        
        # 查询历史
        if len(st.session_state.messages) > 0:
            st.subheader("📝 查询历史")
            recent_messages = st.session_state.messages[-5:]
            for i, message in enumerate(recent_messages):
                if message["role"] == "user":
                    with st.expander(f"👤 用户: {message['content'][:50]}..."):
                        st.write(message["content"])
                        if i < len(recent_messages) - 1 and recent_messages[i+1]["role"] == "assistant":
                            assistant_msg = recent_messages[i+1]
                            st.write("**🤖 AI回复:**")
                            st.write(assistant_msg.get("content", ""))
                            if assistant_msg.get("sql"):
                                st.write("**生成的SQL:**")
                                st.code(assistant_msg["sql"], language="sql")
        
        # 使用说明
        with st.expander("💡 使用说明"):
            st.markdown("""
            ### 支持的查询类型：
            
            **🔍 基础查询:**
            - 查询所有学生
            - 查询计算机学院的学生
            - 查询2021级的学生
            - 查询姓张的学生
            
            **📊 统计分析:**
            - 统计各学院学生数量
            - 统计各年级的男女比例
            - 按专业统计学生分布
            - 统计每个班级的人数
            
            **🎯 复杂条件:**
            - 查询计算机学院2021级的女生
            - 查询手机号是138开头的男生
            - 查询2022-2023级的学生
            - 查询地址包含北京的学生
            
            **📝 数据管理:**
            - 添加学生：张三，学号2021001，计算机学院...
            - 删除学号为2021001的学生
            - 更新张三的手机号为13800138000
            
            ### 特殊功能：
            - 🎯 **智能图表**：AI 自动推荐最佳图表类型
            - 💾 查询历史：保存最近的查询记录
            - 🔍 SQL查看：可查看生成的SQL语句
            - 📊 多种图表：支持柱状图、饼图、折线图等
            """)

    def render_student_management(self):
        """渲染学生管理界面"""
        st.header("👥 学生管理")
        
        # 添加学生表单
        with st.expander("➕ 添加新学生"):
            with st.form("add_student_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    student_id = st.text_input("学号 *", key="new_student_id")
                    name = st.text_input("姓名 *", key="new_name")
                    class_name = st.text_input("班级 *", key="new_class")
                    college = st.text_input("学院 *", key="new_college")
                
                with col2:
                    major = st.text_input("专业 *", key="new_major")
                    grade = st.text_input("年级 *", key="new_grade")
                    gender = st.selectbox("性别 *", ["男", "女"], key="new_gender")
                    phone = st.text_input("手机号", key="new_phone")
                
                email = st.text_input("邮箱", key="new_email")
                address = st.text_area("地址", key="new_address")
                
                submitted = st.form_submit_button("添加学生")
                
                if submitted:
                    required = [student_id, name, class_name, college, major, grade, gender]
                    if all(required):
                        student_data = {
                            "student_id": student_id,
                            "name": name,
                            "class_name": class_name,
                            "college": college,
                            "major": major,
                            "grade": grade,
                            "gender": gender,
                            "phone": phone,
                            "email": email,
                            "address": address
                        }
                        response = self.api_request("POST", "/students", student_data)
                        if response.get("success"):
                            st.success("✅ 学生添加成功！")
                            self.refresh_data()
                        else:
                            st.error("❌ 添加失败，请检查信息。")
                    else:
                        st.error("❌ 请填写所有必填字段。")
        
        # 学生列表
        st.subheader("📋 学生列表")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            search_term = st.text_input("搜索学生", placeholder="输入姓名或学号...")
        with col2:
            limit = st.selectbox("显示数量", [10, 20, 50, 100], index=0)
        
        if st.button("🔄 刷新列表"):
            self.refresh_data()
        
        students = []
        if search_term:
            response = self.api_request("POST", "/query", {"query": f"查询姓名或学号包含{search_term}的学生"})
            if response.get("success") and response.get("data"):
                students = response["data"]
        else:
            students = st.session_state.current_data[:limit] if st.session_state.current_data else []
        
        if students:
            df = pd.DataFrame(students)
            display_columns = ['student_id', 'name', 'class_name', 'college', 'major', 'grade', 'gender', 'phone']
            if all(col in df.columns for col in display_columns):
                df_display = df[display_columns].copy()
                df_display.columns = ['学号', '姓名', '班级', '学院', '专业', '年级', '性别', '手机号']
                st.dataframe(df_display, use_container_width=True)
            else:
                st.dataframe(df, use_container_width=True)
            
            # 操作按钮
            selected = st.selectbox(
                "选择学生进行操作",
                options=[f"{s.get('student_id', '')} - {s.get('name', '')}" for s in students],
                index=None,
                key="student_selector"
            )
            
            if selected:
                student_id = selected.split(" - ")[0]
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.button("📝 编辑", disabled=True, help="编辑功能开发中")  # 占位
                with col2:
                    if st.button("🗑️ 删除", key=f"del_{student_id}"):
                        resp = self.api_request("DELETE", f"/students/{student_id}")
                        if resp.get("success"):
                            st.success("删除成功！")
                            self.refresh_data()
                        else:
                            st.error("删除失败。")
                with col3:
                    if st.button("ℹ️ 详情", key=f"detail_{student_id}"):
                        resp = self.api_request("GET", f"/students/{student_id}")
                        if resp.get("success") and resp.get("data"):
                            st.json(resp["data"])
            
            # 可视化按钮
            if st.button("📊 可视化当前列表"):
                self._generate_chart({
                    "data": students,
                    "chart_type": "auto",
                    "title": "学生列表可视化"
                })
        else:
            st.info("未找到学生信息。")
        
        # 显示图表（如果存在）
        if st.session_state.current_chart:
            st.subheader("📊 当前数据可视化")
            st.components.v1.html(st.session_state.current_chart, height=500)

    def render_settings(self):
        """渲染设置界面"""
        st.header("⚙️ 设置")
        
        st.subheader("API配置")
        st.info(f"当前API地址: {self.api_base_url}")
        
        st.subheader("会话管理")
        
        if st.button("🗑️ 清空聊天记录"):
            st.session_state.messages = []
            st.success("聊天记录已清空")
        
        if st.button("🔄 重置所有数据"):
            if st.session_state.get("confirm_reset"):
                st.session_state.messages = []
                st.session_state.current_data = []
                st.session_state.current_stats = {}
                st.session_state.last_query = ""
                st.session_state.current_chart = None
                st.session_state.confirm_reset = False
                st.success("✅ 所有数据已重置")
            else:
                st.session_state.confirm_reset = True
                st.warning("⚠️ 再次点击确认重置所有数据")
        
        st.subheader("关于")
        st.markdown("""
        **学生信息管理助手 v1.0**
        
        基于大语言模型的智能学生信息管理系统，支持：
        - 自然语言对话交互
        - 学生信息增删改查
        - 智能SQL生成
        - 数据可视化分析
        
        **技术栈：**
        - 后端：FastAPI + MySQL
        - 前端：Streamlit
        - AI模型：DeepSeek API
        - 图表：Plotly
        """)
    
    def refresh_data(self):
        """刷新数据"""
        resp1 = self.api_request("GET", "/students?limit=100")
        if resp1.get("success"):
            st.session_state.current_data = resp1["data"]
        
        resp2 = self.api_request("GET", "/statistics")
        if resp2.get("success"):
            st.session_state.current_stats = resp2["data"]
    
    def run(self):
        """运行应用"""
        page = self.render_sidebar()
        if page == "智能查询":
            self.render_intelligent_query()
        elif page == "学生管理":
            self.render_student_management()
        elif page == "设置":
            self.render_settings()


# 运行应用
if __name__ == "__main__":
    app = StudentManagementApp()
    app.run()