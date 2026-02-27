from fastapi import Depends
from langchain_core.tools import tool
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..db.session import get_async_db
from ..models.tableModels import Enrollment, CourseSchedule, Course, Teacher, Semester
from ..models.toolTableModels import ScoreToolResponse, CourseToolResponse


def create_campus_tools():
    @tool
    async def get_grades_by_student_id(user_id: int):
        """"
            根据学生id查询学生的各科成绩
        """
        async with get_async_db() as db:
            stmt = (
                select(
                    Course.name.label("course_name"),
                    Enrollment.score,
                    Enrollment.grade_point,
                    Enrollment.status,
                    Semester.name.label("semester_name")
                )
                .select_from(Enrollment)
                .join(CourseSchedule, Enrollment.schedule_id == CourseSchedule.id)
                .join(Course, CourseSchedule.course_id == Course.id)
                .join(Semester, CourseSchedule.semester_id == Semester.id)
                .where(Enrollment.student_id == user_id)
                .where(Enrollment.score.isnot(None))  # 使用 .isnot(None)
                .order_by(Semester.id.desc())
            )

            result = await db.execute(stmt)
            score_data = result.mappings().all()
            score_data = [ScoreToolResponse.model_validate(s).model_dump() for s in score_data]
            print(f"score_data: {score_data}")

            return score_data

    @tool
    async def get_courses_by_student_id(user_id: int):
        """
        description: 根据学生id查看学生当前学期的课表
        :param user_id: 学生id
        :return: 学生当前学期的课表
        """
        async with get_async_db() as db:
            try:
                # 1. 构建查询语句
                # 我们从 Enrollment 出发，因为只有学生选了课才会在课表里
                stmt = (
                    select(
                        Course.name.label("course_name"),
                        Teacher.name.label("teacher_name"),
                        CourseSchedule.classroom,
                        CourseSchedule.day_of_week,
                        CourseSchedule.start_period,
                        CourseSchedule.end_period,
                        CourseSchedule.week_range,
                        Semester.name.label("semester_name")
                    )
                    # 【关键修复点 1】显式指定起始表
                    .select_from(Enrollment)
                    # 【关键修复点 2】按照关系链条依次顺序连接，并明确 ON 条件
                    .join(CourseSchedule, Enrollment.schedule_id == CourseSchedule.id)
                    .join(Course, CourseSchedule.course_id == Course.id)
                    .join(Teacher, CourseSchedule.teacher_id == Teacher.id)
                    .join(Semester, CourseSchedule.semester_id == Semester.id)
                    # 过滤条件
                    .where(Enrollment.student_id == user_id)
                    .where(Semester.is_current == True)
                    .where(Enrollment.status == "enrolled")
                    .order_by(CourseSchedule.day_of_week, CourseSchedule.start_period)
                )

                result = await db.execute(stmt)
                # 获取所有行并转为字典
                schedule_data = result.mappings().all()
                schedule_data = [CourseToolResponse.model_validate(s).model_dump() for s in schedule_data]

                print(f"schedule_data: {schedule_data}")

                return schedule_data

            except Exception as e:
                print(f"查询课表时发生错误: {str(e)}")
                return None

    tools = [get_grades_by_student_id, get_courses_by_student_id]
    return tools
