import enum


class AuditAction(str, enum.Enum):

    CREATE = "CREATE"

    UPDATE = "UPDATE"

    DELETE = "DELETE"

    APPROVE = "APPROVE"

    REJECT = "REJECT"

    SUBMIT = "SUBMIT"

    ARCHIVE = "ARCHIVE"

    LOGIN = "LOGIN"

    LOGOUT = "LOGOUT"

    ACCESS = "ACCESS"