# ophishal/common/models.py
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union

@dataclass
class Company:
    uid: str

@dataclass
class Department:
    uid: str
    company: "Company"
    name: Optional[str]
    email: Optional[str]
    head: Optional["Employee"]

@dataclass
class Employee:
    uid: str
    name: str
    username: str
    department: Department
    email: Optional[str]
    phone: Optional[str]
    reports_to: Optional["Employee"]

Target = Union[Employee, Department, Company]
