"""
WINDOWS VERSION
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


class ToDoList(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('To-Do List')
        self.setGeometry(500, 500, 600, 500)

        self.layout = QVBoxLayout()

        self.input_task = QLineEdit()
        self.input_task.setPlaceholderText('Введите задачу')
        self.input_task.returnPressed.connect(self.add_task)  # добавление по Enter
        self.layout.addWidget(self.input_task)

        self.add_button = QPushButton('Добавить задачу')
        self.add_button.clicked.connect(self.add_task)
        self.layout.addWidget(self.add_button)

        self.task_list = QListWidget()
        self.task_list.itemChanged.connect(self.update_counter)
        self.task_list.itemDoubleClicked.connect(self.edit_task)
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

        self.of_button = QPushButton('Снять все отметки')
        self.of_button.clicked.connect(self.of_all)
        self.layout.addWidget(self.of_button)

        self.save_json_button = QPushButton('Сохранить в JSON')
        self.save_json_button.clicked.connect(self.save_tasks_json)
        self.layout.addWidget(self.save_json_button)

        self.load_json_button = QPushButton('Загрузить из JSON')
        self.load_json_button.clicked.connect(self.load_tasks_json)
        self.layout.addWidget(self.load_json_button)

        self.clear_button = QPushButton('Очистить всё')
        self.clear_button.clicked.connect(self.clear_all)
        self.layout.addWidget(self.clear_button)

        self.counter_label = QLabel('Всего задач: 0 | Выполнено: 0')
        self.layout.addWidget(self.counter_label)

        self.setLayout(self.layout)

        # счётчик уже существует -> загрузка безопасна, и счёт сразу корректный
        self.load_tasks()
        self.update_counter()

    # --- единая «фабрика» элемента: текст + чекбокс + приоритет + цвет ---
    def make_item(self, text, checked=False, priority='Обычный'):
        item = QListWidgetItem(text)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
        item.setData(Qt.ItemDataRole.UserRole, priority)  # приоритет хранится в элементе
        if priority == 'Высокий':
            item.setForeground(Qt.GlobalColor.red)
        else:
            item.setForeground(Qt.GlobalColor.darkGreen)
        return item

    def add_task(self):
        task_text = self.input_task.text().strip()
        if not task_text:
            QMessageBox.warning(self, 'Предупреждение', 'Задача не может быть пустой.')
            return

        priority, ok = QInputDialog.getItem(
            self, 'Приоритет', 'Выберите:', ['Обычный', 'Высокий'], 0, False
        )
        if not ok:
            priority = 'Обычный'

        item = self.make_item(task_text, False, priority)
        self.task_list.addItem(item)
        self.input_task.clear()
        self.save_tasks()        # сохраняем сразу после добавления
        self.update_counter()

    def save_tasks(self):
        lines = []
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            text = item.text()
            priority = item.data(Qt.ItemDataRole.UserRole) or 'Обычный'
            checked = item.checkState() == Qt.CheckState.Checked
            lines.append(f'{text}|{priority}|{checked}')

        with open('tasks.txt', 'w', encoding='utf-8') as file:
            file.write('\n'.join(lines))

    def load_tasks(self):
        if not os.path.exists('tasks.txt'):
            return
        with open('tasks.txt', 'r', encoding='utf-8') as file:
            for raw in file:
                line = raw.rstrip('\n')
                if not line.strip():
                    continue
                # rsplit('|', 2): два последних поля — приоритет и отметка,
                # поэтому символ '|' внутри текста задачи больше не ломает разбор
                parts = line.rsplit('|', 2)
                if len(parts) == 3:
                    text, priority, checked = parts
                elif len(parts) == 2:          # старый формат: text|checked
                    text, checked = parts
                    priority = 'Обычный'
                else:
                    text, priority, checked = parts[0], 'Обычный', 'False'
                item = self.make_item(text, checked == 'True', priority)
                self.task_list.addItem(item)

    def save_tasks_json(self):
        data = []
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            data.append({
                'text': item.text(),
                'checked': item.checkState() == Qt.CheckState.Checked,
                'priority': item.data(Qt.ItemDataRole.UserRole) or 'Обычный'
            })
        with open('tasks.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        QMessageBox.information(self, 'Экспорт', 'Задачи сохранены в tasks.json')

    def load_tasks_json(self):
        if not os.path.exists('tasks.json'):
            QMessageBox.information(self, 'Импорт', 'Файл tasks.json не найден.')
            return
        with open('tasks.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.task_list.clear()  # заменяем список, а не добавляем поверх (без дублей)
        for task in data:
            item = self.make_item(
                task.get('text', ''),
                task.get('checked', False),
                task.get('priority', 'Обычный')
            )
            self.task_list.addItem(item)
        self.save_tasks()
        self.update_counter()

    def closeEvent(self, event):
        self.save_tasks()
        event.accept()

    def delete_task(self):
        for i in range(self.task_list.count() - 1, -1, -1):
            item = self.task_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                self.task_list.takeItem(i)
        self.save_tasks()
        self.update_counter()

    def clear_all(self):
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
        if ok and text.strip():
            item.setText(text.strip())
            self.save_tasks()

    def clear_did(self):
        for i in range(self.task_list.count() - 1, -1, -1):
            if self.task_list.item(i).checkState() == Qt.CheckState.Checked:
                self.task_list.takeItem(i)
        self.save_tasks()
        self.update_counter()

    def checked_all(self):
        for i in range(self.task_list.count()):
            self.task_list.item(i).setCheckState(Qt.CheckState.Checked)
        self.save_tasks()
        self.update_counter()

    def of_all(self):
        for i in range(self.task_list.count()):
            self.task_list.item(i).setCheckState(Qt.CheckState.Unchecked)
        self.save_tasks()
        self.update_counter()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = ToDoList()
    main_window.show()
    sys.exit(app.exec())
