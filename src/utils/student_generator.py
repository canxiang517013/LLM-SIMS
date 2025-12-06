"""
自动学生信息生成器（增强版）
用于批量生成真实的、学号唯一且结构合理的测试数据
"""
import random
import string
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, asdict

# 可选：使用 pypinyin 生成更真实的拼音邮箱（推荐）
try:
    from pypinyin import lazy_pinyin
    USE_PINYIN = True
except ImportError:
    USE_PINYIN = False
    import unicodedata


@dataclass
class Student:
    """学生信息数据类"""
    student_id: str
    name: str
    class_name: str
    college: str
    major: str
    grade: str
    gender: str
    phone: str
    email: str
    address: str

    def __repr__(self) -> str:
        return f"<Student {self.student_id} {self.name}>"


class StudentGenerator:
    """学生信息生成器（支持全局唯一学号）"""

    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
        
        # 姓氏和名字
        self.surnames = [
            '王', '李', '张', '刘', '陈', '杨', '赵', '黄', '周', '吴',
            '徐', '孙', '胡', '朱', '高', '林', '何', '郭', '马', '罗',
            '梁', '宋', '郑', '谢', '韩', '唐', '冯', '于', '董', '萧',
            '程', '曹', '袁', '邓', '许', '傅', '沈', '曾', '彭', '吕'
        ]
        
        self.given_names = [
            '伟', '芳', '娜', '秀英', '敏', '静', '丽', '强', '磊', '军',
            '洋', '勇', '艳', '杰', '娟', '涛', '明', '超', '秀兰', '霞',
            '平', '刚', '桂英', '玉兰', '萍', '鹏', '华', '红', '金', '国',
            '春', '梅', '兰', '琳', '宇', '浩', '博', '瑞', '鑫', '健'
        ]
        
        # 学院与专业映射
        self.colleges = {
            '计算机学院': ['计算机科学与技术', '软件工程', '数据科学与大数据技术', '人工智能', '网络工程'],
            '数学学院': ['数学与应用数学', '信息与计算科学', '统计学', '应用统计学'],
            '物理学院': ['物理学', '应用物理学', '光电信息科学与工程', '核物理'],
            '化学学院': ['化学', '应用化学', '材料化学', '化学生物学'],
            '生物学院': ['生物科学', '生物技术', '生态学', '生物信息学'],
            '外国语学院': ['英语', '日语', '法语', '德语', '西班牙语'],
            '机械工程学院': ['机械工程', '机械设计制造及其自动化', '车辆工程', '工业设计'],
            '电子信息学院': ['电子信息工程', '通信工程', '电子科学与技术', '微电子科学与工程'],
            '经济管理学院': ['经济学', '国际经济与贸易', '工商管理', '市场营销', '会计学']
        }

        # === 新增：学院与专业编码（确保唯一性和可读性）===
        self.college_codes = {
            '计算机学院': '01',
            '数学学院': '02',
            '物理学院': '03',
            '化学学院': '04',
            '生物学院': '05',
            '外国语学院': '06',
            '机械工程学院': '07',
            '电子信息学院': '08',
            '经济管理学院': '09'
        }

        # 专业代码只需在学院内唯一
        self.major_codes = {
            # 计算机学院
            '计算机科学与技术': '01',
            '软件工程': '02',
            '数据科学与大数据技术': '03',
            '人工智能': '04',
            '网络工程': '05',
            # 数学学院
            '数学与应用数学': '01',
            '信息与计算科学': '02',
            '统计学': '03',
            '应用统计学': '04',
            # 物理学院
            '物理学': '01',
            '应用物理学': '02',
            '光电信息科学与工程': '03',
            '核物理': '04',
            # 化学学院
            '化学': '01',
            '应用化学': '02',
            '材料化学': '03',
            '化学生物学': '04',
            # 生物学院
            '生物科学': '01',
            '生物技术': '02',
            '生态学': '03',
            '生物信息学': '04',
            # 外国语学院
            '英语': '01',
            '日语': '02',
            '法语': '03',
            '德语': '04',
            '西班牙语': '05',
            # 机械工程学院
            '机械工程': '01',
            '机械设计制造及其自动化': '02',
            '车辆工程': '03',
            '工业设计': '04',
            # 电子信息学院
            '电子信息工程': '01',
            '通信工程': '02',
            '电子科学与技术': '03',
            '微电子科学与工程': '04',
            # 经济管理学院
            '经济学': '01',
            '国际经济与贸易': '02',
            '工商管理': '03',
            '市场营销': '04',
            '会计学': '05'
        }

        # 城市区划
        self.cities = [
            '北京市海淀区', '上海市浦东新区', '广州市天河区', '深圳市南山区',
            '杭州市西湖区', '南京市鼓楼区', '成都市武侯区', '武汉市洪山区',
            '西安市雁塔区', '天津市南开区', '重庆市渝北区', '苏州市工业园区',
            '青岛市市南区', '大连市中山区', '厦门市思明区', '合肥市蜀山区',
            '济南市历下区', '长沙市岳麓区', '郑州市金水区', '沈阳市和平区'
        ] * 2

        # 手机号前缀
        self.phone_prefixes = [
            '130', '131', '132', '133', '134', '135', '136', '137', '138', '139',
            '145', '147', '149',
            '150', '151', '152', '153', '155', '156', '157', '158', '159',
            '166', '167',
            '170', '171', '172', '173', '174', '175', '176', '177', '178',
            '180', '181', '182', '183', '184', '185', '186', '187', '188', '189',
            '190', '191', '192', '193', '195', '196', '197', '198', '199'
        ]

        self.email_domains = ['qq.com', '163.com', '126.com', 'gmail.com', 'outlook.com', 'stu.edu.cn']

        # === 全局序列号计数器（关键：保证学号唯一）===
        # key: f"{grade}_{college}_{major}" -> 当前序列号
        self._sequence_counters = {}

    def _generate_student_id(self, grade: str, college: str, major: str) -> str:
        """生成唯一学号：年份(4) + 学院码(2) + 专业码(2) + 序列号(4)"""
        college_code = self.college_codes.get(college, '99')
        major_code = self.major_codes.get(major, '99')
        
        key = f"{grade}_{college}_{major}"
        
        # 自动递增序列号
        if key not in self._sequence_counters:
            self._sequence_counters[key] = 1
        else:
            self._sequence_counters[key] += 1
        
        seq = self._sequence_counters[key]
        return f"{grade}{college_code}{major_code}{seq:04d}"

    def generate_name(self) -> str:
        surname = random.choice(self.surnames)
        if random.random() < 0.5:
            given = random.choice(self.given_names)
        else:
            given = random.choice(self.given_names) + random.choice(self.given_names)
        return surname + given

    def generate_gender(self) -> str:
        return random.choice(['男', '女'])

    def generate_college_and_major(self) -> Tuple[str, str]:
        college = random.choice(list(self.colleges.keys()))
        major = random.choice(self.colleges[college])
        return college, major

    def generate_grade(self) -> str:
        current_year = 2025
        return str(random.randint(current_year - 3, current_year))

    def generate_class_name(self, major: str, grade: str) -> str:
        abbrev_map = {
            '计算机科学与技术': '计科',
            '软件工程': '软工',
            '数据科学与大数据技术': '数据',
            '人工智能': '智能',
            '网络工程': '网工',
            '数学与应用数学': '数学',
            '信息与计算科学': '信计',
            '统计学': '统计',
            '应用统计学': '应统',
            '物理学': '物理',
            '应用物理学': '应物',
            '光电信息科学与工程': '光电',
            '核物理': '核物',
            '化学': '化学',
            '应用化学': '应化',
            '材料化学': '材化',
            '化学生物学': '化生',
            '生物科学': '生科',
            '生物技术': '生技',
            '生态学': '生态',
            '生物信息学': '生信',
            '英语': '英语',
            '日语': '日语',
            '法语': '法语',
            '德语': '德语',
            '西班牙语': '西语',
            '机械工程': '机械',
            '机械设计制造及其自动化': '机制',
            '车辆工程': '车辆',
            '工业设计': '工设',
            '电子信息工程': '电子',
            '通信工程': '通信',
            '电子科学与技术': '电科',
            '微电子科学与工程': '微电',
            '经济学': '经济',
            '国际经济与贸易': '国贸',
            '工商管理': '工商',
            '市场营销': '营销',
            '会计学': '会计'
        }
        major_short = abbrev_map.get(major, major[:2] if len(major) >= 2 else major)
        class_num = random.randint(1, 5)
        return f"{major_short}{grade[-2:]}{class_num}班"

    def generate_phone(self) -> str:
        prefix = random.choice(self.phone_prefixes)
        suffix = ''.join(random.choices(string.digits, k=8))
        return f"{prefix}{suffix}"

    def _name_to_pinyin(self, name: str) -> str:
        if USE_PINYIN:
            pinyin_list = lazy_pinyin(name, errors='ignore')
            return ''.join(pinyin_list).lower()
        else:
            return f"{name}{random.randint(10, 99)}"

    def generate_email(self, name: str, student_id: str) -> str:
        domain = random.choice(self.email_domains)
        if random.random() < 0.7:
            username = self._name_to_pinyin(name)
            username = username[:16] if len(username) > 16 else username
            username += str(random.randint(10, 99))
        else:
            username = f"stu{student_id}"
        return f"{username}@{domain}"

    def generate_address(self) -> str:
        return random.choice(self.cities)

    def generate_single_student(self, grade: str) -> Student:
        """生成单个学生（学号自动唯一）"""
        name = self.generate_name()
        gender = self.generate_gender()
        college, major = self.generate_college_and_major()
        student_id = self._generate_student_id(grade, college, major)
        class_name = self.generate_class_name(major, grade)
        phone = self.generate_phone()
        email = self.generate_email(name, student_id)
        address = self.generate_address()
        return Student(
            student_id=student_id,
            name=name,
            class_name=class_name,
            college=college,
            major=major,
            grade=grade,
            gender=gender,
            phone=phone,
            email=email,
            address=address
        )

    def generate_multiple_students(self, count: int) -> List[Dict[str, Any]]:
        """简单随机生成多个学生（学号全局唯一）"""
        students = []
        for _ in range(count):
            grade = self.generate_grade()
            student = self.generate_single_student(grade)
            students.append(asdict(student))
        return students

    def generate_balanced_students(self, total_count: int = 100) -> List[Dict[str, Any]]:
        """生成分布均衡的学生数据（学号仍唯一）"""
        grades = [str(y) for y in range(2022, 2026)]  # 2022-2025级
        students_per_grade = total_count // len(grades)
        remainder = total_count % len(grades)

        students = []
        for i, grade in enumerate(grades):
            num = students_per_grade + (1 if i < remainder else 0)
            for _ in range(num):
                s = self.generate_single_student(grade)
                students.append(asdict(s))
        return students

    def get_statistics_summary(self, students: List[Dict[str, Any]]) -> Dict[str, Any]:
        """获取统计摘要"""
        if not students:
            return {}

        def _count(field: str) -> Dict[str, int]:
            d = {}
            for s in students:
                val = s[field]
                d[val] = d.get(val, 0) + 1
            return d

        return {
            'total_students': len(students),
            'by_grade': _count('grade'),
            'by_college': _count('college'),
            'by_gender': _count('gender'),
            'by_major': _count('major')
        }


# 全局实例（固定种子便于测试）
student_generator = StudentGenerator(seed=42)


if __name__ == "__main__":
    print("=== 增强版学生信息生成器测试（唯一学号）===")
    
    # 第一次生成
    students1 = student_generator.generate_balanced_students(5)
    
    # 第二次生成（模拟分批插入）
    students2 = student_generator.generate_balanced_students(5)
    
    all_students = students1 + students2
    all_ids = [s['student_id'] for s in all_students]
    
    print(f"\n总共生成学生数: {len(all_students)}")
    print(f"学号是否全部唯一: {len(all_ids) == len(set(all_ids))}")
    
    print("\n示例学号与信息:")
    for s in all_students[:8]:
        print(f"{s['student_id']} | {s['name']} | {s['college']} - {s['major']} | {s['grade']}")
    
    stats = student_generator.get_statistics_summary(all_students)
    print(f"\n统计摘要:")
    for key, value in stats.items():
        print(f"{key}: {value}")