from pydantic import BaseModel, Field, ConfigDict


class RagQuery(BaseModel):

    hyde_doc: str = Field(description="模拟一份关于该问题的简短政策文档段落")
    keywords: str = Field(description="提取3-5个核心关键词，用空格分隔")
    domain: str = Field(description="确定搜索领域：academic (教务), life (生活), news (新闻)",
                        default="hfut_postgraduate_admission_policy")
