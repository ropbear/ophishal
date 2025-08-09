# ophishal/common/util.py
from ophishal.common.models import Target


def resolve_target(uid: str, obj:object) -> Target:
    if uid == obj.company.uid:
        return obj.company
    if uid in obj.departments:
        return obj.departments[uid]
    if uid in obj.employees:
        return obj.employees[uid]
    raise ValueError(f"Invalid target UID in {obj}: {uid}")
