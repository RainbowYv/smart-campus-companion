from pydantic import BaseModel, ConfigDict, Field, AliasChoices
from typing import Optional, Dict


class UserInRedis(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uid: Optional[int] = Field(default=1, validation_alias="id")  # 数据库ID (student_id 或 teacher_id)
    role: Optional[str] = Field(default="student")  # "student" | "teacher" | "admin"
    name: Optional[str] = Field(default="小明", validation_alias="name")  # 显示名称
    number: Optional[str] = Field(default=None, validation_alias=AliasChoices("student_number", "employee_number"))  # 学号或者教师编号
    preferences: Optional[Dict] = Field(default=None)  # {"notify_time": "morning", "theme": "dark"}

