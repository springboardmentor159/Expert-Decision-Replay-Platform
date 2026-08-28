from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.decision import Decision
from app.models.tag import Tag
from app.models.user import User
from app.schemas.tag import (
    DecisionTagCreate,
    TagCreate,
    TagResponse
)
from app.services.auth import get_current_user


router = APIRouter(
    prefix="/tags",
    tags=["Tags"]
)


# ============================================================
# CREATE TAG
# ============================================================

@router.post(
    "",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED
)
def create_tag(
    tag_data: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # --------------------------------------------------------
    # User must belong to an organization
    # --------------------------------------------------------

    if current_user.organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not assigned to an organization"
        )

    # --------------------------------------------------------
    # Check tag name only inside current organization
    # --------------------------------------------------------

    existing_tag = (
        db.query(Tag)
        .filter(
            Tag.name == tag_data.name,
            Tag.organization_id == current_user.organization_id
        )
        .first()
    )

    if existing_tag is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tag already exists in your organization"
        )

    # --------------------------------------------------------
    # Create tag
    # --------------------------------------------------------

    tag = Tag(
        name=tag_data.name,
        organization_id=current_user.organization_id
    )

    db.add(tag)
    db.commit()
    db.refresh(tag)

    return tag


# ============================================================
# GET ALL TAGS
# ============================================================

@router.get(
    "",
    response_model=list[TagResponse]
)
def get_tags(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not assigned to an organization"
        )

    return (
        db.query(Tag)
        .filter(
            Tag.organization_id == current_user.organization_id
        )
        .order_by(Tag.name)
        .all()
    )


# ============================================================
# GET TAG BY ID
# ============================================================

@router.get(
    "/{tag_id}",
    response_model=TagResponse
)
def get_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    tag = (
        db.query(Tag)
        .filter(
            Tag.id == tag_id,
            Tag.organization_id == current_user.organization_id
        )
        .first()
    )

    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    return tag


# ============================================================
# DELETE TAG
# ============================================================

@router.delete(
    "/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # --------------------------------------------------------
    # Find tag inside current organization only
    # --------------------------------------------------------

    tag = (
        db.query(Tag)
        .filter(
            Tag.id == tag_id,
            Tag.organization_id == current_user.organization_id
        )
        .first()
    )

    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    # --------------------------------------------------------
    # Prevent deletion while assigned to decisions
    # --------------------------------------------------------

    if tag.decisions:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete a tag assigned to decisions"
        )

    db.delete(tag)
    db.commit()

    return None


# ============================================================
# ASSIGN MULTIPLE TAGS TO A DECISION
# ============================================================

@router.post(
    "/{decision_id}/tags",
    response_model=list[TagResponse],
    status_code=status.HTTP_201_CREATED
)
def assign_tags_to_decision(
    decision_id: int,
    tag_data: DecisionTagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # --------------------------------------------------------
    # Find decision inside current organization
    # --------------------------------------------------------

    decision = (
        db.query(Decision)
        .filter(
            Decision.id == decision_id,
            Decision.organization_id == current_user.organization_id
        )
        .first()
    )

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    # --------------------------------------------------------
    # Remove duplicate IDs from request
    # --------------------------------------------------------

    tag_ids = list(
        dict.fromkeys(tag_data.tag_ids)
    )

    # --------------------------------------------------------
    # Find tags belonging to current organization
    # --------------------------------------------------------

    tags = (
        db.query(Tag)
        .filter(
            Tag.id.in_(tag_ids),
            Tag.organization_id == current_user.organization_id
        )
        .all()
    )

    # --------------------------------------------------------
    # Check missing tags
    # --------------------------------------------------------

    found_tag_ids = {
        tag.id
        for tag in tags
    }

    missing_tag_ids = [
        tag_id
        for tag_id in tag_ids
        if tag_id not in found_tag_ids
    ]

    if missing_tag_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag(s) not found: {missing_tag_ids}"
        )

    # --------------------------------------------------------
    # Check already assigned tags
    # --------------------------------------------------------

    existing_tag_ids = {
        tag.id
        for tag in decision.tags
    }

    already_assigned = [
        tag_id
        for tag_id in tag_ids
        if tag_id in existing_tag_ids
    ]

    if already_assigned:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Tag(s) already assigned to this decision: "
                f"{already_assigned}"
            )
        )

    # --------------------------------------------------------
    # Assign tags
    # --------------------------------------------------------

    decision.tags.extend(tags)

    db.commit()

    return tags


# ============================================================
# GET ALL TAGS ASSIGNED TO A DECISION
# ============================================================

@router.get(
    "/{decision_id}/tags",
    response_model=list[TagResponse]
)
def get_decision_tags(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # --------------------------------------------------------
    # Find decision inside current organization
    # --------------------------------------------------------

    decision = (
        db.query(Decision)
        .filter(
            Decision.id == decision_id,
            Decision.organization_id == current_user.organization_id
        )
        .first()
    )

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    return decision.tags


# ============================================================
# REMOVE TAG FROM DECISION
# ============================================================

@router.delete(
    "/{decision_id}/tags/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_tag_from_decision(
    decision_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # --------------------------------------------------------
    # Find decision inside current organization
    # --------------------------------------------------------

    decision = (
        db.query(Decision)
        .filter(
            Decision.id == decision_id,
            Decision.organization_id == current_user.organization_id
        )
        .first()
    )

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    # --------------------------------------------------------
    # Find tag inside current organization
    # --------------------------------------------------------

    tag = (
        db.query(Tag)
        .filter(
            Tag.id == tag_id,
            Tag.organization_id == current_user.organization_id
        )
        .first()
    )

    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    # --------------------------------------------------------
    # Check whether tag is assigned
    # --------------------------------------------------------

    if tag not in decision.tags:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag is not assigned to this decision"
        )

    # --------------------------------------------------------
    # Remove tag
    # --------------------------------------------------------

    decision.tags.remove(tag)

    db.commit()

    return None