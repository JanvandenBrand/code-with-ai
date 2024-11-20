import pytest
from src.tasks import TaskManager, Task

@pytest.fixture
def task_manager():
    return TaskManager()

def test_create_task(task_manager):
    """
    Objective: Ensure that tasks can be created successfully.
    """
    task = Task(name="Test Task", description="This is a test task")
    
    task_manager.create_task(task)
    created_task = task_manager.get_task(task.id)
    
    assert created_task == task

def test_get_task(task_manager):
    """
    Objective: Ensure that tasks can be retrieved successfully.
    """
    task = Task(name="Test Task", description="This is a test task")
    task_manager.create_task(task)
    
    retrieved_task = task_manager.get_task(task.id)
    
    assert retrieved_task == task

def test_update_task(task_manager):
    """
    Objective: Ensure that tasks can be updated successfully.
    """
    task = Task(name="Test Task", description="This is a test task")
    task_manager.create_task(task)
    task.name = "Updated Task"
    
    task_manager.update_task(task)
    updated_task = task_manager.get_task(task.id)
    
    assert updated_task.name == "Updated Task"

def test_delete_task(task_manager):
    """
    Objective: Ensure that tasks can be deleted successfully.
    """
    task = Task(name="Test Task", description="This is a test task")
    task_manager.create_task(task)
    
    task_manager.delete_task(task.id)
    deleted_task = task_manager.get_task(task.id)
    
    assert deleted_task is None

def test_create_task_invalid():
    """
    Objective: Ensure that the system handles invalid task creation gracefully.
    """
    invalid_task_name = ""
    invalid_task_description = "This is a test task"
    
    with pytest.raises(ValueError, match="Task name cannot be empty"):
        Task(name=invalid_task_name, description=invalid_task_description)

def test_get_non_existent_task(task_manager):
    """
    Objective: Ensure that the system handles retrieval of non-existent tasks gracefully.
    """
    non_existent_task_id = 999
    
    retrieved_task = task_manager.get_task(non_existent_task_id)

    assert retrieved_task is None
