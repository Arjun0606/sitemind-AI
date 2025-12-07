"""
SiteMind Task Management Service
Live task assignment and tracking via WhatsApp

FEATURES:
- Create tasks via WhatsApp
- Assign to team members
- Status updates
- Due date tracking
- Photo proof of completion
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    VERIFIED = "verified"


class TaskPriority(str, Enum):
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


@dataclass
class Task:
    id: str
    project_id: str
    title: str
    description: str
    assigned_to: str  # phone number
    assigned_by: str
    status: TaskStatus
    priority: TaskPriority
    location: Optional[str] = None
    due_date: Optional[str] = None
    created_at: str = ""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    completion_photo: Optional[str] = None
    blockers: List[str] = field(default_factory=list)


class TaskManagementService:
    """
    Task management via WhatsApp
    """
    
    def __init__(self):
        self._tasks: Dict[str, List[Task]] = {}  # project_id -> tasks
        self._user_tasks: Dict[str, List[str]] = {}  # phone -> task_ids
    
    # =========================================================================
    # TASK CREATION
    # =========================================================================
    
    def create_task(
        self,
        project_id: str,
        title: str,
        assigned_to: str,
        assigned_by: str,
        description: str = "",
        location: str = None,
        due_date: str = None,
        priority: TaskPriority = TaskPriority.NORMAL,
    ) -> Task:
        """Create a new task"""
        task = Task(
            id=f"task_{datetime.utcnow().timestamp():.0f}",
            project_id=project_id,
            title=title,
            description=description,
            assigned_to=assigned_to,
            assigned_by=assigned_by,
            status=TaskStatus.PENDING,
            priority=priority,
            location=location,
            due_date=due_date,
            created_at=datetime.utcnow().isoformat(),
        )
        
        if project_id not in self._tasks:
            self._tasks[project_id] = []
        self._tasks[project_id].append(task)
        
        if assigned_to not in self._user_tasks:
            self._user_tasks[assigned_to] = []
        self._user_tasks[assigned_to].append(task.id)
        
        return task
    
    # =========================================================================
    # STATUS UPDATES
    # =========================================================================
    
    def start_task(self, task_id: str) -> Optional[Task]:
        """Mark task as in progress"""
        task = self._find_task(task_id)
        if task:
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.utcnow().isoformat()
        return task
    
    def complete_task(
        self,
        task_id: str,
        completion_photo: str = None,
    ) -> Optional[Task]:
        """Mark task as completed"""
        task = self._find_task(task_id)
        if task:
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow().isoformat()
            task.completion_photo = completion_photo
        return task
    
    def block_task(self, task_id: str, reason: str) -> Optional[Task]:
        """Mark task as blocked"""
        task = self._find_task(task_id)
        if task:
            task.status = TaskStatus.BLOCKED
            task.blockers.append(reason)
        return task
    
    def verify_task(self, task_id: str) -> Optional[Task]:
        """Verify completed task"""
        task = self._find_task(task_id)
        if task and task.status == TaskStatus.COMPLETED:
            task.status = TaskStatus.VERIFIED
        return task
    
    # =========================================================================
    # QUERIES
    # =========================================================================
    
    def get_user_tasks(
        self,
        user_phone: str,
        status: TaskStatus = None,
    ) -> List[Task]:
        """Get tasks for a user"""
        task_ids = self._user_tasks.get(user_phone, [])
        tasks = []
        
        for tid in task_ids:
            task = self._find_task(tid)
            if task:
                if status is None or task.status == status:
                    tasks.append(task)
        
        return sorted(tasks, key=lambda t: t.created_at, reverse=True)
    
    def get_project_tasks(
        self,
        project_id: str,
        status: TaskStatus = None,
    ) -> List[Task]:
        """Get all tasks for a project"""
        tasks = self._tasks.get(project_id, [])
        
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        return sorted(tasks, key=lambda t: t.created_at, reverse=True)
    
    def get_overdue_tasks(self, project_id: str) -> List[Task]:
        """Get overdue tasks"""
        tasks = self._tasks.get(project_id, [])
        now = datetime.utcnow().isoformat()
        
        return [
            t for t in tasks 
            if t.due_date and t.due_date < now and t.status not in [TaskStatus.COMPLETED, TaskStatus.VERIFIED]
        ]
    
    def _find_task(self, task_id: str) -> Optional[Task]:
        """Find task by ID"""
        for project_tasks in self._tasks.values():
            for task in project_tasks:
                if task.id == task_id:
                    return task
        return None
    
    # =========================================================================
    # FORMATTING
    # =========================================================================
    
    def format_task(self, task: Task) -> str:
        """Format task for WhatsApp"""
        status_icons = {
            TaskStatus.PENDING: "⏳",
            TaskStatus.IN_PROGRESS: "🔄",
            TaskStatus.BLOCKED: "🚫",
            TaskStatus.COMPLETED: "✅",
            TaskStatus.VERIFIED: "✓✓",
        }
        
        priority_icons = {
            TaskPriority.URGENT: "🔴",
            TaskPriority.HIGH: "🟠",
            TaskPriority.NORMAL: "🟢",
            TaskPriority.LOW: "⚪",
        }
        
        msg = f"{status_icons[task.status]} **{task.title}**\n"
        msg += f"Priority: {priority_icons[task.priority]} {task.priority.value}\n"
        
        if task.description:
            msg += f"Details: {task.description}\n"
        if task.location:
            msg += f"Location: {task.location}\n"
        if task.due_date:
            msg += f"Due: {task.due_date[:10]}\n"
        
        if task.blockers:
            msg += f"\n⚠️ Blocker: {task.blockers[-1]}"
        
        return msg
    
    def format_daily_summary(self, user_phone: str) -> str:
        """Format daily task summary for user"""
        tasks = self.get_user_tasks(user_phone)
        
        pending = [t for t in tasks if t.status == TaskStatus.PENDING]
        in_progress = [t for t in tasks if t.status == TaskStatus.IN_PROGRESS]
        blocked = [t for t in tasks if t.status == TaskStatus.BLOCKED]
        
        summary = "**Your Tasks**\n\n"
        
        if in_progress:
            summary += "🔄 **In Progress:**\n"
            for t in in_progress[:3]:
                summary += f"• {t.title}\n"
            summary += "\n"
        
        if pending:
            summary += "⏳ **Pending:**\n"
            for t in pending[:3]:
                summary += f"• {t.title}\n"
            summary += "\n"
        
        if blocked:
            summary += "🚫 **Blocked:**\n"
            for t in blocked[:2]:
                summary += f"• {t.title}: {t.blockers[-1] if t.blockers else 'Unknown'}\n"
            summary += "\n"
        
        if not tasks:
            summary += "No tasks assigned. Enjoy your day! 👍"
        
        return summary


# Singleton instance
task_management = TaskManagementService()
