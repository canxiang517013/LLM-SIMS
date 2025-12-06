"""
大语言模型客户端
"""
import json
import numpy as np
import openai
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import pandas as pd
import requests

load_dotenv()

class LLMClient:
    """大语言模型客户端类"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.base_url = os.getenv('OPENAI_BASE_URL', 'https://api.deepseek.com/v1').strip()
        self.model = os.getenv('LLM_MODEL', 'deepseek-chat').strip()
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY 环境变量未设置")
        
        # 配置OpenAI客户端
        openai.api_key = self.api_key
        openai.base_url = self.base_url
        
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def chat_completion(self, messages: List[Dict[str, str]], 
                       temperature: float = 0.7,
                       max_tokens: Optional[int] = None) -> Optional[str]:
        """
        聊天补全
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            temperature: 温度参数，控制输出的随机性
            max_tokens: 最大token数
            
        Returns:
            模型回复内容
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM调用错误: {e}")
            return None
    
    def simple_chat(self, user_message: str, 
                   system_prompt: Optional[str] = None,
                   temperature: float = 0.7) -> Optional[str]:
        """
        简单对话
        
        Args:
            user_message: 用户消息
            system_prompt: 系统提示词
            temperature: 温度参数
            
        Returns:
            模型回复
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": user_message})
        
        return self.chat_completion(messages, temperature)
    
    def is_student_management_query(self, query: str) -> bool:
        """
        判断是否为学生管理相关查询
        
        Args:
            query: 用户查询
            
        Returns:
            是否为学生管理相关
        """
        system_prompt = """
        你是一个学生管理系统的查询分类器。请判断用户的查询是否与学生信息管理相关。
        相关的查询包括：增删改查学生信息、统计分析学生数据、查看学生列表等。
        
        请只回答 "是" 或 "否"。
        """
        
        response = self.simple_chat(query, system_prompt, temperature=0.1)
        return response and "是" in response
    
    def extract_student_info(self, text: str) -> Dict[str, Any]:
        """
        从文本中提取学生信息
        
        Args:
            text: 包含学生信息的文本
            
        Returns:
            提取的学生信息字典
        """
        system_prompt = """
        请从以下文本中提取学生信息，并按JSON格式返回。
        包含的字段：student_id(学号), name(姓名), class_name(班级), 
        college(学院), major(专业), grade(年级), gender(性别), phone(手机号), 
        email(邮箱), address(地址)。
        
        如果某个字段信息不存在，请设为null。
        只返回JSON格式的数据，不要包含其他文字。
        """
        
        response = self.simple_chat(text, system_prompt, temperature=0.1)
        
        if response:
            try:
                import json
                return json.loads(response)
            except json.JSONDecodeError:
                print(f"JSON解析错误: {response}")
        
        return {}
    
    def generate_natural_response(self, operation: str, result: Any) -> str:
        """
        生成自然语言响应
        
        Args:
            operation: 操作类型
            result: 操作结果
            
        Returns:
            自然语言响应
        """
        system_prompt = """
        你是一个友好的学生管理助手。请根据操作结果，生成自然、友好的中文回复。
        回复要简洁明了，符合中文表达习惯。
        """
        
        user_message = f"操作：{operation}\n结果：{result}\n请生成回复："
        
        response = self.simple_chat(user_message, system_prompt, temperature=0.7)
        return response or "操作完成。"


    def suggest_chart(self, query: str, data: List[Dict]) -> Dict[str, str]:
        """
        基于自然语言查询和数据样本，推荐图表类型和标题
        """
        if not data:
            return {"chart_type": "bar", "title": "无数据", "reason": "数据为空"}
        
        try:
            import pandas as pd
            import numpy as np
            df = pd.DataFrame(data)
            num_rows = len(df)
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
            
            data_summary = f"""
            - 数据行数: {num_rows}
            - 数值列: {numeric_cols}
            - 分类列: {categorical_cols}
            """
            
            prompt = f"""
        你是一个数据可视化专家。请根据用户的查询和返回的数据特征，推荐最适合的图表类型。

        用户查询: "{query}"
        数据特征: {data_summary}

        支持的图表类型（必须选择其一）：
        bar, pie, line, scatter, histogram, box, heatmap, violin, sunburst, treemap, area, funnel

        请严格按以下JSON格式返回，不要包含其他内容：
        {{
            "chart_type": "推荐的图表类型",
            "title": "推荐的中文图表标题",
            "reason": "推荐理由（1句话）"
        }}
            """.strip()

            # === 关键：捕获 API 调用异常 ===
            try:
                response_text = self.chat_completion(
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3
                )
                if response_text is None:
                    raise RuntimeError("LLM 返回为空")
            except Exception as api_error:
                return {
                    "chart_type": "auto",
                    "title": "数据可视化",
                    "reason": f"LLM 服务调用失败: {str(api_error)[:100]}"
                }
            
            # 解析响应
            import json
            try:
                result = json.loads(response_text)
            except (json.JSONDecodeError, TypeError) as parse_error:
                return {
                    "chart_type": "auto",
                    "title": "数据可视化",
                    "reason": f"LLM 返回格式错误: {str(parse_error)[:100]}"
                }

            # 验证 chart_type
            valid_types = ["bar", "pie", "line", "scatter", "histogram", "box", 
                        "heatmap", "violin", "sunburst", "treemap", "area", "funnel"]
            if result.get("chart_type") not in valid_types:
                result["chart_type"] = "auto"
            
            # 确保必要字段存在
            return {
                "chart_type": result.get("chart_type", "auto"),
                "title": result.get("title", "数据可视化"),
                "reason": result.get("reason", "基于 LLM 推荐")
            }

        except Exception as e:
            # 捕获所有内部异常（如 pandas 处理失败等）
            return {
                "chart_type": "auto",
                "title": "数据可视化",
                "reason": f"图表推荐内部错误: {str(e)[:100]}"
            }

        
# 全局LLM客户端实例
llm_client = LLMClient()
