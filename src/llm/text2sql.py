"""
Text2SQL模块 - 将自然语言转换为SQL查询
"""
from typing import Dict, Any, List, Optional, Tuple
import re
import json
from .llm_client import llm_client
from ..database.models import student_model

class Text2SQL:
    """Text2SQL转换器"""
    
    def __init__(self):
        self.table_schema = self._get_table_schema()
        self.sample_queries = self._get_sample_queries()
    
    def _get_table_schema(self) -> str:
        """获取表结构信息"""
        return """
        学生信息表(students)结构：
        - student_id: 学号 (VARCHAR, 唯一)
        - name: 姓名 (VARCHAR)
        - class_name: 班级 (VARCHAR)
        - college: 学院 (VARCHAR)
        - major: 专业 (VARCHAR)
        - grade: 年级 (VARCHAR)
        - gender: 性别 (VARCHAR)
        - phone: 手机号 (VARCHAR)
        - email: 邮箱 (VARCHAR)
        - address: 地址 (TEXT)
        - created_at: 创建时间 (TIMESTAMP)
        - updated_at: 更新时间 (TIMESTAMP)
        """
    
    def _get_sample_queries(self) -> List[str]:
        """获取示例查询"""
        return [
            "SELECT * FROM students WHERE name = '张三'",
            "SELECT COUNT(*) FROM students WHERE college = '计算机学院'",
            "SELECT * FROM students WHERE grade = '2021' ORDER BY name",
            "SELECT college, COUNT(*) as count FROM students GROUP BY college",
            "DELETE FROM students WHERE student_id = '2021001'",
            "UPDATE students SET phone = '13800138000' WHERE student_id = '2021001'"
        ]
    
    def natural_language_to_sql(self, query: str) -> Tuple[str, str]:
        """
        将自然语言转换为SQL
        
        Args:
            query: 自然语言查询
            
        Returns:
            (sql查询, 操作类型)
        """
        # 首先判断操作类型
        operation_type = self._detect_operation_type(query)
        
        # 生成SQL
        sql = self._generate_sql(query, operation_type)
        
        return sql, operation_type
    
    def _detect_operation_type(self, query: str) -> str:
        """检测操作类型"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['添加', '新增', '插入', '创建', 'add', 'insert', 'create']):
            return 'INSERT'
        elif any(word in query_lower for word in ['删除', '移除', 'delete', 'remove']):
            return 'DELETE'
        elif any(word in query_lower for word in ['修改', '更新', '更改', 'update', 'modify', 'change']):
            return 'UPDATE'
        elif any(word in query_lower for word in ['统计', '汇总', '数量', 'count', 'sum', 'group by']):
            return 'AGGREGATE'
        else:
            return 'SELECT'
    
    def _generate_sql(self, query: str, operation_type: str) -> str:
        """生成SQL查询"""
        system_prompt = f"""
        你是一个SQL查询生成器。请根据用户的自然语言查询生成相应的SQL语句。
        
        表结构信息：
        {self.table_schema}
        
        操作类型：{operation_type}
        
        请注意：
        1. 只生成针对students表的SQL语句
        2. 字段名必须准确匹配表结构
        3. 字符串值要用单引号包围
        4. 确保SQL语法正确
        5. 只返回SQL语句，不要包含其他文字
        6. 对于模糊查询使用LIKE操作符
        7. 对于统计查询，适当使用GROUP BY和聚合函数
        
        示例查询：
        {chr(10).join(self.sample_queries)}
        """
        
        response = llm_client.simple_chat(query, system_prompt, temperature=0.1)
        
        if response:
            # 清理响应，提取SQL语句
            sql = self._extract_sql(response)
            if sql:
                return sql
        
        # 如果生成失败，返回默认查询
        return "SELECT * FROM students LIMIT 10"
    
    def _extract_sql(self, text: str) -> Optional[str]:
        """从文本中提取SQL语句"""
        # 查找SQL语句模式
        sql_patterns = [
            r'```sql\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```',
            r'(SELECT.*?)(?:\n|$)',
            r'(INSERT.*?)(?:\n|$)',
            r'(UPDATE.*?)(?:\n|$)',
            r'(DELETE.*?)(?:\n|$)'
        ]
        
        for pattern in sql_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                sql = match.group(1).strip()
                if self._validate_sql(sql):
                    return sql
        
        # 如果没有找到模式，尝试直接使用
        text = text.strip()
        if self._validate_sql(text):
            return text
        
        return None
    
    def _validate_sql(self, sql: str) -> bool:
        """简单的SQL验证"""
        sql_upper = sql.upper()
        
        # 检查是否包含必要的SQL关键词
        if not any(keyword in sql_upper for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE']):
            return False
        
        # 检查是否包含students表
        sql_lower = sql.lower()
        if 'students' not in sql_lower:
            return False
        
        # 检查危险操作
        dangerous_keywords = ['DROP', 'TRUNCATE', 'ALTER', 'CREATE']
        if any(keyword in sql_upper for keyword in dangerous_keywords):
            return False
        
        return True
    
    def execute_query(self, query: str) -> Dict[str, Any]:
        """
        执行自然语言查询
        
        Args:
            query: 自然语言查询
            
        Returns:
            执行结果
        """
        try:
            # 转换为SQL
            sql, operation_type = self.natural_language_to_sql(query)
            
            # 直接执行生成的SQL
            result = self._execute_raw_sql(sql, operation_type)
            
            # 添加SQL信息
            result['sql'] = sql
            result['operation'] = operation_type
            
            return result
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'查询执行失败: {str(e)}',
                'sql': query  # 返回原始查询用于调试
            }
    
    def _execute_raw_sql(self, sql: str, operation_type: str) -> Dict[str, Any]:
        """直接执行SQL语句"""
        import mysql.connector
        from ..database.connection import db_connection
        
        connection = None
        cursor = None
        
        try:
            # 使用原始连接方式
            connection = mysql.connector.connect(
                host=db_connection.host,
                user=db_connection.user,
                password=db_connection.password,
                database=db_connection.database,
                port=db_connection.port
            )
            cursor = connection.cursor(dictionary=True)
            
            # 执行SQL
            cursor.execute(sql)
            
            if operation_type in ['SELECT', 'AGGREGATE']:
                # 查询操作，返回数据
                result = cursor.fetchall()
                return {
                    'success': True,
                    'data': result,
                    'count': len(result)
                }
            elif operation_type == 'INSERT':
                # 插入操作
                connection.commit()
                insert_id = cursor.lastrowid
                return {
                    'success': True,
                    'insert_id': insert_id,
                    'message': f'成功添加学生，ID: {insert_id}'
                }
            elif operation_type == 'UPDATE':
                # 更新操作
                affected_rows = cursor.rowcount
                connection.commit()
                return {
                    'success': affected_rows > 0,
                    'message': f'更新成功，影响{affected_rows}行' if affected_rows > 0 else '更新失败，未找到匹配记录'
                }
            elif operation_type == 'DELETE':
                # 删除操作
                affected_rows = cursor.rowcount
                connection.commit()
                return {
                    'success': affected_rows > 0,
                    'message': f'删除成功，影响{affected_rows}行' if affected_rows > 0 else '删除失败，未找到匹配记录'
                }
        
        except Exception as e:
            if connection:
                connection.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
    
    def _parse_conditions(self, sql: str) -> Dict[str, Any]:
        """解析SQL条件"""
        conditions = {}
        
        # 简单的条件解析
        patterns = [
            (r"name\s*=\s*'([^']+)'", 'name'),
            (r"student_id\s*=\s*'([^']+)'", 'student_id'),
            (r"college\s*=\s*'([^']+)'", 'college'),
            (r"major\s*=\s*'([^']+)'", 'major'),
            (r"grade\s*=\s*'([^']+)'", 'grade'),
            (r"gender\s*=\s*'([^']+)'", 'gender'),
            (r"class_name\s*=\s*'([^']+)'", 'class_name'),
        ]
        
        for pattern, field in patterns:
            match = re.search(pattern, sql, re.IGNORECASE)
            if match:
                conditions[field] = match.group(1)
        
        return conditions
    
    def _parse_update_query(self, natural_query: str, sql: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """解析更新查询"""
        # 尝试从自然语言中提取学号
        student_id = None
        id_patterns = [
            r'学号[是为]?(\w+)',
            r'student_id[=\s]?(\w+)',
            r'(\d{4,10})'  # 假设学号是4-10位数字
        ]
        
        for pattern in id_patterns:
            match = re.search(pattern, natural_query)
            if match:
                student_id = match.group(1)
                break
        
        if not student_id:
            return None, None
        
        # 提取更新信息
        update_data = llm_client.extract_student_info(natural_query)
        update_data.pop('student_id', None)  # 移除学号字段
        
        return student_id, update_data if update_data else None
    
    def _parse_student_id(self, natural_query: str, sql: str) -> Optional[str]:
        """解析学号"""
        # 尝试从自然语言中提取学号
        id_patterns = [
            r'学号[是为]?(\w+)',
            r'student_id[=\s]?(\w+)',
            r'(\d{4,10})'
        ]
        
        for pattern in id_patterns:
            match = re.search(pattern, natural_query)
            if match:
                return match.group(1)
        
        # 尝试从SQL中提取
        match = re.search(r"student_id\s*=\s*'([^']+)'", sql, re.IGNORECASE)
        if match:
            return match.group(1)
        
        return None

# 全局Text2SQL实例
text2sql = Text2SQL()
