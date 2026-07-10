"""
Analytics Service - Tracks and reports on task statistics
BUG: Contains multiple logic errors!
"""
from datetime import datetime, timedelta
from typing import Optional

class AnalyticsService:
    def __init__(self):
        self.task_data = []

    def calculate_average_completion_time(self, tasks):
        """Calculate average task completion time"""
        # BUG 1: Doesn't check for empty list
        total_time = sum([t.get('duration', 0) for t in tasks])
        return total_time / len(tasks)

    def get_productivity_score(self, completed_tasks: int, total_tasks: int):
        """Calculate productivity score"""
        # BUG 2: No check for division by zero
        score = (completed_tasks / total_tasks) * 100
        return score

    def filter_tasks_by_date(self, tasks, start_date, end_date):
        """Filter tasks within date range"""
        # BUG 3: Comparing string with datetime objects
        filtered = []
        for task in tasks:
            task_date = task.get('created_at')
            if start_date <= task_date <= end_date:
                filtered.append(task)
        return filtered

    def get_top_performers(self, user_tasks: dict, top_n: int = 5):
        """Get top N performing users"""
        # BUG 4: Doesn't handle negative top_n
        # BUG 5: Doesn't handle empty dict
        sorted_users = sorted(user_tasks.items(), key=lambda x: x[1], reverse=True)
        return sorted_users[:top_n]

    def predict_completion_date(self, remaining_tasks: int, daily_rate: float):
        """Predict when all tasks will be completed"""
        # BUG 6: No handling for zero or negative daily_rate
        days_needed = remaining_tasks / daily_rate
        completion_date = datetime.now() + timedelta(days=days_needed)
        return completion_date.strftime('%Y-%m-%d')

    def export_report(self, data: list, format: str):
        """Export analytics report"""
        # BUG 7: Hardcoded format, ignores format parameter
        report = str(data)
        return report
