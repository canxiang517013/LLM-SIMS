# 学生信息管理助手(LLM-SIMS)

基于大语言模型的智能学生信息管理系统，支持自然语言对话交互、学生信息管理、智能SQL生成和数据可视化分析。

## 🎯 项目概述

本项目为实现《深度学习项目实践》而构建的一个完整的学生信息管理解决方案，结合了大语言模型技术，实现了自然语言交互的智能管理功能。

### 核心功能

- **🤖 智能对话交互**: 支持自然语言查询和操作
- **👥 学生信息管理**: 完整的增删改查功能
- **🔄 Text2SQL转换**: 自然语言到SQL的智能转换
- **📊 数据可视化**: 多种图表类型支持，智能图表推荐
- **🏗️ 模块化设计**: 前后端分离，易于扩展
- **🚀 一键启动**: 智能启动脚本，简化部署流程

## 🏗️ 技术架构

### 后端技术栈
- **FastAPI**: 高性能Web框架
- **MySQL**: 关系型数据库
- **OpenAI/DeepSeek API**: 大语言模型服务
- **SQLAlchemy**: ORM框架

### 前端技术栈
- **Streamlit**: 快速构建Web应用
- **Plotly**: 交互式数据可视化
- **Pandas**: 数据处理分析

### AI技术栈
- **Text2SQL**: 自然语言到SQL转换
- **信息抽取**: 结构化数据提取
- **智能对话**: 上下文理解与回复

## 📁 项目结构

```
deepstudy/
├── .env                    # 环境配置文件
├── .env.example           # 环境配置模板
├── requirements.txt       # Python依赖包
├── init_database.py      # 数据库初始化脚本
├── start.py             # 项目启动脚本
├── README.md            # 项目说明文档
├── src/                 # 源代码目录
│   ├── api/            # API服务
│   │   └── main.py     # FastAPI主文件
│   ├── database/       # 数据库模块
│   │   ├── connection.py  # 数据库连接
│   │   └── models.py     # 数据模型
│   ├── llm/           # 大语言模型模块
│   │   ├── llm_client.py  # LLM客户端
│   │   └── text2sql.py   # Text2SQL转换
│   ├── utils/         # 工具模块
│   └── visualization/ # 可视化模块
│       └── chart_generator.py  # 图表生成器
└── frontend/          # 前端代码
    └── app.py        # Streamlit应用
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- MySQL 5.7+
- 8GB+ RAM

### 安装步骤

1. **克隆项目**
```bash
git clone <https://github.com/canxiang517013/LLM-ISIMS.git>
cd deepstudy
```

2. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，填入实际配置
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **初始化数据库**
```bash
python init_database.py
```

5. **启动服务**

方式一：使用启动脚本（推荐）
```bash
python start.py
# 选择选项 1: 完整启动系统
```

方式二：手动启动
```bash
# 启动后端API
python src/api/main.py

# 启动前端界面
python -m streamlit run frontend/app.py --server.port=8501
```

### 访问应用

- **前端界面**: http://localhost:8501
- **API文档**: http://localhost:8000/docs
- **API健康检查**: http://localhost:8000/health

## ⚙️ 配置说明

### 环境变量配置

在 `.env` 文件中配置以下变量：

```env
# 大语言模型API配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-3.5-turbo

# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_db_username
DB_PASSWORD=your_db_password
DB_NAME=student_management

# 应用配置
APP_TITLE=学生信息管理助手
APP_HOST=0.0.0.0
APP_PORT=8501
```

**注意**：
- 支持多种LLM服务，推荐使用DeepSeek API获得更好的中文支持
- 如使用DeepSeek，请将`OPENAI_BASE_URL`设置为`https://api.deepseek.com/v1`，`LLM_MODEL`设置为`deepseek-chat`
- API端口默认为8000，前端端口为8501，请确保端口未被占用

### 数据库配置

确保MySQL服务正在运行，并且：
- 创建数据库（或使用初始化脚本自动创建）
- 配置正确的用户权限
- 支持UTF-8字符集

## 📖 使用指南

### 智能对话

在"智能对话"页面，您可以使用自然语言进行查询：

```
查询计算机学院2021级的学生
统计各学院学生数量
查找姓名为张三的学生信息
```

### 学生管理

在"学生管理"页面，您可以：
- 添加新学生信息
- 查看学生列表
- 编辑学生信息
- 删除学生记录

### 数据查询

在"数据查询"页面，支持：
- 自然语言查询
- SQL查询结果展示
- 数据可视化图表生成

### 统计分析

在"统计分析"页面，提供：
- 学生总览统计
- 学院分布图表
- 年级分布分析
- 性别比例统计

## 🔧 API接口

### 主要端点

#### 学生管理接口
- `GET /students` - 获取学生列表
- `POST /students` - 添加学生
- `GET /students/{student_id}` - 根据学号获取学生信息
- `PUT /students/{student_id}` - 更新学生信息
- `DELETE /students/{student_id}` - 删除学生

#### 智能交互接口
- `POST /chat` - 智能对话接口
- `POST /query` - 执行自然语言查询
- `POST /extract_student_info` - 从文本中提取学生信息

#### 数据可视化接口
- `POST /charts` - 生成图表（HTML）
- `GET /charts/statistics` - 生成学生统计图表
- `POST /charts/suggest` - 智能图表类型推荐
- `GET /chart_types` - 获取支持的图表类型

#### 系统接口
- `GET /` - 根路径
- `GET /health` - 健康检查
- `GET /statistics` - 获取学生统计信息

详细API文档请访问: http://localhost:8000/docs

## 🎨 功能特性

### Text2SQL转换

支持多种查询类型的自然语言转换：
- **查询类**: "查询计算机学院的学生"
- **统计类**: "统计各年级学生数量"
- **条件类**: "查找2021级的男生"
- **排序类**: "按姓名排序显示学生"

### 数据可视化

支持多种图表类型：
- 柱状图 (Bar Chart)
- 饼图 (Pie Chart)
- 折线图 (Line Chart)
- 散点图 (Scatter Plot)
- 直方图 (Histogram)
- 箱线图 (Box Plot)
- 热力图 (Heatmap)
- 小提琴图 (Violin Plot)
- 旭日图 (Sunburst)
- 树状图 (Treemap)

### 智能特性

- **上下文理解**: 保持对话上下文
- **意图识别**: 自动识别用户意图
- **错误处理**: 友好的错误提示
- **数据验证**: 输入数据验证

## 🛠️ 开发指南

### 添加新功能

1. **后端扩展**
   - 在 `src/api/main.py` 中添加新的API端点
   - 在 `src/database/models.py` 中添加数据模型
   - 在 `src/llm/` 中扩展AI功能

2. **前端扩展**
   - 在 `frontend/app.py` 中添加新的页面组件
   - 使用Streamlit组件构建用户界面

3. **数据库扩展**
   - 修改 `init_database.py` 添加新表
   - 更新数据模型和API接口

### 代码规范

- 使用Python 3.8+语法特性
- 遵循PEP 8代码规范
- 添加详细的文档字符串
- 使用类型提示 (Type Hints)

### 测试

```bash
# 运行后端测试
python -m pytest tests/

# 运行前端测试
streamlit run frontend/app.py --server.headless=true
```

## 🐛 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查MySQL服务是否启动
   - 验证数据库配置信息
   - 确认用户权限设置

2. **API调用失败**
   - 检查网络连接
   - 验证API密钥配置
   - 查看错误日志

3. **前端无法访问**
   - 检查端口占用情况
   - 确认后端服务正常运行
   - 检查防火墙设置

### 日志查看

```bash
# 查看API服务日志
python src/api/main.py

# 查看前端日志
streamlit run frontend/app.py --logger.level=debug
```

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

感谢以下开源项目和服务：
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的Web框架
- [Streamlit](https://streamlit.io/) - 快速构建数据应用
- [Plotly](https://plotly.com/) - 交互式可视化库
- [OpenAI](https://openai.com/) - 大语言模型API
- [MySQL](https://www.mysql.com/) - 关系型数据库

---

**学生信息管理助手** - 让学生管理更智能、更高效！ 🎓
