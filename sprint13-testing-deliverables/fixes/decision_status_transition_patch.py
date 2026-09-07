# Fix for BUG-002 (see BUG_TRACKER.md).
#
# Add near the top of app/routers/decision.py, alongside
# ALLOWED_SORT_FIELDS:

VALID_STATUS_TRANSITIONS = {
    "Draft": {"Under Review", "Archived"},
    "Under Review": {"Approved", "Rejected", "Draft"},
    "Approved": {"Archived"},
    "Rejected": {"Archived"},
    "Archived": set(),  # terminal - no transitions out
}


def _validate_status_transition(current_status: str, new_status: str) -> None:
    if new_status == current_status:
        return  # idempotent no-op PATCH is harmless

    allowed = VALID_STATUS_TRANSITIONS.get(current_status, set())
    if new_status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Cannot transition decision from '{current_status}' to "
                f"'{new_status}'. Allowed next states: "
                f"{sorted(allowed) or 'none (terminal state)'}"
            ),
        )


# Then, inside update_decision_status(), right after
# `decision = get_decision_or_404(decision_id, db)` and before any
# mutation happens, add:
#
#     _validate_status_transition(decision.status, status_data.status.value)
#
# The rest of the function body (audit logging, versioning, activity
# logging, response) is unchanged.
