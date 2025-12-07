"""
SiteMind Task Management Service
Live task tracking via WhatsApp - no separate app needed

FEATURES:
1. Daily Work Checklists - PM assigns, engineers complete via WhatsApp
2. Task Status Updates - Real-time visibility for management
3. Blocker Reporting - Flag issues immediately
4. Completion Verification - Photo-based task completion
5. Timeline Tracking - Actual vs planned progress

HOW IT WORKS:
- PM creates tasks via dashboard or WhatsApp
- Engineers receive tasks on WhatsApp
- Engineers update status via WhatsApp: "B2 formwork done"
- AI logs completion with timestamp
- Management sees real-time progress
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field

from utils.logger import logger


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    VERIFIED = "verified"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


@dataclass
class Task:
    """A construction task"""
    task_id: str
    project_id: str
    title: str
    description: str
    location: str  # e.g., "Floor 3, Grid B2"
    assigned_to: List[str]  # Phone numbers
    created_by: str
    created_at: str
    due_date: str
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    verified_at: Optional[str] = None
    verified_by: Optional[str] = None
    blocker: Optional[str] = None
    completion_notes: Optional[str] = None
    completion_photos: List[str] = field(default_factory=list)
    checklist: List[Dict] = field(default_factory=list)  # [{item, completed}]
    dependencies: List[str] = field(default_factory=list)  # task_ids


class TaskManagementService:
    """
    Construction task management via WhatsApp
    """
    
    def __init__(self):
        self._tasks: Dict[str, List[Task]] = {}
        self._user_tasks: Dict[str, List[str]] = {}  # phone -> [task_ids]
    
    # =========================================================================
    # TASK CREATION
    # =========================================================================
    
    def create_task(
        self,
        project_id: str,
        title: str,
        description: str,
        location: str,
        assigned_to: List[str],
        created_by: str,
        due_date: str,
        priority: TaskPriority = TaskPriority.NORMAL,
        checklist: List[str] = None,
        dependencies: List[str] = None,
    ) -> Task:
        """
        Create a new task
        
        Can be created via dashboard or WhatsApp command
        """
        task = Task(
            task_id=f"task_{int(datetime.utcnow().timestamp() * 1000)}",
            project_id=project_id,
            title=title,
            description=description,
            location=location,
            assigned_to=assigned_to,
            created_by=created_by,
            created_at=datetime.utcnow().isoformat(),
            due_date=due_date,
            priority=priority,
            checklist=[{"item": item, "completed": False} for item in (checklist or [])],
            dependencies=dependencies or [],
        )
        
        if project_id not in self._tasks:
            self._tasks[project_id] = []
        
        self._tasks[project_id].append(task)
        
        # Track by user
        for phone in assigned_to:
            if phone not in self._user_tasks:
                self._user_tasks[phone] = []
            self._user_tasks[phone].append(task.task_id)
        
        logger.info(f"📋 Task created: {title} → {len(assigned_to)} assignees")
        
        return task
    
    def create_daily_checklist(
        self,
        project_id: str,
        date: str,
        tasks: List[Dict],  # [{title, location, assigned_to, checklist}]
        created_by: str,
    ) -> List[Task]:
        """
        Create a daily checklist of tasks
        
        Useful for PM to assign morning work
        """
        created_tasks = []
        
        for task_data in tasks:
            task = self.create_task(
                project_id=project_id,
                title=task_data["title"],
                description=task_data.get("description", ""),
                location=task_data.get("location", ""),
                assigned_to=task_data.get("assigned_to", []),
                created_by=created_by,
                due_date=date,
                checklist=task_data.get("checklist", []),
            )
            created_tasks.append(task)
        
        return created_tasks
    
    # =========================================================================
    # TASK UPDATES (Via WhatsApp)
    # =========================================================================
    
    def start_task(self, task_id: str, started_by: str) -> bool:
        """Mark task as started"""
        task = self._find_task(task_id)
        if task and task.status == TaskStatus.PENDING:
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.utcnow().isoformat()
            logger.info(f"▶️ Task started: {task.title}")
            return True
        return False
    
    def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        updated_by: str,
        notes: str = None,
    ) -> bool:
        """Update task status"""
        task = self._find_task(task_id)
        if task:
            task.status = status
            
            if status == TaskStatus.IN_PROGRESS and not task.started_at:
                task.started_at = datetime.utcnow().isoformat()
            elif status == TaskStatus.COMPLETED:
                task.completed_at = datetime.utcnow().isoformat()
                task.completion_notes = notes
            
            logger.info(f"📋 Task updated: {task.title} → {status.value}")
            return True
        return False
    
    def complete_task(
        self,
        task_id: str,
        completed_by: str,
        notes: str = None,
        photo_urls: List[str] = None,
    ) -> bool:
        """Mark task as completed"""
        task = self._find_task(task_id)
        if task:
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow().isoformat()
            task.completion_notes = notes
            if photo_urls:
                task.completion_photos.extend(photo_urls)
            
            logger.info(f"✅ Task completed: {task.title}")
            return True
        return False
    
    def verify_task(
        self,
        task_id: str,
        verified_by: str,
        approved: bool,
        notes: str = None,
    ) -> bool:
        """Verify a completed task"""
        task = self._find_task(task_id)
        if task and task.status == TaskStatus.COMPLETED:
            if approved:
                task.status = TaskStatus.VERIFIED
                task.verified_at = datetime.utcnow().isoformat()
                task.verified_by = verified_by
                logger.info(f"✓ Task verified: {task.title}")
            else:
                task.status = TaskStatus.IN_PROGRESS  # Send back
                task.blocker = notes or "Verification failed"
                logger.info(f"↩️ Task sent back: {task.title}")
            return True
        return False
    
    def report_blocker(
        self,
        task_id: str,
        reported_by: str,
        blocker_description: str,
    ) -> bool:
        """Report a blocker on a task"""
        task = self._find_task(task_id)
        if task:
            task.status = TaskStatus.BLOCKED
            task.blocker = blocker_description
            logger.warning(f"🚫 Task blocked: {task.title} - {blocker_description}")
            return True
        return False
    
    def complete_checklist_item(
        self,
        task_id: str,
        item_index: int,
        completed_by: str,
    ) -> bool:
        """Complete a checklist item"""
        task = self._find_task(task_id)
        if task and 0 <= item_index < len(task.checklist):
            task.checklist[item_index]["completed"] = True
            task.checklist[item_index]["completed_by"] = completed_by
            task.checklist[item_index]["completed_at"] = datetime.utcnow().isoformat()
            
            # Check if all items complete
            if all(item["completed"] for item in task.checklist):
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.utcnow().isoformat()
            
            return True
        return False
    
    # =========================================================================
    # QUERIES
    # =========================================================================
    
    def get_user_tasks(
        self,
        phone: str,
        status_filter: TaskStatus = None,
    ) -> List[Task]:
        """Get tasks assigned to a user"""
        task_ids = self._user_tasks.get(phone, [])
        tasks = []
        
        for project_tasks in self._tasks.values():
            for task in project_tasks:
                if task.task_id in task_ids:
                    if status_filter is None or task.status == status_filter:
                        tasks.append(task)
        
        return tasks
    
    def get_project_tasks(
        self,
        project_id: str,
        status_filter: TaskStatus = None,
        date_filter: str = None,
    ) -> List[Task]:
        """Get tasks for a project"""
        tasks = self._tasks.get(project_id, [])
        
        if status_filter:
            tasks = [t for t in tasks if t.status == status_filter]
        
        if date_filter:
            tasks = [t for t in tasks if t.due_date == date_filter]
        
        return tasks
    
    def get_blocked_tasks(self, project_id: str) -> List[Task]:
        """Get blocked tasks that need attention"""
        return self.get_project_tasks(project_id, TaskStatus.BLOCKED)
    
    def get_overdue_tasks(self, project_id: str) -> List[Task]:
        """Get overdue tasks"""
        today = datetime.utcnow().date().isoformat()
        tasks = self._tasks.get(project_id, [])
        
        return [t for t in tasks 
                if t.due_date < today 
                and t.status not in [TaskStatus.COMPLETED, TaskStatus.VERIFIED, TaskStatus.CANCELLED]]
    
    def _find_task(self, task_id: str) -> Optional[Task]:
        """Find a task by ID"""
        for project_tasks in self._tasks.values():
            for task in project_tasks:
                if task.task_id == task_id:
                    return task
        return None
    
    # =========================================================================
    # WHATSAPP INTEGRATION
    # =========================================================================
    
    def format_task_for_whatsapp(self, task: Task) -> str:
        """Format task for WhatsApp display"""
        status_emoji = {
            TaskStatus.PENDING: "⏳",
            TaskStatus.IN_PROGRESS: "🔄",
            TaskStatus.BLOCKED: "🚫",
            TaskStatus.COMPLETED: "✅",
            TaskStatus.VERIFIED: "✓",
        }
        
        msg = f"""**{status_emoji.get(task.status, '📋')} {task.title}**

📍 Location: {task.location}
📅 Due: {task.due_date}
⚡ Priority: {task.priority.value}
Status: {task.status.value}
"""
        
        if task.checklist:
            msg += "\n**Checklist:**\n"
            for i, item in enumerate(task.checklist):
                check = "✓" if item["completed"] else "○"
                msg += f"  {check} {item['item']}\n"
        
        if task.blocker:
            msg += f"\n🚫 Blocker: {task.blocker}"
        
        msg += "\n\n_Reply with status update or 'done' when complete_"
        
        return msg
    
    def format_daily_summary(self, phone: str) -> str:
        """Format daily task summary for a user"""
        tasks = self.get_user_tasks(phone)
        
        if not tasks:
            return "No tasks assigned for today."
        
        pending = [t for t in tasks if t.status == TaskStatus.PENDING]
        in_progress = [t for t in tasks if t.status == TaskStatus.IN_PROGRESS]
        completed = [t for t in tasks if t.status in [TaskStatus.COMPLETED, TaskStatus.VERIFIED]]
        blocked = [t for t in tasks if t.status == TaskStatus.BLOCKED]
        
        msg = f"""**Your Tasks Today**

Pending: {len(pending)}
In Progress: {len(in_progress)}
Completed: {len(completed)}
Blocked: {len(blocked)}
"""
        
        if pending:
            msg += "\n**To Do:**\n"
            for t in pending[:5]:
                msg += f"• {t.title} ({t.location})\n"
        
        if blocked:
            msg += "\n**⚠️ Blocked:**\n"
            for t in blocked:
                msg += f"• {t.title}: {t.blocker}\n"
        
        return msg
    
    # =========================================================================
    # REPORTS
    # =========================================================================
    
    def generate_daily_report(self, project_id: str, date: str = None) -> str:
        """Generate daily task completion report"""
        if not date:
            date = datetime.utcnow().date().isoformat()
        
        tasks = self.get_project_tasks(project_id, date_filter=date)
        
        total = len(tasks)
        completed = len([t for t in tasks if t.status in [TaskStatus.COMPLETED, TaskStatus.VERIFIED]])
        blocked = len([t for t in tasks if t.status == TaskStatus.BLOCKED])
        
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        report = f"""
**Daily Task Report - {date}**

Total Tasks: {total}
Completed: {completed}
Blocked: {blocked}
Completion Rate: {completion_rate:.1f}%

"""
        
        if blocked > 0:
            report += "**Blocked Tasks:**\n"
            for t in self.get_blocked_tasks(project_id):
                report += f"• {t.title}: {t.blocker}\n"
        
        return report


# Singleton instance
task_management = TaskManagementService()

