import enum


class AuditEntityType(str, enum.Enum):
    DECISION = "Decision"
    ALTERNATIVE = "Alternative"
    COMMENT = "Comment"
    DISCUSSION_THREAD = "DiscussionThread"
    MEETING_NOTE = "MeetingNote"
    APPROVAL = "Approval"
    USER = "User"