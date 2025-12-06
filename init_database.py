"""
数据库初始化脚本
"""
import sys
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
# 强制设置标准输出使用 UTF-8 编码
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

# 加载环境变量
load_dotenv()

class DatabaseInitializer:
    """数据库初始化器"""
    
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', 3306))
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        self.database = os.getenv('DB_NAME', 'student_management')
        self.connection = None
    
    def connect_without_database(self):
        """连接MySQL服务器（不指定数据库）"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                charset='utf8mb4'
            )
            return True
        except Error as e:
            print(f"连接MySQL服务器失败: {e}")
            return False
    
    def connect_with_database(self):
        """连接指定数据库"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4'
            )
            return True
        except Error as e:
            print(f"连接数据库失败: {e}")
            return False
    
    def create_database(self):
        """创建数据库"""
        try:
            cursor = self.connection.cursor()
            
            # 创建数据库
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"数据库 '{self.database}' 创建成功或已存在")
            
            cursor.close()
            return True
        except Error as e:
            print(f"创建数据库失败: {e}")
            return False
    
    def create_students_table(self):
        """创建学生表"""
        try:
            cursor = self.connection.cursor()
            
            # 删除已存在的表（可选）
            cursor.execute("DROP TABLE IF EXISTS students")
            
            # 创建学生表
            create_table_sql = """
            CREATE TABLE students (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
                student_id VARCHAR(20) UNIQUE NOT NULL COMMENT '学号',
                name VARCHAR(50) NOT NULL COMMENT '姓名',
                class_name VARCHAR(50) NOT NULL COMMENT '班级',
                college VARCHAR(100) NOT NULL COMMENT '学院',
                major VARCHAR(100) NOT NULL COMMENT '专业',
                grade VARCHAR(10) NOT NULL COMMENT '年级',
                gender VARCHAR(10) NOT NULL COMMENT '性别',
                phone VARCHAR(20) COMMENT '手机号',
                email VARCHAR(100) COMMENT '邮箱',
                address TEXT COMMENT '地址',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                
                INDEX idx_student_id (student_id),
                INDEX idx_name (name),
                INDEX idx_college (college),
                INDEX idx_grade (grade),
                INDEX idx_gender (gender),
                INDEX idx_class_name (class_name),
                INDEX idx_major (major)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学生信息表'
            """
            
            cursor.execute(create_table_sql)
            print("学生表创建成功")
            
            cursor.close()
            return True
        except Error as e:
            print(f"创建学生表失败: {e}")
            return False
    
    def insert_sample_data(self):
        """使用 student_generator 动态插入示例数据"""
        try:
            # 导入生成器（确保路径正确）
            from src.utils.student_generator import student_generator
            
            # 生成 30000 条均衡分布的示例学生数据
            sample_students = student_generator.generate_balanced_students(30000)
            
            if not sample_students:
                print("未能生成示例数据")
                return False

            cursor = self.connection.cursor()
            
            # 准备插入 SQL
            insert_sql = """
            INSERT INTO students (student_id, name, class_name, college, major, grade, gender, phone, email, address)
            VALUES (%(student_id)s, %(name)s, %(class_name)s, %(college)s, %(major)s, %(grade)s, %(gender)s, %(phone)s, %(email)s, %(address)s)
            """
            
            # 批量插入（使用字典参数，更安全清晰）
            cursor.executemany(insert_sql, sample_students)
            self.connection.commit()
            
            print(f"成功插入 {cursor.rowcount} 条动态生成的示例数据")
            cursor.close()
            return True
            
        except ImportError as e:
            print(f"导入 student_generator 失败: {e}")
            return False
        except Exception as e:
            print(f"插入示例数据失败: {e}")
            self.connection.rollback()
            if 'cursor' in locals():
                cursor.close()
            return False
    
    def verify_data(self):
        """验证数据"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # 检查表结构
            cursor.execute("DESCRIBE students")
            columns = cursor.fetchall()
            print("\n学生表结构：")
            for column in columns:
                print(f"  {column['Field']}: {column['Type']} {'(NOT NULL)' if column['Null'] == 'NO' else ''} {'(UNIQUE)' if column['Key'] == 'UNI' else ''}")
            
            # 检查数据
            cursor.execute("SELECT COUNT(*) as total FROM students")
            total = cursor.fetchone()['total']
            print(f"\n总学生数: {total}")
            
            # 按学院统计
            cursor.execute("SELECT college, COUNT(*) as count FROM students GROUP BY college")
            college_stats = cursor.fetchall()
            print("\n学院分布：")
            for stat in college_stats:
                print(f"  {stat['college']}: {stat['count']}人")
            
            # 按年级统计
            cursor.execute("SELECT grade, COUNT(*) as count FROM students GROUP BY grade")
            grade_stats = cursor.fetchall()
            print("\n年级分布：")
            for stat in grade_stats:
                print(f"  {stat['grade']}: {stat['count']}人")
            
            # 按性别统计
            cursor.execute("SELECT gender, COUNT(*) as count FROM students GROUP BY gender")
            gender_stats = cursor.fetchall()
            print("\n性别分布：")
            for stat in gender_stats:
                print(f"  {stat['gender']}: {stat['count']}人")
            
            cursor.close()
            return True
        except Error as e:
            print(f"验证数据失败: {e}")
            return False
    
    def close_connection(self):
        """关闭数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("数据库连接已关闭")
    
    def initialize(self):
        """完整初始化流程"""
        print("开始初始化数据库...")
        
        # 步骤1: 连接MySQL服务器
        print("1. 连接MySQL服务器...")
        if not self.connect_without_database():
            return False
        
        # 步骤2: 创建数据库
        print("2. 创建数据库...")
        if not self.create_database():
            return False
        
        # 关闭连接
        self.close_connection()
        
        # 步骤3: 连接数据库
        print("3. 连接数据库...")
        if not self.connect_with_database():
            return False
        
        # 步骤4: 创建表
        print("4. 创建学生表...")
        if not self.create_students_table():
            return False
        
        # 步骤5: 插入示例数据
        print("5. 插入示例数据...")
        if not self.insert_sample_data():
            return False
        
        # 步骤6: 验证数据
        print("6. 验证数据...")
        if not self.verify_data():
            return False
        
        # 关闭连接
        self.close_connection()
        
        print("\n✅ 数据库初始化完成！")
        return True

def main():
    """主函数"""
    print("=" * 50)
    print("学生信息管理助手 - 数据库初始化")
    print("=" * 50)
    
    # 检查环境变量
    if not os.getenv('DB_HOST'):
        print("❌ 错误: 缺少DB_HOST环境变量")
        return
    
    if not os.getenv('DB_USER'):
        print("❌ 错误: 缺少DB_USER环境变量")
        return
    
    if not os.getenv('DB_PASSWORD'):
        print("❌ 错误: 缺少DB_PASSWORD环境变量")
        return
    
    # 创建初始化器
    initializer = DatabaseInitializer()
    
    try:
        # 执行初始化
        success = initializer.initialize()
        
        if success:
            print("\n🎉 数据库初始化成功！")
            print("\n下一步:")
            print("1. 启动后端API服务: python src/api/main.py")
            print("2. 启动前端界面: python frontend/app.py")
            print("3. 打开浏览器访问: http://localhost:8501")
        else:
            print("\n❌ 数据库初始化失败！")
            print("请检查数据库配置和连接信息。")
    
    except KeyboardInterrupt:
        print("\n\n⚠️ 初始化被用户中断")
    except Exception as e:
        print(f"\n❌ 初始化过程中发生错误: {e}")
    finally:
        initializer.close_connection()

if __name__ == "__main__":
    main()
