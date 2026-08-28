from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.organization import Organization
from app.models.user import User, UserRole
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
)
from app.services.auth import get_current_user
from app.services.authorization import require_roles


router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"]
)


# ============================================================
# CREATE ORGANIZATION
# Administrator only
# ============================================================

@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_organization(
    organization_data: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMINISTRATOR)
    )
):
    existing_organization = (
        db.query(Organization)
        .filter(
            Organization.name == organization_data.name
        )
        .first()
    )

    if existing_organization:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Organization name already exists"
        )

    organization = Organization(
        name=organization_data.name,
        description=organization_data.description
    )

    db.add(organization)
    db.commit()
    db.refresh(organization)

    return organization


# ============================================================
# GET ALL ORGANIZATIONS
# Administrator only
# ============================================================

@router.get(
    "",
    response_model=list[OrganizationResponse]
)
def get_organizations(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMINISTRATOR)
    )
):
    return (
        db.query(Organization)
        .order_by(Organization.name)
        .all()
    )


# ============================================================
# GET ORGANIZATION BY ID
#
# Administrator can view any organization.
# Other users can only view their own organization.
# ============================================================

@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse
)
def get_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    organization = (
        db.query(Organization)
        .filter(
            Organization.id == organization_id
        )
        .first()
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # Administrator can view any organization
    if current_user.role == UserRole.ADMINISTRATOR:
        return organization

    # Other users must belong to the organization
    if current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this organization"
        )

    return organization


# ============================================================
# UPDATE ORGANIZATION
# Administrator only
# ============================================================

@router.put(
    "/{organization_id}",
    response_model=OrganizationResponse
)
def update_organization(
    organization_id: int,
    organization_data: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMINISTRATOR)
    )
):
    organization = (
        db.query(Organization)
        .filter(
            Organization.id == organization_id
        )
        .first()
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # Check duplicate organization name
    if organization_data.name is not None:
        existing_organization = (
            db.query(Organization)
            .filter(
                Organization.name == organization_data.name,
                Organization.id != organization_id
            )
            .first()
        )

        if existing_organization:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Organization name already exists"
            )

        organization.name = organization_data.name

    if organization_data.description is not None:
        organization.description = organization_data.description

    db.commit()
    db.refresh(organization)

    return organization


# ============================================================
# DELETE ORGANIZATION
# Administrator only
#
# Organization cannot be deleted if users or decisions
# are still associated with it.
# ============================================================

@router.delete(
    "/{organization_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMINISTRATOR)
    )
):
    organization = (
        db.query(Organization)
        .filter(
            Organization.id == organization_id
        )
        .first()
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # Do not allow deletion when users are assigned
    if organization.users:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Cannot delete organization while users "
                "are assigned to it"
            )
        )

    # Do not allow deletion when decisions exist
    if organization.decisions:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Cannot delete organization while decisions "
                "belong to it"
            )
        )

    # Do not allow deletion when tags exist
    if organization.tags:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Cannot delete organization while tags "
                "belong to it"
            )
        )

    db.delete(organization)
    db.commit()

    return None