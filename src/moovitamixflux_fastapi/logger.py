from datetime import datetime
from faker import Faker
from fastapi_pagination import Page
from pydantic import BaseModel, Field, PrivateAttr
from typing import List
import random

fake = Faker()

class Log(BaseModel):
    raised_at: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    level: int = Field(..., description="Log level: 0=INFO, 1=WARNING, 2=ERROR")
    message: str = Field(..., description="Log message")

    @classmethod
    def generate_fake(cls) -> "Log":
        return cls(
            raised_at=int(fake.date_time_between(start_date="-2y", end_date="now").timestamp()),
            level=random.choice([0, 1, 2]),
            message=fake.sentence(),
        )

    @classmethod
    def generate_fake_page(cls) -> Page["Log"]:
        logs = [Log.generate_fake() for _ in range(10)]
        return Page(
            items=logs,
            size=len(logs),
            page=random.randint(1, 10),
            total=len(logs) * random.randint(1, 10),
        )
        
class Logger(BaseModel):
    _logs: List[Log] = PrivateAttr(default_factory=list)

    def add_log(self, log: Log):
        self._logs.append(log)

    @classmethod
    def generate_fake(cls) -> "Logger":
        logger = cls()
        logger._logs.extend([Log.generate_fake() for _ in range(10)])
        return logger