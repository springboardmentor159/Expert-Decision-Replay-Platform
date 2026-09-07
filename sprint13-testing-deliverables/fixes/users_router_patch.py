# Fix for BUG-001 (see BUG_TRACKER.md).
#
# This is NOT a full file replacement - it shows the specific edits to
# make in app/routers/users.py. Diff-style: unchanged context is
# included so the surrounding code is unambiguous.

# 1) Add require_role to the existing import:
#
#    from app.utils.security import (
#        hash_password,
#        verify_password,
#        create_access_token,
#        get_current_user,
#        require_role,        # <-- add this
#    )

# 2) GET ALL USERS - Administrator only (was: any authenticated user)
#
# @router.get("/", response_model=List[UserResponse])
# def get_users(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(require_role("Administrator"))   # was: get_current_user
# ):
#     return db.query(User).all()


# 3) GET USER BY ID - self, or Administrator (was: any authenticated user)
#
# @router.get("/{user_id}", response_model=UserResponse)
# def get_user(
#     user_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     if user_id != current_user.id and current_user.role != "Administrator":
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You do not have permission to view this user"
#         )
#
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
#     return user


# 4) UPDATE USER - self (limited fields), or Administrator (was: any authenticated user)
#
# @router.put("/{user_id}", response_model=UserResponse)
# def update_user(
#     user_id: int,
#     user_data: UserUpdate,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     is_self = user_id == current_user.id
#     is_admin = current_user.role == "Administrator"
#
#     if not is_self and not is_admin:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You do not have permission to update this user"
#         )
#
#     # Only an Administrator may change someone's role.
#     if user_data.role is not None and not is_admin:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Only an Administrator can change a user's role"
#         )
#
#     ... (rest of the function body is unchanged) ...


# 5) DELETE USER - Administrator only (was: any authenticated user)
#
# @router.delete("/{user_id}")
# def delete_user(
#     user_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(require_role("Administrator"))   # was: get_current_user
# ):
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
#     db.delete(user)
#     db.commit()
#     return {"message": "User deleted successfully"}
