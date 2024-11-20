from typing import List, Optional

class Task:
    """
    A class to represent a task.

    :param name: The name of the task.
    :type name: str
    :param description: The description of the task.
    :type description: str
    :raises ValueError: If the task name is empty.

    :Example:

    >>> task = Task(name="Buy groceries", description="Buy milk and eggs")
    >>> task.name
    'Buy groceries'
    >>> task.description
    'Buy milk and eggs'
    """

    def __init__(self, name: str, description: str):
        if not name:
            raise ValueError("Task name cannot be empty")
        self.id = id(self)
        self.name = name
        self.description = description

    def __eq__(self, other):
        """
        Check if two tasks are equal based on their IDs.

        :param other: The other task to compare.
        :type other: Task
        :return: True if the tasks are equal, False otherwise.
        :rtype: bool
        """
        return self.id == other.id

    def __repr__(self):
        """
        Return a string representation of the task.

        :return: A string representation of the task.
        :rtype: str
        """
        return f"Task(id={self.id}, name={self.name}, description={self.description})"

class TaskManager:
    """
    A class to manage tasks.

    :Example:

    >>> manager = TaskManager()
    >>> task = Task(name="Buy groceries", description="Buy milk and eggs")
    >>> manager.create_task(task)
    "Task 'Buy groceries' added."
    """

    def __init__(self):
        """
        Initialize the task manager with an empty list of tasks.
        """
        self.tasks: List[Task] = []

    def create_task(self, task: Task) -> str:
        """
        Add a new task to the task manager.

        :param task: The task to add.
        :type task: Task
        :return: A message indicating the task was added.
        :rtype: str
        """
        try:
            self.tasks.append(task)
            return f"Task '{task.name}' added."
        except ValueError as e:
            return str(e)

    def get_task(self, task_id: int) -> Optional[Task]:
        """
        Retrieve a task by its ID.

        :param task_id: The ID of the task to retrieve.
        :type task_id: int
        :return: The task with the specified ID, or None if not found.
        :rtype: Optional[Task]
        """
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def update_task(self, task: Task) -> str:
        """
        Update an existing task.

        :param task: The task to update.
        :type task: Task
        :return: A message indicating the task was updated, or not found.
        :rtype: str
        """
        for i, t in enumerate(self.tasks):
            if t.id == task.id:
                self.tasks[i] = task
                return f"Task '{task.name}' updated."
        return "Task not found."

    def delete_task(self, task_id: int) -> str:
        """
        Delete a task by its ID.

        :param task_id: The ID of the task to delete.
        :type task_id: int
        :return: A message indicating the task was removed, or not found.
        :rtype: str
        """
        task = self.get_task(task_id)
        if task:
            self.tasks.remove(task)
            return f"Task '{task.name}' removed."
        else:
            return "Task not found."

    def list_tasks(self) -> List[Task]:
        """
        List all tasks in the task manager.

        :return: A list of all tasks.
        :rtype: List[Task]
        """
        return self.tasks

# Example usage
if __name__ == "__main__":
    manager = TaskManager()
    task1 = Task(name="Buy groceries", description="Buy milk and eggs")
    task2 = Task(name="Read a book", description="Read '1984' by George Orwell")

    print(manager.create_task(task1))
    print(manager.create_task(task2))
    print(manager.list_tasks())