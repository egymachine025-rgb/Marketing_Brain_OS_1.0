"""
Research Tasks Management for Marketing Brain OS

This module manages research tasks including creation, tracking, and completion.
Tasks are stored in data/research/tasks.json
"""

import os
import json
import uuid
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from enum import Enum


class TaskStatus(Enum):
    """Research task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Research task priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class ResearchTask:
    """Dataclass representing a research task."""
    task_id: str
    title: str
    description: str
    category: str  # keywords, social_media, competitors, market_research
    suggested_tools: List[str]
    steps: List[str]
    expected_results: Dict[str, Any]
    status: str = TaskStatus.PENDING.value
    priority: str = TaskPriority.MEDIUM.value
    created_at: str = None
    updated_at: str = None
    completed_at: str = None
    assigned_to: Optional[str] = None
    notes: Optional[str] = None
    tags: List[str] = None
    brand: Optional[str] = None
    product_id: Optional[str] = None

    def __post_init__(self):
        """Initialize timestamps if not provided."""
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat() + "Z"
        if self.updated_at is None:
            self.updated_at = self.created_at
        if self.tags is None:
            self.tags = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResearchTask':
        """Create from dictionary."""
        return cls(**data)


class ResearchTaskManager:
    """Manager for research tasks storage and operations."""

    def __init__(self, data_dir: str = None):
        """
        Initialize the task manager.
        
        Args:
            data_dir: Directory for storing tasks. Defaults to data/research
        """
        if data_dir is None:
            # Default to project root/data/research
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
            data_dir = os.path.join(project_root, "data", "research")
        
        self.data_dir = data_dir
        self.tasks_file = os.path.join(data_dir, "tasks.json")
        os.makedirs(data_dir, exist_ok=True)
        
        # Load existing tasks
        self._tasks: Dict[str, ResearchTask] = {}
        self._load_tasks()

    def _load_tasks(self):
        """Load tasks from JSON file."""
        if os.path.exists(self.tasks_file):
            try:
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for task_id, task_data in data.items():
                        self._tasks[task_id] = ResearchTask.from_dict(task_data)
            except Exception as e:
                print(f"Error loading tasks: {e}")
                self._tasks = {}

    def _save_tasks(self):
        """Save tasks to JSON file."""
        try:
            data = {task_id: task.to_dict() for task_id, task in self._tasks.items()}
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise RuntimeError(f"Error saving tasks: {e}")

    def create_task(
        self,
        title: str,
        description: str,
        category: str,
        suggested_tools: List[str],
        steps: List[str],
        expected_results: Dict[str, Any],
        priority: str = TaskPriority.MEDIUM.value,
        assigned_to: Optional[str] = None,
        tags: List[str] = None,
        brand: Optional[str] = None,
        product_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> ResearchTask:
        """
        Create a new research task.
        
        Args:
            title: Task title
            description: Task description
            category: Research category (keywords, social_media, competitors, market_research)
            suggested_tools: List of research tool IDs to use
            steps: Step-by-step instructions
            expected_results: Expected data structure for results
            priority: Task priority (low, medium, high, urgent)
            assigned_to: Who is assigned to this task
            tags: List of tags for filtering
            brand: Associated brand (if any)
            product_id: Associated product ID (if any)
            notes: Additional notes
            
        Returns:
            Created ResearchTask
        """
        task_id = str(uuid.uuid4())
        
        task = ResearchTask(
            task_id=task_id,
            title=title,
            description=description,
            category=category,
            suggested_tools=suggested_tools,
            steps=steps,
            expected_results=expected_results,
            priority=priority,
            assigned_to=assigned_to,
            tags=tags or [],
            brand=brand,
            product_id=product_id,
            notes=notes
        )
        
        self._tasks[task_id] = task
        self._save_tasks()
        return task

    def get_task(self, task_id: str) -> Optional[ResearchTask]:
        """
        Get a task by ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            ResearchTask or None if not found
        """
        return self._tasks.get(task_id)

    def list_tasks(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        brand: Optional[str] = None,
        product_id: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[ResearchTask]:
        """
        List tasks with optional filtering.
        
        Args:
            status: Filter by status
            category: Filter by category
            priority: Filter by priority
            brand: Filter by brand
            product_id: Filter by product ID
            tags: Filter by tags (must match all)
            
        Returns:
            List of filtered ResearchTask objects
        """
        tasks = list(self._tasks.values())
        
        if status:
            tasks = [t for t in tasks if t.status == status]
        if category:
            tasks = [t for t in tasks if t.category == category]
        if priority:
            tasks = [t for t in tasks if t.priority == priority]
        if brand:
            tasks = [t for t in tasks if t.brand == brand]
        if product_id:
            tasks = [t for t in tasks if t.product_id == product_id]
        if tags:
            tasks = [t for t in tasks if all(tag in t.tags for tag in tags)]
        
        # Sort by created_at (newest first)
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        return tasks

    def complete_task(self, task_id: str, notes: Optional[str] = None) -> Optional[ResearchTask]:
        """
        Mark a task as completed.
        
        Args:
            task_id: Task ID
            notes: Completion notes
            
        Returns:
            Updated ResearchTask or None if not found
        """
        task = self._tasks.get(task_id)
        if not task:
            return None
        
        task.status = TaskStatus.COMPLETED.value
        task.completed_at = datetime.utcnow().isoformat() + "Z"
        task.updated_at = task.completed_at
        if notes:
            task.notes = notes
        
        self._save_tasks()
        return task

    def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[str] = None,
        notes: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[ResearchTask]:
        """
        Update an existing task.
        
        Args:
            task_id: Task ID
            title: New title
            description: New description
            status: New status
            priority: New priority
            assigned_to: New assignee
            notes: New notes
            tags: New tags
            
        Returns:
            Updated ResearchTask or None if not found
        """
        task = self._tasks.get(task_id)
        if not task:
            return None
        
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if status is not None:
            task.status = status
        if priority is not None:
            task.priority = priority
        if assigned_to is not None:
            task.assigned_to = assigned_to
        if notes is not None:
            task.notes = notes
        if tags is not None:
            task.tags = tags
        
        task.updated_at = datetime.utcnow().isoformat() + "Z"
        self._save_tasks()
        return task

    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            True if deleted, False if not found
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            self._save_tasks()
            return True
        return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get task statistics.
        
        Returns:
            Dictionary with task statistics
        """
        total = len(self._tasks)
        by_status = {}
        by_category = {}
        by_priority = {}
        
        for task in self._tasks.values():
            by_status[task.status] = by_status.get(task.status, 0) + 1
            by_category[task.category] = by_category.get(task.category, 0) + 1
            by_priority[task.priority] = by_priority.get(task.priority, 0) + 1
        
        return {
            "total": total,
            "by_status": by_status,
            "by_category": by_category,
            "by_priority": by_priority
        }
