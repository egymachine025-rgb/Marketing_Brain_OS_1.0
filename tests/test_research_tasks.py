"""
Tests for Research Tasks Management
"""

import os
import json
import tempfile
import shutil
import unittest
from datetime import datetime

from src.research.research_tasks import (
    ResearchTask,
    ResearchTaskManager,
    TaskStatus,
    TaskPriority
)


class TestResearchTask(unittest.TestCase):
    """Test ResearchTask dataclass."""

    def test_task_creation(self):
        """Test creating a research task."""
        task = ResearchTask(
            task_id="test-123",
            title="Test Task",
            description="Test description",
            category="keywords",
            suggested_tools=["google_trends"],
            steps=["Step 1", "Step 2"],
            expected_results={"keywords": []}
        )
        
        self.assertEqual(task.task_id, "test-123")
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.status, TaskStatus.PENDING.value)
        self.assertIsNotNone(task.created_at)
        self.assertIsNotNone(task.updated_at)

    def test_task_to_dict(self):
        """Test converting task to dictionary."""
        task = ResearchTask(
            task_id="test-123",
            title="Test Task",
            description="Test description",
            category="keywords",
            suggested_tools=["google_trends"],
            steps=["Step 1"],
            expected_results={"keywords": []}
        )
        
        task_dict = task.to_dict()
        self.assertIsInstance(task_dict, dict)
        self.assertEqual(task_dict["task_id"], "test-123")
        self.assertEqual(task_dict["title"], "Test Task")

    def test_task_from_dict(self):
        """Test creating task from dictionary."""
        task_dict = {
            "task_id": "test-123",
            "title": "Test Task",
            "description": "Test description",
            "category": "keywords",
            "suggested_tools": ["google_trends"],
            "steps": ["Step 1"],
            "expected_results": {"keywords": []},
            "status": "pending",
            "priority": "medium",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "completed_at": None,
            "assigned_to": None,
            "notes": None,
            "tags": [],
            "brand": None,
            "product_id": None
        }
        
        task = ResearchTask.from_dict(task_dict)
        self.assertEqual(task.task_id, "test-123")
        self.assertEqual(task.title, "Test Task")


class TestResearchTaskManager(unittest.TestCase):
    """Test ResearchTaskManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = ResearchTaskManager(data_dir=self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_create_task(self):
        """Test creating a new task."""
        task = self.manager.create_task(
            title="Test Task",
            description="Test description",
            category="keywords",
            suggested_tools=["google_trends"],
            steps=["Step 1"],
            expected_results={"keywords": []}
        )
        
        self.assertIsNotNone(task.task_id)
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.status, TaskStatus.PENDING.value)

    def test_get_task(self):
        """Test retrieving a task by ID."""
        task = self.manager.create_task(
            title="Test Task",
            description="Test description",
            category="keywords",
            suggested_tools=["google_trends"],
            steps=["Step 1"],
            expected_results={"keywords": []}
        )
        
        retrieved = self.manager.get_task(task.task_id)
        self.assertEqual(retrieved.task_id, task.task_id)
        self.assertEqual(retrieved.title, "Test Task")

    def test_get_nonexistent_task(self):
        """Test retrieving a non-existent task."""
        retrieved = self.manager.get_task("nonexistent-id")
        self.assertIsNone(retrieved)

    def test_list_tasks(self):
        """Test listing all tasks."""
        task1 = self.manager.create_task(
            title="Task 1",
            description="Description 1",
            category="keywords",
            suggested_tools=["google_trends"],
            steps=["Step 1"],
            expected_results={"keywords": []}
        )
        
        task2 = self.manager.create_task(
            title="Task 2",
            description="Description 2",
            category="competitors",
            suggested_tools=["similarweb"],
            steps=["Step 1"],
            expected_results={"competitors": []}
        )
        
        tasks = self.manager.list_tasks()
        self.assertEqual(len(tasks), 2)

    def test_list_tasks_with_filter(self):
        """Test listing tasks with category filter."""
        self.manager.create_task(
            title="Task 1",
            description="Description 1",
            category="keywords",
            suggested_tools=["google_trends"],
            steps=["Step 1"],
            expected_results={"keywords": []}
        )
        
        self.manager.create_task(
            title="Task 2",
            description="Description 2",
            category="competitors",
            suggested_tools=["similarweb"],
            steps=["Step 1"],
            expected_results={"competitors": []}
        )
        
        keyword_tasks = self.manager.list_tasks(category="keywords")
        self.assertEqual(len(keyword_tasks), 1)
        self.assertEqual(keyword_tasks[0].category, "keywords")

    def test_complete_task(self):
        """Test marking a task as completed."""
        task = self.manager.create_task(
            title="Test Task",
            description="Test description",
            category="keywords",
            suggested_tools=["google_trends"],
            steps=["Step 1"],
            expected_results={"keywords": []}
        )
        
        completed = self.manager.complete_task(task.task_id, notes="Done!")
        self.assertEqual(completed.status, TaskStatus.COMPLETED.value)
        self.assertIsNotNone(completed.completed_at)
        self.assertEqual(completed.notes, "Done!")

    def test_update_task(self):
        """Test updating a task."""
        task = self.manager.create_task(
            title="Test Task",
            description="Test description",
            category="keywords",
            suggested_tools=["google_trends"],
            steps=["Step 1"],
            expected_results={"keywords": []}
        )
        
        updated = self.manager.update_task(
            task.task_id,
            title="Updated Title",
            status=TaskStatus.IN_PROGRESS.value
        )
        
        self.assertEqual(updated.title, "Updated Title")
        self.assertEqual(updated.status, TaskStatus.IN_PROGRESS.value)

    def test_delete_task(self):
        """Test deleting a task."""
        task = self.manager.create_task(
            title="Test Task",
            description="Test description",
            category="keywords",
            suggested_tools=["google_trends"],
            steps=["Step 1"],
            expected_results={"keywords": []}
        )
        
        success = self.manager.delete_task(task.task_id)
        self.assertTrue(success)
        
        retrieved = self.manager.get_task(task.task_id)
        self.assertIsNone(retrieved)

    def test_delete_nonexistent_task(self):
        """Test deleting a non-existent task."""
        success = self.manager.delete_task("nonexistent-id")
        self.assertFalse(success)

    def test_get_statistics(self):
        """Test getting task statistics."""
        self.manager.create_task(
            title="Task 1",
            description="Description 1",
            category="keywords",
            suggested_tools=["google_trends"],
            steps=["Step 1"],
            expected_results={"keywords": []}
        )
        
        self.manager.create_task(
            title="Task 2",
            description="Description 2",
            category="competitors",
            suggested_tools=["similarweb"],
            steps=["Step 1"],
            expected_results={"competitors": []}
        )
        
        stats = self.manager.get_statistics()
        self.assertEqual(stats["total"], 2)
        self.assertEqual(stats["by_category"]["keywords"], 1)
        self.assertEqual(stats["by_category"]["competitors"], 1)

    def test_persistence(self):
        """Test that tasks persist across manager instances."""
        task = self.manager.create_task(
            title="Test Task",
            description="Test description",
            category="keywords",
            suggested_tools=["google_trends"],
            steps=["Step 1"],
            expected_results={"keywords": []}
        )
        
        # Create new manager with same directory
        new_manager = ResearchTaskManager(data_dir=self.temp_dir)
        retrieved = new_manager.get_task(task.task_id)
        
        self.assertEqual(retrieved.task_id, task.task_id)
        self.assertEqual(retrieved.title, task.title)

    def test_task_with_brand_and_product(self):
        """Test creating task with brand and product associations."""
        task = self.manager.create_task(
            title="Brand Research",
            description="Research for Nike",
            category="keywords",
            suggested_tools=["google_trends"],
            steps=["Step 1"],
            expected_results={"keywords": []},
            brand="Nike",
            product_id="prod-123"
        )
        
        self.assertEqual(task.brand, "Nike")
        self.assertEqual(task.product_id, "prod-123")

    def test_task_with_tags(self):
        """Test creating task with tags."""
        task = self.manager.create_task(
            title="Tagged Task",
            description="Task with tags",
            category="keywords",
            suggested_tools=["google_trends"],
            steps=["Step 1"],
            expected_results={"keywords": []},
            tags=["fashion", "egypt"]
        )
        
        self.assertIn("fashion", task.tags)
        self.assertIn("egypt", task.tags)

    def test_filter_by_tags(self):
        """Test filtering tasks by tags."""
        self.manager.create_task(
            title="Task 1",
            description="Description 1",
            category="keywords",
            suggested_tools=["google_trends"],
            steps=["Step 1"],
            expected_results={"keywords": []},
            tags=["fashion", "egypt"]
        )
        
        self.manager.create_task(
            title="Task 2",
            description="Description 2",
            category="keywords",
            suggested_tools=["google_trends"],
            steps=["Step 1"],
            expected_results={"keywords": []},
            tags=["electronics"]
        )
        
        fashion_tasks = self.manager.list_tasks(tags=["fashion"])
        self.assertEqual(len(fashion_tasks), 1)
        
        both_tags = self.manager.list_tasks(tags=["fashion", "egypt"])
        self.assertEqual(len(both_tags), 1)


if __name__ == "__main__":
    unittest.main()
