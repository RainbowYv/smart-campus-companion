from typing import Optional

from fastapi import UploadFile
from pydantic import BaseModel, Field


class LoginInfo(BaseModel):
    number: str
    password: str


class FrontUserQuery(BaseModel):
    chat_text: str
    file: Optional[UploadFile] = Field(default=None)


class FrontUserQueryInterrupt(BaseModel):
    chat_text: str
    file: Optional[UploadFile] = Field(default=None)
    resume_data: Optional[dict]


class LeaveData(BaseModel):
    """提取请假所需信息"""
    leave_type: Optional[str] = Field(None, description="请假类型，必须归一化为 'sick' (病假), 'personal' (事假), 或 'other' (其他)")
    start_date: Optional[str] = Field(None, description="开始日期，格式：YYYY-MM-DD")
    end_date: Optional[str] = Field(None, description="结束日期，格式：YYYY-MM-DD")
    reason: Optional[str] = Field(None, description="请假具体原因")
