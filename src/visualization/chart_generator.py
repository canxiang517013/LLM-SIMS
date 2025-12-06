"""
增强版数据可视化图表生成模块
新增：面积图、雷达图、漏斗图、组合图、时间序列优化等
"""
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import re

# 设置中文字体（对 matplotlib 有效，Plotly 自动支持中文）
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class ChartGenerator:
    """增强版图表生成器类"""

    def __init__(self):
        self.color_palette = px.colors.qualitative.Set3 + px.colors.qualitative.Pastel
        self.chart_types = [
            'bar', 'pie', 'line', 'scatter', 'histogram',
            'box', 'heatmap', 'violin', 'sunburst', 'treemap',
            'area', 'funnel', 'radar', 'boxviolin', 'timeline'
        ]

    def generate_chart_from_data(self, data: List[Dict[str, Any]],
                                chart_type: str = 'auto',
                                title: str = "数据可视化") -> str:
        """
        从数据生成图表（返回 HTML 字符串）
        """
        if not data:
            return self._generate_empty_chart("无数据")

        df = pd.DataFrame(data)

        # 尝试解析 title 中的语义线索（如“分布”、“趋势”、“占比”）
        if chart_type == 'auto':
            chart_type = self._suggest_chart_type(df, title)

        # 调用内部方法生成 Plotly Figure
        fig = self._generate_figure(df, chart_type, title)
        if fig is None:
            return self._generate_empty_chart(f"不支持的图表类型: {chart_type}")

        return fig.to_html(include_plotlyjs='cdn')

    def generate_plotly_figure(self, data: List[Dict[str, Any]],
                              chart_type: str = 'auto',
                              title: str = "数据可视化") -> Optional[go.Figure]:
        """返回 Plotly Figure 对象（便于 Streamlit 直接使用）"""
        if not data:
            return self._create_empty_figure("无数据")
        df = pd.DataFrame(data)
        if chart_type == 'auto':
            chart_type = self._suggest_chart_type(df, title)
        return self._generate_figure(df, chart_type, title)

    def _suggest_chart_type(self, df: pd.DataFrame, query_or_title: str = "") -> str:
        """智能推荐图表类型（结合数据特征 + 语义线索）"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        text = query_or_title.lower()

        # 语义关键词匹配
        if any(word in text for word in ['占比', '比例', '构成', '分布']):
            return 'pie' if len(categorical_cols) >= 1 and (not numeric_cols or len(df) <= 10) else 'treemap'
        if any(word in text for word in ['趋势', '变化', '随时间', '增长']):
            return 'line'
        if any(word in text for word in ['对比', '比较']):
            return 'bar'
        if any(word in text for word in ['漏斗', '转化']):
            return 'funnel'
        if any(word in text for word in ['关系', '相关', '关联']):
            return 'heatmap' if len(numeric_cols) >= 2 else 'scatter'
        if any(word in text for word in ['层次', '层级', '结构']):
            return 'sunburst'

        # 数据特征回退逻辑
        if categorical_cols and numeric_cols:
            if len(categorical_cols) == 1 and len(numeric_cols) == 1 and len(df) <= 20:
                return 'bar'
            else:
                return 'scatter'

        elif categorical_cols:
            if len(df) <= 10 and max(len(df[col].unique()) for col in categorical_cols) <= 8:
                return 'pie'
            else:
                return 'bar'

        elif numeric_cols:
            if len(numeric_cols) == 1:
                return 'histogram'
            elif len(numeric_cols) == 2:
                return 'scatter'
            else:
                return 'heatmap'

        return 'bar'

    def _generate_figure(self, df: pd.DataFrame, chart_type: str, title: str) -> Optional[go.Figure]:
        """统一入口：根据类型生成 Figure"""
        try:
            if chart_type == 'bar':
                return self._create_bar_chart(df, title)
            elif chart_type == 'pie':
                return self._create_pie_chart(df, title)
            elif chart_type == 'line':
                return self._create_line_chart(df, title)
            elif chart_type == 'scatter':
                return self._create_scatter_chart(df, title)
            elif chart_type == 'histogram':
                return self._create_histogram(df, title)
            elif chart_type == 'box':
                return self._create_box_chart(df, title)
            elif chart_type == 'violin':
                return self._create_violin_chart(df, title)
            elif chart_type == 'heatmap':
                return self._create_heatmap(df, title)
            elif chart_type == 'sunburst':
                return self._create_sunburst_chart(df, title)
            elif chart_type == 'treemap':
                return self._create_treemap_chart(df, title)
            elif chart_type == 'area':
                return self._create_area_chart(df, title)
            elif chart_type == 'funnel':
                return self._create_funnel_chart(df, title)
            elif chart_type == 'radar':
                return self._create_radar_chart(df, title)
            elif chart_type == 'boxviolin':
                return self._create_box_violin_combo(df, title)
            elif chart_type == 'timeline':
                return self._create_timeline_chart(df, title)
            else:
                return self._create_bar_chart(df, title)
        except Exception:
            return None

    # === 原有图表方法（略作优化）===
    def _create_bar_chart(self, df, title):
        cat_cols = df.select_dtypes(include=['object']).columns.tolist()
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if not cat_cols:
            raise ValueError("缺少分类列")

        x_col = cat_cols[0]
        if num_cols:
            y_col = num_cols[0]
            fig = px.bar(df, x=x_col, y=y_col, title=title, color_discrete_sequence=self.color_palette)
        else:
            counts = df[x_col].value_counts()
            fig = px.bar(x=counts.index, y=counts.values, labels={'x': x_col, 'y': '数量'}, title=title)
        return fig

    def _create_pie_chart(self, df, title):
        cat_cols = df.select_dtypes(include=['object']).columns.tolist()
        if not cat_cols:
            raise ValueError("缺少分类列")
        col = cat_cols[0]
        counts = df[col].value_counts()
        fig = px.pie(names=counts.index, values=counts.values, title=title, color_discrete_sequence=self.color_palette)
        return fig

    def _create_line_chart(self, df, title):
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(num_cols) < 2:
            # 尝试用索引作为 X
            fig = px.line(df.reset_index(), x='index', y=num_cols[0] if num_cols else df.columns[0], title=title)
        else:
            fig = px.line(df, x=num_cols[0], y=num_cols[1], title=title)
        return fig

    def _create_scatter_chart(self, df, title):
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = df.select_dtypes(include=['object']).columns.tolist()
        if len(num_cols) < 2:
            raise ValueError("需要至少两个数值列")
        x, y = num_cols[0], num_cols[1]
        color = cat_cols[0] if cat_cols else None
        fig = px.scatter(df, x=x, y=y, color=color, title=title, color_discrete_sequence=self.color_palette)
        return fig

    def _create_histogram(self, df, title):
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if not num_cols:
            raise ValueError("缺少数值列")
        fig = px.histogram(df, x=num_cols[0], title=title, nbins=20, color_discrete_sequence=[self.color_palette[0]])
        return fig

    def _create_box_chart(self, df, title):
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if not num_cols:
            raise ValueError("缺少数值列")
        fig = px.box(df, y=num_cols[0], title=title, color_discrete_sequence=[self.color_palette[1]])
        return fig

    def _create_violin_chart(self, df, title):
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = df.select_dtypes(include=['object']).columns.tolist()
        if not num_cols:
            raise ValueError("缺少数值列")
        y = num_cols[0]
        x = cat_cols[0] if cat_cols else None
        fig = px.violin(df, x=x, y=y, title=title, color_discrete_sequence=self.color_palette)
        return fig

    def _create_heatmap(self, df, title):
        num_df = df.select_dtypes(include=[np.number])
        if num_df.shape[1] < 2:
            raise ValueError("需要至少两个数值列")
        corr = num_df.corr()
        fig = px.imshow(corr, title=title, color_continuous_scale='RdBu', aspect="auto")
        return fig

    def _create_sunburst_chart(self, df, title):
        cat_cols = df.select_dtypes(include=['object']).columns.tolist()
        if len(cat_cols) < 2:
            raise ValueError("需要至少两个分类列")
        path = cat_cols[:3]
        agg_df = df.groupby(path).size().reset_index(name='count')
        fig = px.sunburst(agg_df, path=path, values='count', title=title, color_discrete_sequence=self.color_palette)
        return fig

    def _create_treemap_chart(self, df, title):
        cat_cols = df.select_dtypes(include=['object']).columns.tolist()
        if len(cat_cols) < 2:
            raise ValueError("需要至少两个分类列")
        path = cat_cols[:3]
        agg_df = df.groupby(path).size().reset_index(name='count')
        fig = px.treemap(agg_df, path=path, values='count', title=title, color_discrete_sequence=self.color_palette)
        return fig

    # === 新增图表类型 ===

    def _create_area_chart(self, df, title):
        """面积图（适合时间序列累积）"""
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(num_cols) < 2:
            raise ValueError("面积图需要至少两个数值列")
        fig = px.area(df, x=num_cols[0], y=num_cols[1], title=title, color_discrete_sequence=[self.color_palette[2]])
        return fig

    def _create_funnel_chart(self, df, title):
        """漏斗图（需有 step 和 value 列）"""
        if 'step' in df.columns and 'value' in df.columns:
            fig = px.funnel(df, x='value', y='step', title=title, color_discrete_sequence=self.color_palette)
        else:
            # 自动假设第一列为 step，第二列为 value
            cat_cols = df.select_dtypes(include=['object']).columns.tolist()
            num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if not cat_cols or not num_cols:
                raise ValueError("漏斗图需要分类列（步骤）和数值列（值）")
            fig = px.funnel(df, x=num_cols[0], y=cat_cols[0], title=title, color_discrete_sequence=self.color_palette)
        return fig

    def _create_radar_chart(self, df, title):
        """雷达图（需多维数值）"""
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(num_cols) < 3:
            raise ValueError("雷达图需要至少3个数值维度")
        # 取第一行或多行平均
        if len(df) > 1:
            values = df[num_cols].mean().values
        else:
            values = df[num_cols].iloc[0].values
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=num_cols,
            fill='toself',
            name='指标'
        ))
        fig.update_layout(title=title, polar=dict(radialaxis=dict(visible=True)))
        return fig

    def _create_box_violin_combo(self, df, title):
        """箱线图 + 小提琴图组合"""
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = df.select_dtypes(include=['object']).columns.tolist()
        if not num_cols:
            raise ValueError("缺少数值列")
        y = num_cols[0]
        x = cat_cols[0] if cat_cols else None

        fig = go.Figure()
        if x:
            for category in df[x].unique():
                subset = df[df[x] == category][y]
                fig.add_trace(go.Violin(x=[category]*len(subset), y=subset, name=str(category), box_visible=True, meanline_visible=True))
        else:
            fig.add_trace(go.Violin(y=df[y], box_visible=True, meanline_visible=True))
        fig.update_layout(title=title)
        return fig

    def _create_timeline_chart(self, df, title):
        """时间线图（假设有一列为日期）"""
        date_cols = df.select_dtypes(include=['datetime', 'object']).columns.tolist()
        # 尝试解析日期
        for col in date_cols:
            if df[col].astype(str).str.contains(r'\d{4}').any():
                try:
                    df['parsed_date'] = pd.to_datetime(df[col], errors='coerce')
                    if df['parsed_date'].notna().sum() > 0:
                        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                        y = num_cols[0] if num_cols else df.columns[0]
                        fig = px.line(df, x='parsed_date', y=y, title=title)
                        return fig
                except:
                    continue
        # 回退到普通折线图
        return self._create_line_chart(df, title)

    # === 工具方法 ===
    def _create_empty_figure(self, message: str) -> go.Figure:
        fig = go.Figure()
        fig.add_annotation(text=message, x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False, font=dict(size=16, color="gray"))
        fig.update_layout(title="数据可视化", xaxis=dict(showgrid=False, visible=False), yaxis=dict(showgrid=False, visible=False))
        return fig

    def _generate_empty_chart(self, message: str) -> str:
        return self._create_empty_figure(message).to_html(include_plotlyjs='cdn')

    def generate_student_statistics_charts(self, stats_data: Dict[str, Any]) -> List[str]:
        """保持原有接口兼容"""
        charts = []
        # ...（原有逻辑不变）
        if 'by_college' in stats_data:
            # 使用新方法
            college_data = [{"学院": k, "人数": v} for k, v in stats_data['by_college'].items()]
            charts.append(self.generate_chart_from_data(college_data, 'pie', "各学院学生分布"))
        if 'by_grade' in stats_data:
            grade_data = [{"年级": k, "人数": v} for k, v in stats_data['by_grade'].items()]
            charts.append(self.generate_chart_from_data(grade_data, 'bar', "各年级学生分布"))
        if 'by_gender' in stats_data:
            gender_data = [{"性别": k, "人数": v} for k, v in stats_data['by_gender'].items()]
            charts.append(self.generate_chart_from_data(gender_data, 'pie', "性别分布"))
        return charts


# 全局实例
chart_generator = ChartGenerator()