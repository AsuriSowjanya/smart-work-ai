from sqlalchemy import Boolean, Column, DateTime, Integer, String

from database import Base
class TaskDB(Base):
    __tablename__ = "tasks"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )
    title = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)
    priority = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
    start = Column(String, nullable=True)
    end = Column(String, nullable=True)


class ProductivityLogDB(Base):
    __tablename__ = "productivity_logs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    scheduled_start = Column(String, nullable=True)
    scheduled_end = Column(String, nullable=True)
    duration = Column(Integer, nullable=False)
    priority = Column(String, nullable=False)
    completed = Column(Boolean, nullable=False)
    completed_at = Column(DateTime, nullable=True)