"""
Admin Router - Administrative endpoints
BUG: Security and logic issues!
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List

router = APIRouter(prefix="/admin", tags=["admin"])

class AdminService:
    def __init__(self):
        self.admin_users = ["admin"]

    def is_admin(self, username: str):
        """Check if user is admin"""
        # BUG 1: Case-sensitive check, "Admin" won't work
        return username in self.admin_users

    def delete_user(self, user_id: int):
        """Delete a user"""
        # BUG 2: No validation if user exists
        # BUG 3: No check if deleting yourself
        return {"message": f"User {user_id} deleted"}

    def get_all_passwords(self):
        """Get all user passwords"""
        # BUG 4: SECURITY! Should never expose passwords
        passwords = ["password123", "admin123", "qwerty"]
        return passwords

    def update_user_role(self, user_id: int, role: str):
        """Update user role"""
        # BUG 5: No role validation
        # BUG 6: SQL injection vulnerable if used with raw SQL
        query = f"UPDATE users SET role='{role}' WHERE id={user_id}"
        return {"query": query}

    def bulk_delete_tasks(self, task_ids: List[int]):
        """Bulk delete tasks"""
        # BUG 7: No transaction handling
        # BUG 8: No permission check
        for task_id in task_ids:
            pass  # Would delete here
        return {"deleted": len(task_ids)}

admin_service = AdminService()

@router.get("/users/passwords")
async def get_passwords():
    """Get all passwords - DANGEROUS!"""
    # BUG 9: No authentication required!
    return admin_service.get_all_passwords()

@router.delete("/user/{user_id}")
async def delete_user(user_id: int):
    """Delete a user"""
    # BUG 10: No authentication or authorization
    return admin_service.delete_user(user_id)
