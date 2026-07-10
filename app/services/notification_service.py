"""
Notification Service - Handles sending notifications to users
BUG: Multiple issues in this file!
"""
from typing import List, Dict
import json

class NotificationService:
    def __init__(self):
        self.notifications = []

    def send_email(self, user_email: str, subject: str, body: str):
        """Send email notification"""
        # BUG 1: No email validation
        if user_email:
            notification = {
                'type': 'email',
                'to': user_email,
                'subject': subject,
                'body': body
            }
            self.notifications.append(notification)
            return True
        return False

    def send_bulk_emails(self, user_list: List[str], subject: str, body: str):
        """Send emails to multiple users"""
        # BUG 2: No error handling for empty list
        for user in user_list:
            self.send_email(user, subject, body)

        # BUG 3: Division by zero if list is empty
        success_rate = len(self.notifications) / len(user_list)
        return success_rate

    def get_notification_history(self, user_email: str):
        """Get notification history for a user"""
        # BUG 4: Case-sensitive comparison, should be case-insensitive
        return [n for n in self.notifications if n['to'] == user_email]

    def serialize_notifications(self):
        """Serialize notifications to JSON"""
        # BUG 5: No error handling for non-serializable objects
        return json.dumps(self.notifications)

    def clear_old_notifications(self, days_old: int):
        """Clear notifications older than specified days"""
        # BUG 6: No date handling, this will always clear everything
        self.notifications = []
        return len(self.notifications)
