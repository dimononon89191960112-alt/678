import sys
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
                             QComboBox, QSpinBox, QDateEdit, QMessageBox, QTabWidget, QGroupBox,
                             QHeaderView, QTextEdit)
from PyQt5.QtCore import Qt, QDate
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class Employee:
    def __init__(self, name, role):
        self.name = name
        self.role = role  # "Монтажник" или "Инженер"
        self.assigned_post = None
        self.work_hours = 8  # По умолчанию 8 часов

    def can_work_on_stage(self, stage_type):
        if stage_type == "Инженерная":
            return self.role == "Инженер"
        return True  # Монтажники могут работать на монтажных этапах

class ProductionStage:
    def __init__(self, name, stage_type, time_per_unit):
        self.name = name
        self.stage_type = stage_type  # "Монтажная" или "Инженерная"
        self.time_per_unit = time_per_unit  # Время на единицу продукции в часах

class ProductModel:
    def __init__(self, name, stages):
        self.name = name
        self.stages = stages  # Список этапов ProductionStage

class ProductionOrder:
    def __init__(self, model, quantity, creation_date):
        self.model = model
        self.quantity = quantity
        self.creation_date = creation_date
        self.completed_units = 0
        self.daily_progress = {}  # Дата: количество произведенных единиц
        self.estimated_end_date = None
        self.calculate_estimated_end_date()

    def calculate_estimated_end_date(self):
        # Этот метод будет пересчитываться после назначения сотрудников
        pass

    def add_daily_progress(self, date, units):
        self.daily_progress[date] = units
        self.completed_units += units
        # Пересчет оставшегося времени после добавления прогресса

class ProductionScheduleApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.employees = []
        self.product_models = []
        self.orders = []
        self.current_assignments = {}  # Пост: сотрудник
        self.workday_hours = 8  # Стандартный рабочий день
        
        self.initUI()
        self.load_sample_data()
        
    def initUI(self):
        self.setWindowTitle("Система планирования производства")
        self.setGeometry(100, 100, 1200, 800)
        
        # Создаем вкладки
        tabs = QTabWidget()
        self.setCentralWidget(tabs)
        
        # Вкладка управления сотрудниками
        employee_tab = QWidget()
        employee_layout = QVBoxLayout()
        
        # Группа добавления сотрудников
        add_employee_group = QGroupBox("Добавить сотрудника")
        add_employee_layout = QHBoxLayout()
        
        self.employee_name_input = QLineEdit()
        self.employee_name_input.setPlaceholderText("Имя сотрудника")
        self.employee_role_combo = QComboBox()
        self.employee_role_combo.addItems(["Монтажник", "Инженер"])
        
        add_employee_btn = QPushButton("Добавить")
        add_employee_btn.clicked.connect(self.add_employee)
        
        add_employee_layout.addWidget(QLabel("Имя:"))
        add_employee_layout.addWidget(self.employee_name_input)
        add_employee_layout.addWidget(QLabel("Должность:"))
        add_employee_layout.addWidget(self.employee_role_combo)
        add_employee_layout.addWidget(add_employee_btn)
        add_employee_group.setLayout(add_employee_layout)
        
        # Таблица сотрудников
        self.employees_table = QTableWidget()
        self.employees_table.setColumnCount(3)
        self.employees_table.setHorizontalHeaderLabels(["Имя", "Должность", "Действия"])
        
        employee_layout.addWidget(add_employee_group)
        employee_layout.addWidget(self.employees_table)
        employee_tab.setLayout(employee_layout)
        
        # Вкладка управления моделями продукции
        model_tab = QWidget()
        model_layout = QVBoxLayout()
        
        # Группа добавления моделей
        add_model_group = QGroupBox("Добавить модель продукции")
        add_model_layout = QVBoxLayout()
        
        model_name_layout = QHBoxLayout()
        self.model_name_input = QLineEdit()
        self.model_name_input.setPlaceholderText("Название модели")
        model_name_layout.addWidget(QLabel("Название:"))
        model_name_layout.addWidget(self.model_name_input)
        
        add_model_layout.addLayout(model_name_layout)
        
        # Этапы производства
        stages_group = QGroupBox("Этапы производства")
        stages_layout = QVBoxLayout()
        
        self.stages_table = QTableWidget()
        self.stages_table.setColumnCount(3)
        self.stages_table.setHorizontalHeaderLabels(["Название", "Тип", "Время на ед. (час)"])
        
        add_stage_layout = QHBoxLayout()
        self.stage_name_input = QLineEdit()
        self.stage_name_input.setPlaceholderText("Название этапа")
        self.stage_type_combo = QComboBox()
        self.stage_type_combo.addItems(["Монтажная", "Инженерная"])
        self.stage_time_input = QLineEdit()
        self.stage_time_input.setPlaceholderText("Время на ед.")
        
        add_stage_btn = QPushButton("Добавить этап")
        add_stage_btn.clicked.connect(self.add_stage_to_model)
        
        add_stage_layout.addWidget(QLabel("Название:"))
        add_stage_layout.addWidget(self.stage_name_input)
        add_stage_layout.addWidget(QLabel("Тип:"))
        add_stage_layout.addWidget(self.stage_type_combo)
        add_stage_layout.addWidget(QLabel("Время:"))
        add_stage_layout.addWidget(self.stage_time_input)
        add_stage_layout.addWidget(add_stage_btn)
        
        stages_layout.addWidget(self.stages_table)
        stages_layout.addLayout(add_stage_layout)
        stages_group.setLayout(stages_layout)
        
        add_model_layout.addWidget(stages_group)
        
        add_model_btn = QPushButton("Создать модель")
        add_model_btn.clicked.connect(self.add_product_model)
        add_model_layout.addWidget(add_model_btn)
        
        add_model_group.setLayout(add_model_layout)
        model_layout.addWidget(add_model_group)
        
        # Таблица моделей
        self.models_table = QTableWidget()
        self.models_table.setColumnCount(2)
        self.models_table.setHorizontalHeaderLabels(["Название", "Кол-во этапов"])
        model_layout.addWidget(self.models_table)
        
        model_tab.setLayout(model_layout)
        
        # Вкладка назначения на посты
        assignment_tab = QWidget()
        assignment_layout = QVBoxLayout()
        
        # Выбор даты
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Дата:"))
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.dateChanged.connect(self.update_assignment_display)
        date_layout.addWidget(self.date_edit)
        
        # Продолжительность рабочего дня
        workday_layout = QHBoxLayout()
        workday_layout.addWidget(QLabel("Продолжительность рабочего дня (часы):"))
        self.workday_hours_input = QLineEdit()
        self.workday_hours_input.setText("8")
        self.workday_hours_input.textChanged.connect(self.update_workday_hours)
        workday_layout.addWidget(self.workday_hours_input)
        
        assignment_layout.addLayout(date_layout)
        assignment_layout.addLayout(workday_layout)
        
        # Таблица постов
        posts_group = QGroupBox("Назначение на посты")
        posts_layout = QVBoxLayout()
        
        self.posts_table = QTableWidget()
        self.posts_table.setColumnCount(4)
        self.posts_table.setHorizontalHeaderLabels(["Пост", "Тип поста", "Сотрудник", "Действие"])
        
        posts_layout.addWidget(self.posts_table)
        posts_group.setLayout(posts_layout)
        assignment_layout.addWidget(posts_group)
        
        # Кнопка сохранения назначений
        save_assignments_btn = QPushButton("Сохранить назначения")
        save_assignments_btn.clicked.connect(self.save_assignments)
        assignment_layout.addWidget(save_assignments_btn)
        
        assignment_tab.setLayout(assignment_layout)
        
        # Вкладка заказов
        orders_tab = QWidget()
        orders_layout = QVBoxLayout()
        
        # Создание заказа
        create_order_group = QGroupBox("Создать заказ")
        create_order_layout = QHBoxLayout()
        
        self.order_model_combo = QComboBox()
        self.order_quantity_input = QSpinBox()
        self.order_quantity_input.setMinimum(1)
        self.order_quantity_input.setMaximum(10000)
        self.order_quantity_input.setValue(100)
        
        create_order_btn = QPushButton("Создать заказ")
        create_order_btn.clicked.connect(self.create_order)
        
        create_order_layout.addWidget(QLabel("Модель:"))
        create_order_layout.addWidget(self.order_model_combo)
        create_order_layout.addWidget(QLabel("Количество:"))
        create_order_layout.addWidget(self.order_quantity_input)
        create_order_layout.addWidget(create_order_btn)
        create_order_group.setLayout(create_order_layout)
        orders_layout.addWidget(create_order_group)
        
        # Таблица заказов
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(5)
        self.orders_table.setHorizontalHeaderLabels(["Модель", "Количество", "Создан", "Прогноз завершения", "Выполнено"])
        orders_layout.addWidget(self.orders_table)
        
        # Ввод ежедневной продукции
        daily_production_group = QGroupBox("Ежедневная выработка")
        daily_production_layout = QVBoxLayout()
        
        select_order_layout = QHBoxLayout()
        select_order_layout.addWidget(QLabel("Заказ:"))
        self.daily_order_combo = QComboBox()
        select_order_layout.addWidget(self.daily_order_combo)
        
        select_date_layout = QHBoxLayout()
        select_date_layout.addWidget(QLabel("Дата:"))
        self.production_date_edit = QDateEdit()
        self.production_date_edit.setDate(QDate.currentDate())
        select_date_layout.addWidget(self.production_date_edit)
        
        production_layout = QHBoxLayout()
        production_layout.addWidget(QLabel("Произведено единиц:"))
        self.daily_production_input = QSpinBox()
        self.daily_production_input.setMinimum(0)
        self.daily_production_input.setMaximum(10000)
        production_layout.addWidget(self.daily_production_input)
        
        save_production_btn = QPushButton("Сохранить выработку")
        save_production_btn.clicked.connect(self.save_daily_production)
        
        daily_production_layout.addLayout(select_order_layout)
        daily_production_layout.addLayout(select_date_layout)
        daily_production_layout.addLayout(production_layout)
        daily_production_layout.addWidget(save_production_btn)
        daily_production_group.setLayout(daily_production_layout)
        orders_layout.addWidget(daily_production_group)
        
        orders_tab.setLayout(orders_layout)
        
        # Вкладка графиков
        charts_tab = QWidget()
        charts_layout = QVBoxLayout()
        
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        charts_layout.addWidget(self.canvas)
        
        update_charts_btn = QPushButton("Обновить графики")
        update_charts_btn.clicked.connect(self.update_charts)
        charts_layout.addWidget(update_charts_btn)
        
        charts_tab.setLayout(charts_layout)
        
        # Добавляем вкладки
        tabs.addTab(employee_tab, "Сотрудники")
        tabs.addTab(model_tab, "Модели продукции")
        tabs.addTab(assignment_tab, "Назначения")
        tabs.addTab(orders_tab, "Заказы")
        tabs.addTab(charts_tab, "Графики")
        
        self.update_employees_table()
        self.update_models_table()
        self.update_posts_table()
        self.update_orders_table()
        self.update_order_combos()
        
    def load_sample_data(self):
        # Загрузка примеров данных для демонстрации
        self.employees.append(Employee("Иванов И.И.", "Монтажник"))
        self.employees.append(Employee("Петров П.П.", "Монтажник"))
        self.employees.append(Employee("Сидоров С.С.", "Инженер"))
        self.employees.append(Employee("Кузнецов К.К.", "Инженер"))
        self.employees.append(Employee("Николаев Н.Н.", "Инженер"))
        
        # Пример модели продукции
        stages = [
            ProductionStage("Динамик к основанию", "Монтажная", 0.2),
            ProductionStage("Установка микропрограммы", "Инженерная", 0.3),
            ProductionStage("Припаивание платы", "Инженерная", 0.4),
            ProductionStage("Сборка в корпус", "Монтажная", 0.3),
            ProductionStage("Нанесение серийного номера и ПО", "Инженерная", 0.2),
            ProductionStage("Финальная сборка и упаковка", "Монтажная", 0.3)
        ]
        self.product_models.append(ProductModel("Излучатель 1", stages))
        
        self.update_employees_table()
        self.update_models_table()
        self.update_order_combos()
        
    def add_employee(self):
        name = self.employee_name_input.text()
        role = self.employee_role_combo.currentText()
        
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите имя сотрудника")
            return
            
        self.employees.append(Employee(name, role))
        self.update_employees_table()
        self.employee_name_input.clear()
        
    def update_employees_table(self):
        self.employees_table.setRowCount(len(self.employees))
        for i, employee in enumerate(self.employees):
            self.employees_table.setItem(i, 0, QTableWidgetItem(employee.name))
            self.employees_table.setItem(i, 1, QTableWidgetItem(employee.role))
            
            delete_btn = QPushButton("Удалить")
            delete_btn.clicked.connect(lambda checked, e=employee: self.delete_employee(e))
            self.employees_table.setCellWidget(i, 2, delete_btn)
        
        self.employees_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
    def delete_employee(self, employee):
        self.employees.remove(employee)
        self.update_employees_table()
        self.update_posts_table()
        
    def add_stage_to_model(self):
        name = self.stage_name_input.text()
        stage_type = self.stage_type_combo.currentText()
        time_text = self.stage_time_input.text()
        
        if not name or not time_text:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля этапа")
            return
            
        try:
            time_per_unit = float(time_text)
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректное время")
            return
            
        row = self.stages_table.rowCount()
        self.stages_table.insertRow(row)
        self.stages_table.setItem(row, 0, QTableWidgetItem(name))
        self.stages_table.setItem(row, 1, QTableWidgetItem(stage_type))
        self.stages_table.setItem(row, 2, QTableWidgetItem(str(time_per_unit)))
        
        self.stage_name_input.clear()
        self.stage_time_input.clear()
        
    def add_product_model(self):
        name = self.model_name_input.text()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название модели")
            return
            
        if self.stages_table.rowCount() == 0:
            QMessageBox.warning(self, "Ошибка", "Добавьте хотя бы один этап")
            return
            
        stages = []
        for row in range(self.stages_table.rowCount()):
            stage_name = self.stages_table.item(row, 0).text()
            stage_type = self.stages_table.item(row, 1).text()
            time_per_unit = float(self.stages_table.item(row, 2).text())
            stages.append(ProductionStage(stage_name, stage_type, time_per_unit))
            
        self.product_models.append(ProductModel(name, stages))
        self.update_models_table()
        self.update_order_combos()
        self.model_name_input.clear()
        self.stages_table.setRowCount(0)
        
    def update_models_table(self):
        self.models_table.setRowCount(len(self.product_models))
        for i, model in enumerate(self.product_models):
            self.models_table.setItem(i, 0, QTableWidgetItem(model.name))
            self.models_table.setItem(i, 1, QTableWidgetItem(str(len(model.stages))))
        
        self.models_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
    def update_order_combos(self):
        self.order_model_combo.clear()
        self.daily_order_combo.clear()
        
        for model in self.product_models:
            self.order_model_combo.addItem(model.name)
            
        for order in self.orders:
            self.daily_order_combo.addItem(f"{order.model.name} ({order.quantity} шт.)")
        
    def update_posts_table(self):
        self.posts_table.setRowCount(5)
        for i in range(5):
            post_type = "Монтажная" if i < 2 else "Инженерная"
            self.posts_table.setItem(i, 0, QTableWidgetItem(f"Пост {i+1}"))
            self.posts_table.setItem(i, 1, QTableWidgetItem(post_type))
            
            # Комбо-бокс для выбора сотрудника
            combo = QComboBox()
            combo.addItem("Не назначен")
            
            # Фильтруем сотрудников по типу поста
            for employee in self.employees:
                if post_type == "Инженерная" and employee.role != "Инженер":
                    continue
                combo.addItem(employee.name)
                
            # Устанавливаем текущее значение, если есть назначение
            current_date = self.date_edit.date().toString("yyyy-MM-dd")
            assignment_key = f"{current_date}_post_{i+1}"
            if assignment_key in self.current_assignments:
                assigned_employee = self.current_assignments[assignment_key]
                index = combo.findText(assigned_employee.name)
                if index >= 0:
                    combo.setCurrentIndex(index)
            
            self.posts_table.setCellWidget(i, 2, combo)
            
            # Кнопка для назначения
            assign_btn = QPushButton("Назначить")
            assign_btn.clicked.connect(lambda checked, p=i+1, c=combo: self.assign_employee_to_post(p, c.currentText()))
            self.posts_table.setCellWidget(i, 3, assign_btn)
        
        self.posts_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
    def assign_employee_to_post(self, post_number, employee_name):
        if employee_name == "Не назначен":
            # Снимаем назначение
            current_date = self.date_edit.date().toString("yyyy-MM-dd")
            assignment_key = f"{current_date}_post_{post_number}"
            if assignment_key in self.current_assignments:
                del self.current_assignments[assignment_key]
            QMessageBox.information(self, "Назначение", f"Сотрудник снят с поста {post_number}")
            return
            
        # Находим сотрудника
        employee = next((e for e in self.employees if e.name == employee_name), None)
        if not employee:
            QMessageBox.warning(self, "Ошибка", "Сотрудник не найден")
            return
            
        # Проверяем, может ли сотрудник работать на этом типе поста
        post_type = "Монтажная" if post_number < 3 else "Инженерная"
        if not employee.can_work_on_stage(post_type):
            QMessageBox.warning(self, "Ошибка", "Этот сотрудник не может работать на данном типе поста")
            return
            
        # Сохраняем назначение
        current_date = self.date_edit.date().toString("yyyy-MM-dd")
        assignment_key = f"{current_date}_post_{post_number}"
        self.current_assignments[assignment_key] = employee
        
        QMessageBox.information(self, "Назначение", f"{employee_name} назначен на пост {post_number}")
        
    def update_assignment_display(self):
        self.update_posts_table()
        
    def update_workday_hours(self):
        try:
            self.workday_hours = float(self.workday_hours_input.text())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректное количество часов")
            
    def save_assignments(self):
        # В реальной реализации здесь будет сохранение назначений
        QMessageBox.information(self, "Сохранение", "Назначения сохранены")
        
    def create_order(self):
        model_name = self.order_model_combo.currentText()
        quantity = self.order_quantity_input.value()
        
        model = next((m for m in self.product_models if m.name == model_name), None)
        if not model:
            QMessageBox.warning(self, "Ошибка", "Модель не найдена")
            return
            
        order = ProductionOrder(model, quantity, datetime.now())
        self.orders.append(order)
        self.update_orders_table()
        self.update_order_combos()
        
        QMessageBox.information(self, "Заказ создан", f"Заказ на {quantity} единиц {model_name} создан")
        
    def update_orders_table(self):
        self.orders_table.setRowCount(len(self.orders))
        for i, order in enumerate(self.orders):
            self.orders_table.setItem(i, 0, QTableWidgetItem(order.model.name))
            self.orders_table.setItem(i, 1, QTableWidgetItem(str(order.quantity)))
            self.orders_table.setItem(i, 2, QTableWidgetItem(order.creation_date.strftime("%Y-%m-%d")))
            
            # Расчет прогнозируемой даты завершения
            if order.estimated_end_date:
                end_date = order.estimated_end_date.strftime("%Y-%m-%d")
            else:
                end_date = "Расчитывается..."
            self.orders_table.setItem(i, 3, QTableWidgetItem(end_date))
            self.orders_table.setItem(i, 4, QTableWidgetItem(str(order.completed_units)))
        
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
    def save_daily_production(self):
        if not self.orders:
            QMessageBox.warning(self, "Ошибка", "Нет заказов")
            return
            
        order_index = self.daily_order_combo.currentIndex()
        if order_index < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите заказ")
            return
            
        order = self.orders[order_index]
        date = self.production_date_edit.date().toString("yyyy-MM-dd")
        units = self.daily_production_input.value()
        
        order.add_daily_progress(date, units)
        self.update_orders_table()
        
        QMessageBox.information(self, "Сохранено", f"Производство {units} единиц за {date} сохранено")
        
    def update_charts(self):
        self.figure.clear()
        
        if not self.orders:
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'Нет данных для отображения', 
                    horizontalalignment='center', verticalalignment='center')
            self.canvas.draw()
            return
            
        # График прогресса по заказам
        ax = self.figure.add_subplot(111)
        
        orders_data = []
        for order in self.orders:
            planned = order.quantity
            actual = order.completed_units
            percentage = (actual / planned) * 100 if planned > 0 else 0
            orders_data.append((order.model.name, planned, actual, percentage))
            
        model_names = [data[0] for data in orders_data]
        planned_values = [data[1] for data in orders_data]
        actual_values = [data[2] for data in orders_data]
        
        x = np.arange(len(model_names))
        width = 0.35
        
        ax.bar(x - width/2, planned_values, width, label='План')
        ax.bar(x + width/2, actual_values, width, label='Факт')
        
        ax.set_xlabel('Заказы')
        ax.set_ylabel('Количество')
        ax.set_title('Прогресс выполнения заказов')
        ax.set_xticks(x)
        ax.set_xticklabels(model_names, rotation=45)
        ax.legend()
        
        self.figure.tight_layout()
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProductionScheduleApp()
    window.show()
    sys.exit(app.exec_())