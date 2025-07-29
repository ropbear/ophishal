from dataclasses import dataclass
from typing import List, Optional


@dataclass
class CompanyProfile:
    uid:                str
    official_name:      str
    common_names:       List[str]
    abbreviations:      List[str]
    net_worth:          str
    number_of_employees: int
    type:               str
    industry:           str


@dataclass
class EmployeeProfile:
    uid:            str
    first_name:     str
    last_name:      str
    nickname:       Optional[str]
    username:       str
    department:     str
    work_title:     str
    signature_block: str
    work_email:     str
    work_phone:     str
    personal_email: Optional[str]
    personal_phone: Optional[str]
    location:       str
    reports_to:     Optional[str]


@dataclass
class DepartmentProfile:
    uid:        str
    name:       str
    company_uid: str
    head_uid:   Optional[str]


@dataclass
class CultureProfile:
    city:           str
    province:       str
    country_code:   str
    workplace:      str

