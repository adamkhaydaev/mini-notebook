"""
LINUX VERSION
"""

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QMessageBox,
    QLabel, QInputDialog
)
from PyQt6.QtCore import Qt
import sys
import os
import json

# Подавление сообщений Wayland и Qt
os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false'
os.environ['QT_LOGGING_CONF'] = ''
os.environ['QT_QPA_PLATFORM'] = 'wayland'

# Перенаправление stderr в пустоту
sys.stderr = open(os.devnull, 'w')

class ToDoList(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('To-Do List')
        self.setGeometry(500, 500, 600, 500)

        self.layout = QVBoxLayout()

        self.input_task = QLineEdit()
        self.input_task.setPlaceholderText('Введите задачу')
        self.layout.addWidget(self.input_task)

        self.add_button = QPushButton('Добавить задачу')
        self.add_button.clicked.connect(self.add_task)
        self.layout.addWidget(self.add_button)

        self.task_list = QListWidget()
        self.task_list.itemChanged.connect(self.update_counter)
        self.layout.addWidget(self.task_list)

        self.delete_button = QPushButton('Удалить выбранные задачи')
        self.delete_button.clicked.connect(self.delete_task)
        self.layout.addWidget(self.delete_button)

        self.clear_done_button = QPushButton('Очистить выполненные')
        self.clear_done_button.clicked.connect(self.clear_did)
        self.layout.addWidget(self.clear_done_button)

        self.checked_button = QPushButton('Отметить все выполненными')
        self.checked_button.clicked.connect(self.checked_all)
        self.layout.addWidget(self.checked_button)

        self.of_button = QPushButton('Снять все выполненными')
        self.of_button.clicked.connect(self.of_all)
        self.layout.addWidget(self.of_button)

        self.task_list.itemDoubleClicked.connect(self.edit_task)

        self.save_json_button = QPushButton('Сохранить в JSON')
        self.save_json_button.clicked.connect(self.save_tasks_json)
        self.layout.addWidget(self.save_json_button)

        self.load_json_button = QPushButton('Загрузить из JSON')
        self.load_json_button.clicked.connect(self.load_tasks_json)
        self.layout.addWidget(self.load_json_button)

        self.clear_button = QPushButton('Очистить всё')
        self.clear_button.clicked.connect(self.clear_all)
        self.layout.addWidget(self.clear_button)

        self.load_tasks()

        self.counter_label = QLabel('Всего задач: 0 | Выполнено: 0')
        self.layout.addWidget(self.counter_label)

        self.setLayout(self.layout)

    def add_task(self):
        task_text = self.input_task.text().strip()
        if task_text:
            priority, ok = QInputDialog.getItem(self, 'Приоритет', 'Выберите:', ['Обычный', 'Высокий'], 0, False)
            item = QListWidgetItem(task_text)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            if ok and priority == 'Высокий':
                item.setForeground(Qt.GlobalColor.red)
            else:
                item.setForeground(Qt.GlobalColor.darkGreen)
            self.task_list.addItem(item)
            self.input_task.clear()
        else:
            QMessageBox.warning(self, 'Предупреждение', 'Задача не может быть пустой.')
        self.update_counter()

    def save_tasks(self):
        tasks = []
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            task_text = item.text()
            task_checked = item.checkState() == Qt.CheckState.Checked
            if item.foreground().color() == Qt.GlobalColor.red:
                priority = 'Высокий'
            else:
                priority = 'Обычный'
            tasks.append(f'{task_text}|{task_checked}|{priority}')

        with open('tasks.txt', 'w', encoding='utf-8') as file:
            file.write('\n'.join(tasks))

    def save_tasks_json(self):
        data = []
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            if item.foreground().color() == Qt.GlobalColor.red:
                priority = 'Высокий'
            else:
                priority = 'Обычный'
            data.append({
                "text": item.text(),
                "checked": item.checkState() == Qt.CheckState.Checked,
                "priority": priority
            })
        with open('tasks.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_tasks_json(self):
        if os.path.exists('tasks.json'):
            with open('tasks.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                for task in data:
                    item = QListWidgetItem(task['text'])
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    item.setCheckState(Qt.CheckState.Checked if task['checked'] else Qt.CheckState.Unchecked)
                    priority = task.get('priority', 'Обычный')
                    if priority == 'Высокий':
                        item.setForeground(Qt.GlobalColor.red)
                    else:
                        item.setForeground(Qt.GlobalColor.darkGreen)
                    self.task_list.addItem(item)

    def closeEvent(self, event):
        self.save_tasks()
        event.accept()

    def load_tasks(self):
        if os.path.exists('tasks.txt'):
            with open('tasks.txt', 'r', encoding='utf-8') as file:
                for line in file:
                    if line.strip():
                        parts = line.strip().split('|')
                        task_text = parts[0]
                        task_checked = parts[1] == 'True'
                        priority = parts[2] if len(parts) > 2 else 'Обычный'
                        item = QListWidgetItem(task_text)
                        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                        item.setCheckState(Qt.CheckState.Checked if task_checked else Qt.CheckState.Unchecked)
                        if priority == 'Высокий':
                            item.setForeground(Qt.GlobalColor.red)
                        else:
                            item.setForeground(Qt.GlobalColor.darkGreen)
                        self.task_list.addItem(item)

    def delete_task(self):
        for i in range(self.task_list.count() - 1, -1, -1):
            item = self.task_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                self.task_list.takeItem(i)
        self.save_tasks()
        self.update_counter()

    def clear_all(self):
        reply = QMessageBox.question(self, 'Подтверждение', 'Удалить все задачи?')
        if reply == QMessageBox.StandardButton.Yes:
            self.task_list.clear()
            self.save_tasks()
            self.input_task.clear()
            self.update_counter()

    def update_counter(self):
        total = self.task_list.count()
        checked = 0
        for i in range(total):
            if self.task_list.item(i).checkState() == Qt.CheckState.Checked:
                checked += 1
        self.counter_label.setText(f'Всего задач: {total} | Выполнено: {checked}')

    def edit_task(self, item):
        text, ok = QInputDialog.getText(self, 'Редактировать', 'Текст задачи:', text=item.text())
        if ok and text:
            item.setText(text)
            self.save_tasks()

    def clear_did(self):
        for i in range(self.task_list.count() - 1, -1, -1):
            if self.task_list.item(i).checkState() == Qt.CheckState.Checked:
                self.task_list.takeItem(i)
        self.save_tasks()
        self.update_counter()

    def checked_all(self):
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            item.setCheckState(Qt.CheckState.Checked)
        self.save_tasks()
        self.update_counter()

    def of_all(self):
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            item.setCheckState(Qt.CheckState.Unchecked)
        self.save_tasks()
        self.update_counter()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QLineEdit {
            background-color: #3c3c3c;
            border: 1px solid #555;
            padding: 5px;
            border-radius: 3px;
        }
        QPushButton {
            background-color: #444;
            border: 1px solid #555;
            padding: 6px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #555;
        }
        QListWidget {
            background-color: #3c3c3c;
            border: 1px solid #555;
        }
    """)
    main_window = ToDoList()
    main_window.show()
    sys.exit(app.exec())
