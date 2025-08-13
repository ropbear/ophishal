# ophishal/common/models.py
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union

@dataclass
class Company:
    uid: str
    official_name: str
    common_names: List[str]
    abbreviations: List[str]
    net_worth: str
    number_of_employees: int
    type: str
    industry: str

@dataclass
class Department:
    uid: str
    name: str
    company: "Company"
    head: Optional["Employee"]

@dataclass
class Employee:
    uid: str
    first_name: str
    last_name: str
    nickname: Optional[str]
    username: str
    department: Department
    work_title: str
    signature_block: str
    work_email: Optional[str]
    work_phone: Optional[str]
    personal_email: Optional[str]
    personal_phone: Optional[str]
    location: str
    reports_to: Optional["Employee"]
    sample_text: Optional[str]

@dataclass
class Culture:
    city: str
    province: str
    country_code: str
    workplace: str

Target = Union[Employee, Department, Company]
