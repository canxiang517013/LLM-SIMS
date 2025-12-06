"""
学生数据模型
"""
from typing import Dict, Any, List, Optional
from .connection import db_connection

class Student:
    """学生模型类"""
    
    def __init__(self):
        self.table_name = "students"
    
    def create_table(self) -> bool:
        """创建学生表"""
        sql = """
        CREATE TABLE IF NOT EXISTS students (
            id INT AUTO_INCREMENT PRIMARY KEY,
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
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生信息表'
        """
        return db_connection.execute_update(sql)
    
    def insert(self, student_data: Dict[str, Any]) -> Optional[int]:
        """插入学生记录"""
        sql = """
        INSERT INTO students (student_id, name, class_name, college, major, grade, gender, phone, email, address)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            student_data.get('student_id'),
            student_data.get('name'),
            student_data.get('class_name'),
            student_data.get('college'),
            student_data.get('major'),
            student_data.get('grade'),
            student_data.get('gender'),
            student_data.get('phone'),
            student_data.get('email'),
            student_data.get('address')
        )
        return db_connection.execute_insert(sql, params)
    
    def update(self, student_id: str, update_data: Dict[str, Any]) -> bool:
        """更新学生记录"""
        set_clauses = []
        params = []
        
        for field, value in update_data.items():
            if field != 'student_id' and value is not None:
                set_clauses.append(f"{field} = %s")
                params.append(value)
        
        if not set_clauses:
            return False
        
        sql = f"UPDATE {self.table_name} SET {', '.join(set_clauses)} WHERE student_id = %s"
        params.append(student_id)
        
        return db_connection.execute_update(sql, tuple(params))
    
    def delete(self, student_id: str) -> bool:
        """删除学生记录"""
        sql = f"DELETE FROM {self.table_name} WHERE student_id = %s"
        return db_connection.execute_update(sql, (student_id,))
    
    def select_by_id(self, student_id: str) -> Optional[Dict[str, Any]]:
        """根据学号查询学生"""
        sql = f"SELECT * FROM {self.table_name} WHERE student_id = %s"
        result = db_connection.execute_query(sql, (student_id,))
        return result[0] if result else None
    
    def select_all(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """查询所有学生"""
        sql = f"SELECT * FROM {self.table_name} ORDER BY created_at DESC"
        if limit:
            sql += f" LIMIT {limit}"
        return db_connection.execute_query(sql)
    
    def select_by_conditions(self, conditions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """根据条件查询学生"""
        where_clauses = []
        params = []
        
        for field, value in conditions.items():
            if value is not None:
                if isinstance(value, str) and '%' in value:
                    where_clauses.append(f"{field} LIKE %s")
                else:
                    where_clauses.append(f"{field} = %s")
                params.append(value)
        
        if not where_clauses:
            return self.select_all()
        
        sql = f"SELECT * FROM {self.table_name} WHERE {' AND '.join(where_clauses)} ORDER BY created_at DESC"
        return db_connection.execute_query(sql, tuple(params))
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取学生统计信息"""
        stats = {}
        
        # 总人数
        sql = "SELECT COUNT(*) as total FROM students"
        result = db_connection.execute_query(sql)
        stats['total_students'] = result[0]['total'] if result else 0
        
        # 按学院统计
        sql = "SELECT college, COUNT(*) as count FROM students GROUP BY college"
        result = db_connection.execute_query(sql)
        stats['by_college'] = {item['college']: item['count'] for item in result}
        
        # 按年级统计
        sql = "SELECT grade, COUNT(*) as count FROM students GROUP BY grade"
        result = db_connection.execute_query(sql)
        stats['by_grade'] = {item['grade']: item['count'] for item in result}
        
        # 按性别统计
        sql = "SELECT gender, COUNT(*) as count FROM students GROUP BY gender"
        result = db_connection.execute_query(sql)
        stats['by_gender'] = {item['gender']: item['count'] for item in result}
        
        return stats

# 学生模型实例
student_model = Student()
