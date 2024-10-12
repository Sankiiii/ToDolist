import sys
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QListWidget, QMessageBox, QDateTimeEdit, QComboBox, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette,QIcon

class Node:
    def __init__(self, task, due_date, priority, status):
        self.task = task
        self.due_date = due_date
        self.priority = priority
        self.status = status
        self.prev = self.next = None

class DoublyLinkedList:
    def __init__(self):
        self.head = self.tail = None

    def add_task(self, task, due_date, priority):
        new_node = Node(task, due_date, priority, "Pending")
        if not self.head:
            self.head = self.tail = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node

    def delete_task(self, task_name):
        current = self.head
        while current:
            if current.task == task_name:
                if current == self.head:
                    self.head = current.next
                    if self.head:
                        self.head.prev = None
                elif current == self.tail:
                    self.tail = current.prev
                    self.tail.next = None
                else:
                    current.prev.next = current.next
                    current.next.prev = current.prev
                return current
            current = current.next
        return None

    def mark_complete(self, task_name):
        current = self.head
        while current:
            if current.task == task_name:
                current.status = "Completed"
                return True
            current = current.next
        return False

    def display_tasks(self):
        return [{"task": node.task, "due_date": node.due_date, "priority": node.priority, "status": node.status}
                for node in self]

    def __iter__(self):
        current = self.head
        while current:
            yield current
            current = current.next

    def sort_tasks_by_due_date(self):
        tasks = sorted(self.display_tasks(), key=lambda x: datetime.strptime(x["due_date"], "%Y-%m-%d %H:%M:%S"))
        self.__init__()
        for task in tasks:
            self.add_task(task["task"], task["due_date"], task["priority"])

class Stack:
    def __init__(self):
        self.stack = []

    def push(self, task):
        self.stack.append(task)

    def pop(self):
        return self.stack.pop() if self.stack else None

class Queue:
    def __init__(self):
        self.queue = []

    def enqueue(self, task):
        self.queue.append(task)

    def dequeue(self):
        return self.queue.pop(0) if self.queue else None

class TodoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.task_list = DoublyLinkedList()
        self.undo_stack = Stack()
        self.urgent_task_queue = Queue()
        self.init_ui()

    def init_ui(self):
        self.setWindowIcon(QIcon(r"TODOLOGO.png"))
        self.setWindowTitle("To Do List")
        self.setGeometry(400, 200, 800, 700)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
            }
            QLineEdit, QDateTimeEdit, QComboBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: white;
            }
            QPushButton {
                padding: 5px 10px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: white;
            }
            QLabel {
                font-weight: bold;
                color: #333;
            }
        """)

        layout = QVBoxLayout()

        input_layout = QHBoxLayout()
        self.task_input = QLineEdit(placeholderText="Enter a task...")
        # self.due_date_input = QDateTimeEdit(datetime=datetime.now(), displayFormat="yyyy-MM-dd")
        # self.due_date_input = QDateTimeEdit( displayFormat="yyyy-MM-dd")
        self.due_date_input = QDateTimeEdit(self)
        self.due_date_input.setDisplayFormat("yyyy-MM-dd")
        self.due_date_input.setDateTime(datetime.now())
        
        self.priority_input = QComboBox()
        self.priority_input.addItems(["Low", "Medium", "High"])
        input_layout.addWidget(self.task_input)
        input_layout.addWidget(self.due_date_input)
        input_layout.addWidget(self.priority_input)

        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Task")
        self.delete_button = QPushButton("Delete Task")
        self.undo_button = QPushButton("Undo Delete")
        self.complete_button = QPushButton("Mark as Complete")
        self.sort_button = QPushButton("Sort by Due Date")
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(self.undo_button)
        buttons_layout.addWidget(self.complete_button)
        buttons_layout.addWidget(self.sort_button)

        urgent_layout = QHBoxLayout()
        self.enqueue_button = QPushButton("Add to Urgent Queue")
        self.dequeue_button = QPushButton("Dequeue Urgent Task")
        urgent_layout.addWidget(self.enqueue_button)
        urgent_layout.addWidget(self.dequeue_button)

        self.search_input = QLineEdit(placeholderText="Search tasks...")
        self.todo_list_widget = QListWidget()
        self.urgent_list_widget = QListWidget()

        layout.addLayout(input_layout)
        layout.addLayout(buttons_layout)
        layout.addLayout(urgent_layout)
        layout.addWidget(QLabel("Search Task:"))
        layout.addWidget(self.search_input)
        layout.addWidget(QLabel("Todo List:"))
        layout.addWidget(self.todo_list_widget)
        layout.addWidget(QLabel("Urgent Task Queue:"))
        layout.addWidget(self.urgent_list_widget)

        self.setLayout(layout)

        # Connect buttons to functions
        self.add_button.clicked.connect(self.add_task)
        self.delete_button.clicked.connect(self.delete_task)
        self.undo_button.clicked.connect(self.undo_delete)
        self.complete_button.clicked.connect(self.mark_task_complete)
        self.sort_button.clicked.connect(self.sort_tasks)
        self.enqueue_button.clicked.connect(self.enqueue_urgent_task)
        self.dequeue_button.clicked.connect(self.dequeue_urgent_task)
        self.search_input.textChanged.connect(self.search_task)

    def add_task(self):
        task = self.task_input.text().strip()
        due_date = self.due_date_input.dateTime().toPython().strftime("%Y-%m-%d %H:%M:%S")
        priority = self.priority_input.currentText()
        if task:
            self.task_list.add_task(task, due_date, priority)
            self.update_task_list()
            self.task_input.clear()
        else:
            QMessageBox.warning(self, "Input Error", "Please enter a task.")

    def delete_task(self):
        selected_task = self.todo_list_widget.currentItem()
        if selected_task:
            task_name = selected_task.text().split(" | ")[0]
            deleted_task = self.task_list.delete_task(task_name)
            if deleted_task:
                self.undo_stack.push(deleted_task)
                self.update_task_list()
            else:
                QMessageBox.warning(self, "Delete Error", "Task not found.")
        else:
            QMessageBox.warning(self, "Selection Error", "Please select a task to delete.")

    def undo_delete(self):
        last_deleted_task = self.undo_stack.pop()
        if last_deleted_task:
            self.task_list.add_task(last_deleted_task.task, last_deleted_task.due_date, last_deleted_task.priority)
            self.update_task_list()
        else:
            QMessageBox.information(self, "Undo Error", "No tasks to undo.")

    def mark_task_complete(self):
        selected_task = self.todo_list_widget.currentItem()
        if selected_task:
            task_name = selected_task.text().split(" | ")[0]
            if self.task_list.mark_complete(task_name):
                self.update_task_list()
            else:
                QMessageBox.warning(self, "Error", "Unable to mark as complete.")
        else:
            QMessageBox.warning(self, "Selection Error", "Please select a task to mark complete.")

    def sort_tasks(self):
        self.task_list.sort_tasks_by_due_date()
        self.update_task_list()

    def enqueue_urgent_task(self):
        selected_task = self.todo_list_widget.currentItem()
        if selected_task:
            task_name = selected_task.text().split(" | ")[0]
            self.urgent_task_queue.enqueue(task_name)
            self.update_urgent_task_list()
        else:
            QMessageBox.warning(self, "Selection Error", "Please select a task to add to urgent queue.")

    def dequeue_urgent_task(self):
        urgent_task = self.urgent_task_queue.dequeue()
        if urgent_task:
            QMessageBox.information(self, "Urgent Task", f"Processing urgent task: {urgent_task}")
            self.update_urgent_task_list()
        else:
            QMessageBox.information(self, "Queue Empty", "No urgent tasks in the queue.")

    def search_task(self):
        search_term = self.search_input.text().lower()
        tasks = self.task_list.display_tasks()
        self.todo_list_widget.clear()
        for task in tasks:
            if search_term in task["task"].lower():
                self.todo_list_widget.addItem(f"{task['task']} | {task['due_date']} | {task['priority']} | {task['status']}")

    def update_task_list(self):
        self.todo_list_widget.clear()
        for task in self.task_list.display_tasks():
            item = f"{task['task']} | {task['due_date']} | {task['priority']} | {task['status']}"
            list_item = self.todo_list_widget.addItem(item)
            self.todo_list_widget.item(self.todo_list_widget.count() - 1).setForeground(self.get_priority_color(task['priority']))

    def update_urgent_task_list(self):
        self.urgent_list_widget.clear()
        for task in self.urgent_task_queue.queue:
            self.urgent_list_widget.addItem(task)

    def get_priority_color(self, priority):
        colors = {"Low": QColor(0, 128, 0), "Medium": QColor(255, 165, 0), "High": QColor(255, 0, 0)}
        return colors.get(priority, QColor(0, 0, 0))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    todo_app = TodoApp()
    todo_app.show()
    sys.exit(app.exec())