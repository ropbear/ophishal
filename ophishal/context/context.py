# ophishal/context/context.py
from typing import Dict, List, Optional
from ophishal.context.profile import CompanyProfile, EmployeeProfile, DepartmentProfile

class Context:
    """
    Encapsulates the operational context for a phishing campaign, 
    including the full organizational structure and metadata needed
    for context-aware phishing content generation and campaign execution.

    :param company: Metadata about the target company.
    :type company: CompanyProfile
    :param employees: All known employee profiles, keyed by employee ID.
    :type employees: Dict[str, EmployeeProfile]
    :param departments: List of organizational departments.
    :type departments: Optional[List[DepartmentProfile]]
    :param culture: Cultural attributes relevant to communication style.
    :type culture: Optional[dict]
    :param information_technologies: Technologies in use within the organization.
    :type information_technologies: Optional[List[str]]
    :param current_events: Ongoing or recent events that may inform pretext scenarios.
    :type current_events: Optional[List[str]]
    :param current_access: List of employee IDs for whom access is known or simulated.
    :type current_access: Optional[List[str]]

    :ivar company: Metadata about the target company.
    :ivar employees: All known employee profiles, keyed by employee ID.
    :ivar departments: List of organizational departments.
    :ivar culture: Cultural attributes relevant to communication style.
    :ivar information_technologies: Technologies in use within the organization.
    :ivar current_events: Ongoing or recent events that may inform pretext scenarios.
    :ivar current_access: List of employee IDs for whom access is known or simulated.
    """
    def __init__(
        self,
        company: CompanyProfile,
        employees: Dict[str, EmployeeProfile],
        departments: Optional[List[DepartmentProfile]] = None,
        culture: Optional[dict] = None,
        information_technologies: Optional[List[str]] = None,
        current_events: Optional[List[str]] = None,
        current_access: Optional[List[str]] = None  # List of employee_ids
    ):
        self.company = company
        self.employees = employees
        self.departments = departments or []
        self.culture = culture or {}
        self.information_technologies = information_technologies or []
        self.current_events = current_events or []
        self.current_access = current_access or []

    @classmethod
    def from_json(cls, data: dict) -> "Context":
        company = CompanyProfile(**data["company"])

        employees = {
            eid: EmployeeProfile(**profile) for eid, profile in data["employees"].items()
        }

        departments = [
            DepartmentProfile(**dept) for dept in data.get("departments", [])
        ]

        return cls(
            company=company,
            employees=employees,
            departments=departments,
            culture=data.get("culture"),
            information_technologies=data.get("information_technologies"),
            current_events=data.get("current_events"),
            current_access=data.get("current_access")
        )