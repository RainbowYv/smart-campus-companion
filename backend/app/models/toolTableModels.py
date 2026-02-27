from pydantic import BaseModel, ConfigDict
from typing import List


class ScoreToolResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    course_name: str
    score: float
    grade_point: float
    status: str
    semester_name: str


class CourseToolResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    course_name: str
    teacher_name: str
    classroom: str
    day_of_week: int
    start_period: int
    end_period: int
    week_range: str
    semester_name: str
