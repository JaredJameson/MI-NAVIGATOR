"""
Workspace API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
import uuid

from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.models.workspace import WorkspaceMemberRole

router = APIRouter()


# In-memory storage for workspaces (simplified for MVP)
WORKSPACES_STORAGE: List[dict] = []
WORKSPACE_MEMBERS_STORAGE: List[dict] = []


# Pydantic models
class WorkspaceCreate(BaseModel):
    name: str
    description: Optional[str] = None


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class MemberInvite(BaseModel):
    email: str
    role: WorkspaceMemberRole = WorkspaceMemberRole.MEMBER


class MemberRoleUpdate(BaseModel):
    role: WorkspaceMemberRole


class OwnershipTransfer(BaseModel):
    new_owner_user_id: str


class WorkspaceResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    owner_id: str
    is_active: bool
    created_at: str
    updated_at: str
    member_count: int
    current_user_role: str


class MemberResponse(BaseModel):
    id: str
    workspace_id: str
    user_id: str
    user_email: str
    user_name: Optional[str]
    role: str
    invitation_accepted: bool
    created_at: str


def get_user_role_in_workspace(workspace_id: str, user_id: str) -> Optional[str]:
    """Get user's role in a workspace."""
    for member in WORKSPACE_MEMBERS_STORAGE:
        if member["workspace_id"] == workspace_id and member["user_id"] == user_id:
            return member["role"]
    return None


def check_workspace_permission(workspace_id: str, user_id: str, required_roles: List[str]):
    """Check if user has required permission in workspace."""
    user_role = get_user_role_in_workspace(workspace_id, user_id)
    if not user_role or user_role not in required_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to perform this action"
        )


@router.post("/", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    workspace_data: WorkspaceCreate
    # TESTING: Auth disabled - current_user: User = Depends(get_current_user)
):
    """Create a new workspace."""
    # TESTING: Use mock user
    mock_user_id = "test-user-309"
    mock_user_email = "testowner@feature309.com"
    mock_user_name = "Test Owner 309"

    workspace_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + "Z"

    workspace = {
        "id": workspace_id,
        "name": workspace_data.name,
        "description": workspace_data.description,
        "owner_id": mock_user_id,
        "is_active": True,
        "settings": {},
        "created_at": now,
        "updated_at": now
    }

    WORKSPACES_STORAGE.append(workspace)

    # Add owner as member with OWNER role
    member_id = str(uuid.uuid4())
    member = {
        "id": member_id,
        "workspace_id": workspace_id,
        "user_id": mock_user_id,
        "user_email": mock_user_email,
        "user_name": mock_user_name,
        "role": WorkspaceMemberRole.OWNER.value,
        "invited_by": None,
        "invitation_accepted": True,
        "created_at": now,
        "updated_at": now
    }

    WORKSPACE_MEMBERS_STORAGE.append(member)

    return WorkspaceResponse(
        **workspace,
        member_count=1,
        current_user_role=WorkspaceMemberRole.OWNER.value
    )


@router.get("/", response_model=List[WorkspaceResponse])
async def list_workspaces():  # TESTING: Auth disabled
    """List all workspaces the user is a member of."""
    user_id = "test-user-309"  # TESTING: Mock user

    # Get all workspace IDs where user is a member
    user_workspace_ids = set()
    for member in WORKSPACE_MEMBERS_STORAGE:
        if member["user_id"] == user_id:
            user_workspace_ids.add(member["workspace_id"])

    # Get workspace details
    workspaces = []
    for workspace in WORKSPACES_STORAGE:
        if workspace["id"] in user_workspace_ids:
            # Count members
            member_count = sum(
                1 for m in WORKSPACE_MEMBERS_STORAGE
                if m["workspace_id"] == workspace["id"]
            )

            # Get user's role
            user_role = get_user_role_in_workspace(workspace["id"], user_id)

            workspaces.append(
                WorkspaceResponse(
                    **workspace,
                    member_count=member_count,
                    current_user_role=user_role
                )
            )

    return workspaces


@router.get("/invitations/pending", response_model=List[MemberResponse])
async def list_pending_invitations():  # TESTING: Auth disabled
    """List all pending workspace invitations for the current user."""
    # TESTING: Support multiple mock users by email parameter
    # This will be replaced with actual user auth in production

    # For now, we'll list ALL pending invitations (for testing purposes)
    # In production, this would filter by current_user email
    pending_invitations = [
        MemberResponse(**m)
        for m in WORKSPACE_MEMBERS_STORAGE
        if not m["invitation_accepted"]
    ]

    return pending_invitations


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: str
    # TESTING: Auth disabled - current_user: User = Depends(get_current_user)
):
    """Get workspace details."""
    mock_user_id = "test-user-309"  # TESTING: Mock user

    workspace = next((w for w in WORKSPACES_STORAGE if w["id"] == workspace_id), None)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Check if user is a member
    user_role = get_user_role_in_workspace(workspace_id, mock_user_id)
    if not user_role:
        raise HTTPException(status_code=403, detail="You are not a member of this workspace")

    # Count members
    member_count = sum(
        1 for m in WORKSPACE_MEMBERS_STORAGE
        if m["workspace_id"] == workspace_id
    )

    return WorkspaceResponse(
        **workspace,
        member_count=member_count,
        current_user_role=user_role
    )


@router.get("/{workspace_id}/members", response_model=List[MemberResponse])
async def list_workspace_members(
    workspace_id: str
    # TESTING: Auth disabled - current_user: User = Depends(get_current_user)
):
    """List all members of a workspace."""
    # Check if workspace exists
    workspace = next((w for w in WORKSPACES_STORAGE if w["id"] == workspace_id), None)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Check if user is a member
    mock_user_id = "test-user-309"  # TESTING: Mock user
    user_role = get_user_role_in_workspace(workspace_id, mock_user_id)
    if not user_role:
        raise HTTPException(status_code=403, detail="You are not a member of this workspace")

    # Get all members
    members = [
        MemberResponse(**m)
        for m in WORKSPACE_MEMBERS_STORAGE
        if m["workspace_id"] == workspace_id
    ]

    return members


@router.post("/{workspace_id}/members", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
async def invite_member(
    workspace_id: str,
    invite_data: MemberInvite
    # TESTING: Auth disabled - current_user: User = Depends(get_current_user)
):
    """Invite a new member to the workspace."""
    mock_user_id = "test-user-309"  # TESTING: Mock user

    # Check if workspace exists
    workspace = next((w for w in WORKSPACES_STORAGE if w["id"] == workspace_id), None)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Check if user has permission (OWNER or ADMIN)
    check_workspace_permission(workspace_id, mock_user_id, [
        WorkspaceMemberRole.OWNER.value,
        WorkspaceMemberRole.ADMIN.value
    ])

    # TODO: In production, find user by email
    # For now, create mock user
    invited_user_id = str(uuid.uuid4())

    # Check if user is already a member
    existing_member = next(
        (m for m in WORKSPACE_MEMBERS_STORAGE
         if m["workspace_id"] == workspace_id and m["user_email"] == invite_data.email),
        None
    )
    if existing_member:
        raise HTTPException(status_code=400, detail="User is already a member of this workspace")

    # Create member
    member_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + "Z"

    member = {
        "id": member_id,
        "workspace_id": workspace_id,
        "user_id": invited_user_id,
        "user_email": invite_data.email,
        "user_name": None,
        "role": invite_data.role.value,
        "invited_by": mock_user_id,  # TESTING: Use mock user
        "invitation_accepted": False,  # Invitation requires acceptance
        "created_at": now,
        "updated_at": now
    }

    WORKSPACE_MEMBERS_STORAGE.append(member)

    return MemberResponse(**member)


@router.post("/{workspace_id}/members/{member_id}/accept", response_model=MemberResponse)
async def accept_invitation(
    workspace_id: str,
    member_id: str
    # TESTING: Auth disabled - current_user: User = Depends(get_current_user)
):
    """Accept a workspace invitation."""
    # Check if workspace exists
    workspace = next((w for w in WORKSPACES_STORAGE if w["id"] == workspace_id), None)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Find the member/invitation
    member = next(
        (m for m in WORKSPACE_MEMBERS_STORAGE
         if m["id"] == member_id and m["workspace_id"] == workspace_id),
        None
    )
    if not member:
        raise HTTPException(status_code=404, detail="Invitation not found")

    # Check if already accepted
    if member["invitation_accepted"]:
        raise HTTPException(status_code=400, detail="Invitation already accepted")

    # Accept the invitation
    member["invitation_accepted"] = True
    member["updated_at"] = datetime.utcnow().isoformat() + "Z"

    return MemberResponse(**member)


@router.delete("/{workspace_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    workspace_id: str,
    member_id: str
    # TESTING: Auth disabled - current_user: User = Depends(get_current_user)
):
    """Remove a member from the workspace."""
    mock_user_id = "test-user-309"  # TESTING: Mock user

    # Check if workspace exists
    workspace = next((w for w in WORKSPACES_STORAGE if w["id"] == workspace_id), None)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Find the member to remove
    member_to_remove = next(
        (m for m in WORKSPACE_MEMBERS_STORAGE
         if m["id"] == member_id and m["workspace_id"] == workspace_id),
        None
    )
    if not member_to_remove:
        raise HTTPException(status_code=404, detail="Member not found")

    # Check permissions
    user_role = get_user_role_in_workspace(workspace_id, mock_user_id)
    if not user_role:
        raise HTTPException(status_code=403, detail="You are not a member of this workspace")

    # Cannot remove the owner
    if member_to_remove["role"] == WorkspaceMemberRole.OWNER.value:
        raise HTTPException(status_code=400, detail="Cannot remove workspace owner")

    # Only OWNER or ADMIN can remove members
    if user_role not in [WorkspaceMemberRole.OWNER.value, WorkspaceMemberRole.ADMIN.value]:
        raise HTTPException(status_code=403, detail="You don't have permission to remove members")

    # Remove the member
    WORKSPACE_MEMBERS_STORAGE.remove(member_to_remove)

    return None


@router.patch("/{workspace_id}/members/{member_id}/role", response_model=MemberResponse)
async def update_member_role(
    workspace_id: str,
    member_id: str,
    role_update: MemberRoleUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a member's role in the workspace."""
    # Check if workspace exists
    workspace = next((w for w in WORKSPACES_STORAGE if w["id"] == workspace_id), None)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Find the member
    member = next(
        (m for m in WORKSPACE_MEMBERS_STORAGE
         if m["id"] == member_id and m["workspace_id"] == workspace_id),
        None
    )
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    # Only OWNER can change roles
    check_workspace_permission(workspace_id, str(current_user.id), [WorkspaceMemberRole.OWNER.value])

    # Cannot change owner role
    if member["role"] == WorkspaceMemberRole.OWNER.value:
        raise HTTPException(status_code=400, detail="Cannot change owner role")

    # Update role
    member["role"] = role_update.role.value
    member["updated_at"] = datetime.utcnow().isoformat() + "Z"

    return MemberResponse(**member)


@router.post("/{workspace_id}/transfer-ownership", response_model=WorkspaceResponse)
async def transfer_ownership(
    workspace_id: str,
    transfer_data: OwnershipTransfer
    # TESTING: Auth disabled - current_user: User = Depends(get_current_user)
):
    """Transfer workspace ownership to another member."""
    mock_user_id = "test-user-309"  # TESTING: Mock user (current owner)

    # Check if workspace exists
    workspace = next((w for w in WORKSPACES_STORAGE if w["id"] == workspace_id), None)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Only current OWNER can transfer ownership
    check_workspace_permission(workspace_id, mock_user_id, [WorkspaceMemberRole.OWNER.value])

    # Verify new owner is a member of the workspace
    new_owner_member = next(
        (m for m in WORKSPACE_MEMBERS_STORAGE
         if m["workspace_id"] == workspace_id and m["user_id"] == transfer_data.new_owner_user_id),
        None
    )
    if not new_owner_member:
        raise HTTPException(
            status_code=400,
            detail="New owner must be a member of the workspace"
        )

    # Cannot transfer to yourself
    if transfer_data.new_owner_user_id == mock_user_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot transfer ownership to yourself"
        )

    # Update workspace owner
    workspace["owner_id"] = transfer_data.new_owner_user_id
    workspace["updated_at"] = datetime.utcnow().isoformat() + "Z"

    # Update old owner's role to ADMIN
    old_owner_member = next(
        (m for m in WORKSPACE_MEMBERS_STORAGE
         if m["workspace_id"] == workspace_id and m["user_id"] == mock_user_id),
        None
    )
    if old_owner_member:
        old_owner_member["role"] = WorkspaceMemberRole.ADMIN.value
        old_owner_member["updated_at"] = datetime.utcnow().isoformat() + "Z"

    # Update new owner's role to OWNER
    new_owner_member["role"] = WorkspaceMemberRole.OWNER.value
    new_owner_member["updated_at"] = datetime.utcnow().isoformat() + "Z"

    # Calculate member count
    member_count = len([m for m in WORKSPACE_MEMBERS_STORAGE if m["workspace_id"] == workspace_id])

    # Get current user's role (now ADMIN)
    current_user_role = get_user_role_in_workspace(workspace_id, mock_user_id) or "none"

    return WorkspaceResponse(
        id=workspace["id"],
        name=workspace["name"],
        description=workspace.get("description"),
        owner_id=workspace["owner_id"],
        is_active=workspace["is_active"],
        created_at=workspace["created_at"],
        updated_at=workspace["updated_at"],
        member_count=member_count,
        current_user_role=current_user_role
    )
