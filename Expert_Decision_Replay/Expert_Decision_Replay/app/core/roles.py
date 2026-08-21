from enum import Enum


class Role(str, Enum):
    EMPLOYEE = "Employee"
    MANAGER = "Manager"
    ADMINISTRATOR = "Administrator"