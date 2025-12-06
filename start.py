"""
项目启动脚本
"""
import os
import sys
import subprocess
import time
import threading
import webbrowser
from pathlib import Path
from dotenv import load_dotenv

# 强制设置标准输出使用 UTF-8 编码
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

# 加载 .env 文件
load_dotenv()
class ProjectStarter:
    """项目启动器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.api_process = None
        self.frontend_process = None
        self.running = True
    
    def print_banner(self):
        """打印项目横幅"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                学生信息管理助手                              ║
║         基于大语言模型的智能学生信息管理系统                  ║
╠══════════════════════════════════════════════════════════════╣
║ 功能特性：                                                   ║
║ • 自然语言对话交互                                           ║
║ • 学生信息增删改查                                           ║
║ • 智能Text2SQL转换                                          ║
║ • 数据可视化分析                                             ║
║ • 模块化系统设计                                             ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def check_environment(self):
        """检查环境配置"""
        print("🔍 检查环境配置...")
        
        # 检查Python版本
        if sys.version_info < (3, 8):
            print("❌ 错误: 需要Python 3.8或更高版本")
            return False
        
        # 检查环境变量
        required_env_vars = ['OPENAI_API_KEY', 'DB_HOST', 'DB_USER', 'DB_PASSWORD']
        missing_vars = []
        
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ 错误: 缺少环境变量: {', '.join(missing_vars)}")
            print("请检查.env文件配置")
            return False
        
        # 检查依赖包
        try:
            import streamlit
            import fastapi
            import mysql.connector
            import openai
            import plotly
            print("✅ 依赖包检查通过")
        except ImportError as e:
            print(f"❌ 错误: 缺少依赖包: {e}")
            print("请运行: pip install -r requirements.txt")
            return False
        
        print("✅ 环境配置检查通过")
        return True
    
    def install_dependencies(self):
        """安装依赖包"""
        print("📦 安装依赖包...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ])
            print("✅ 依赖包安装完成")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 依赖包安装失败: {e}")
            return False
    
    def initialize_database(self):
        """初始化数据库"""
        print("🗄️ 初始化数据库...")
        
        try:
            result = subprocess.run(
                [sys.executable, "init_database.py"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                encoding='utf-8',      # 👈 关键：强制用 UTF-8 解码
                errors='replace'       # 👈 容错：遇到非法字节用  替代，避免崩溃
            )
            
            if result.returncode == 0:
                print("✅ 数据库初始化完成")
                return True
            else:
                print(f"❌ 数据库初始化失败:\n{result.stderr}")
                return False
        except Exception as e:
            print(f"❌ 数据库初始化异常: {e}")
            return False
    
    def start_api_server(self):
        """启动API服务器"""
        print("🚀 启动后端API服务...")
        
        try:
            self.api_process = subprocess.Popen([
                sys.executable, "src/api/main.py"
            ], cwd=self.project_root)
            
            # 等待API服务启动
            time.sleep(3)
            
            if self.api_process.poll() is None:
                print("✅ 后端API服务启动成功 (http://localhost:8000)")
                return True
            else:
                print("❌ 后端API服务启动失败")
                return False
        
        except Exception as e:
            print(f"❌ 启动API服务异常: {e}")
            return False
    
    def start_frontend(self):
        """启动前端界面"""
        print("🎨 启动前端界面...")
        
        try:
            self.frontend_process = subprocess.Popen([
                sys.executable, "-m", "streamlit", "run", "frontend/app.py",
                "--server.port=8501", "--server.address=localhost"
            ], cwd=self.project_root)
            
            # 等待前端启动
            time.sleep(5)
            
            if self.frontend_process.poll() is None:
                print("✅ 前端界面启动成功 (http://localhost:8501)")
                return True
            else:
                print("❌ 前端界面启动失败")
                return False
        
        except Exception as e:
            print(f"❌ 启动前端界面异常: {e}")
            return False
    
    def open_browser(self):
        """打开浏览器"""
        try:
            time.sleep(2)
            webbrowser.open("http://localhost:8501")
            print("🌐 已在浏览器中打开应用界面")
        except Exception as e:
            print(f"⚠️ 无法自动打开浏览器: {e}")
            print("请手动访问: http://localhost:8501")
    
    def show_menu(self):
        """显示菜单"""
        print("\n" + "="*60)
        print("🎓 学生信息管理助手 - 控制面板")
        print("="*60)
        print("1. 🚀 完整启动系统")
        print("2. 📦 仅安装依赖")
        print("3. 🗄️ 仅初始化数据库")
        print("4. 🔧 仅启动后端API")
        print("5. 🎨 仅启动前端")
        print("6. 🌐 打开浏览器")
        print("7. 🛑 停止所有服务")
        print("8. ❌ 退出")
        print("="*60)
    
    def stop_services(self):
        """停止所有服务"""
        print("🛑 停止服务...")
        
        if self.api_process:
            try:
                self.api_process.terminate()
                self.api_process.wait(timeout=5)
                print("✅ 后端API服务已停止")
            except Exception as e:
                print(f"⚠️ 停止API服务失败: {e}")
        
        if self.frontend_process:
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
                print("✅ 前端服务已停止")
            except Exception as e:
                print(f"⚠️ 停止前端服务失败: {e}")
        
        self.api_process = None
        self.frontend_process = None
    
    def full_start(self):
        """完整启动"""
        if not self.check_environment():
            return False
        
        if not self.initialize_database():
            return False
        
        if not self.start_api_server():
            return False
        
        if not self.start_frontend():
            return False
        
        # 在新线程中打开浏览器
        threading.Thread(target=self.open_browser, daemon=True).start()
        
        return True
    
    def run(self):
        """运行启动器"""
        self.print_banner()
        
        while self.running:
            try:
                self.show_menu()
                choice = input("\n请选择操作 (1-8): ").strip()
                
                if choice == "1":
                    print("\n🚀 开始完整启动...")
                    if self.full_start():
                        print("\n🎉 系统启动成功！")
                        print("📍 访问地址: http://localhost:8501")
                        print("📍 API文档: http://localhost:8000/docs")
                        input("\n按Enter键返回菜单...")
                    else:
                        input("\n启动失败，按Enter键返回菜单...")
                
                elif choice == "2":
                    self.install_dependencies()
                    input("\n按Enter键返回菜单...")
                
                elif choice == "3":
                    self.initialize_database()
                    input("\n按Enter键返回菜单...")
                
                elif choice == "4":
                    self.start_api_server()
                    input("\n按Enter键返回菜单...")
                
                elif choice == "5":
                    self.start_frontend()
                    input("\n按Enter键返回菜单...")
                
                elif choice == "6":
                    self.open_browser()
                    input("\n按Enter键返回菜单...")
                
                elif choice == "7":
                    self.stop_services()
                    input("\n按Enter键返回菜单...")
                
                elif choice == "8":
                    print("\n👋 感谢使用学生信息管理助手！")
                    self.stop_services()
                    self.running = False
                
                else:
                    print("\n⚠️ 无效选择，请输入1-8")
                    input("按Enter键继续...")
            
            except KeyboardInterrupt:
                print("\n\n🛑 检测到中断信号，正在停止服务...")
                self.stop_services()
                self.running = False
            
            except Exception as e:
                print(f"\n❌ 发生错误: {e}")
                input("按Enter键继续...")

def main():
    """主函数"""
    # 切换到项目根目录
    os.chdir(Path(__file__).parent)
    
    # 创建启动器
    starter = ProjectStarter()
    
    # 运行启动器
    starter.run()

if __name__ == "__main__":
    main()
