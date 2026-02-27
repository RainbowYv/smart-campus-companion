import enum
from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import String, Integer, Boolean, ForeignKey, DECIMAL, Text, Date, DateTime, func, Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs


# 1. 定义基础模型类
class Base(AsyncAttrs, DeclarativeBase):
    pass


# 2. 定义枚举类型 (与数据库 Enum 对应)
class Gender(str, enum.Enum):
    M = "M"
    F = "F"


class EnrollmentStatus(str, enum.Enum):
    enrolled = "enrolled"
    completed = "completed"
    dropped = "dropped"


class EventType(str, enum.Enum):
    lecture = "lecture"
    news = "news"


# --- 学院表 ---
class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="学院名称")
    code: Mapped[Optional[str]] = mapped_column(String(20), comment="学院代号")

    # 反向关联
    students: Mapped[List["Student"]] = relationship(back_populates="department")
    teachers: Mapped[List["Teacher"]] = relationship(back_populates="department")
    courses: Mapped[List["Course"]] = relationship(back_populates="department")

    def __repr__(self):
        return f"<Department {self.name}>"


# --- 学期表 ---
class Semester(Base):
    __tablename__ = "semesters"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="学期名称 2024-2025-1")
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)

    schedules: Mapped[List["CourseSchedule"]] = relationship(back_populates="semester")


# --- 学生表 ---
class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    gender: Mapped[Optional[Gender]] = mapped_column(comment="性别")
    enrollment_year: Mapped[Optional[int]] = mapped_column(Integer)
    class_name: Mapped[Optional[str]] = mapped_column(String(50))

    # 外键
    dept_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"))

    # 关联
    department: Mapped[Optional["Department"]] = relationship(back_populates="students")
    enrollments: Mapped[List["Enrollment"]] = relationship(back_populates="student")
    leave_requests: Mapped[List["LeaveRequest"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan"  # 如果学生被删除，相关的请假记录也删除
    )


# --- 教师表 ---
class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(50))

    # 外键
    dept_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"))

    # 关联
    department: Mapped[Optional["Department"]] = relationship(back_populates="teachers")
    schedules: Mapped[List["CourseSchedule"]] = relationship(back_populates="teacher")


# --- 课程目录表 (抽象课程) ---
class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    credits: Mapped[float] = mapped_column(DECIMAL(3, 1), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, comment="RAG检索用简介")

    dept_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"))

    department: Mapped[Optional["Department"]] = relationship(back_populates="courses")
    schedules: Mapped[List["CourseSchedule"]] = relationship(back_populates="course")


# --- 排课表 (具体排课) ---
class CourseSchedule(Base):
    __tablename__ = "course_schedules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    classroom: Mapped[Optional[str]] = mapped_column(String(50))
    day_of_week: Mapped[Optional[int]] = mapped_column(Integer, comment="1-7")
    start_period: Mapped[Optional[int]] = mapped_column(Integer, comment="开始节次")
    end_period: Mapped[Optional[int]] = mapped_column(Integer)
    week_range: Mapped[Optional[str]] = mapped_column(String(20))
    max_capacity: Mapped[int] = mapped_column(Integer, default=60)

    # 外键
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"))
    semester_id: Mapped[int] = mapped_column(ForeignKey("semesters.id"))

    # 关联
    course: Mapped["Course"] = relationship(back_populates="schedules")
    teacher: Mapped["Teacher"] = relationship(back_populates="schedules")
    semester: Mapped["Semester"] = relationship(back_populates="schedules")
    enrollments: Mapped[List["Enrollment"]] = relationship(back_populates="schedule")


# --- 选课与成绩表 ---
class Enrollment(Base):
    __tablename__ = "enrollments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    score: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2), comment="分数, NULL表示未出分")
    grade_point: Mapped[Optional[float]] = mapped_column(DECIMAL(3, 1))
    status: Mapped[EnrollmentStatus] = mapped_column(default=EnrollmentStatus.enrolled)

    # 外键
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    schedule_id: Mapped[int] = mapped_column(ForeignKey("course_schedules.id"))

    # 关联
    student: Mapped["Student"] = relationship(back_populates="enrollments")
    schedule: Mapped["CourseSchedule"] = relationship(back_populates="enrollments")




# --- 校园事件表 (用于 RAG/Qdrant) ---
class CampusEvent(Base):
    __tablename__ = "campus_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(String(1000), comment="向量化摘要")
    content: Mapped[Optional[str]] = mapped_column(Text, comment="完整正文")
    event_type: Mapped[EventType] = mapped_column(default=EventType.news)

    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime)
    location: Mapped[Optional[str]] = mapped_column(String(100))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    status: Mapped[int] = mapped_column(Integer, default=1, comment="1正常 0删除")


# 1. 定义请假类型枚举
class LeaveType(str, enum.Enum):
    SICK = "sick"  # 病假
    PERSONAL = "personal"  # 事假
    OTHER = "other"  # 其他


# 2. 定义审批状态枚举
class LeaveStatus(str, enum.Enum):
    PENDING = "pending"  # 待审批
    APPROVED = "approved"  # 已批准
    REJECTED = "rejected"  # 已驳回
    CANCELLED = "cancelled"  # 已取消


# 3. 请假申请表映射类
class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 外键：关联学生
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)

    # 请假详情
    leave_type: Mapped[LeaveType] = mapped_column(
        Enum(LeaveType),
        nullable=False,
        default=LeaveType.PERSONAL,
        comment="请假类型: sick, personal, other"
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False, comment="开始日期")
    end_date: Mapped[date] = mapped_column(Date, nullable=False, comment="结束日期")
    reason: Mapped[str] = mapped_column(Text, nullable=False, comment="请假理由")

    # 状态管理
    status: Mapped[LeaveStatus] = mapped_column(
        Enum(LeaveStatus),
        default=LeaveStatus.PENDING,
        comment="审批状态: pending, approved, rejected, cancelled"
    )

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # 关联关系
    student: Mapped["Student"] = relationship(back_populates="leave_requests")

    def __repr__(self):
        return f"<LeaveRequest(id={self.id}, student_id={self.student_id}, status={self.status})>"