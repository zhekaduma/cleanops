"""Экран калькулятора стоимости.

Реализует F-1.1–F-1.8: расчёт стоимости заказа по формуле из ТЗ.
Позволяет выбрать клиента, объект, дату и сохранить заказ в БД.
"""

from datetime import date, time
from typing import Optional

from PyQt5.QtCore import QDate, QTime, Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from src.repositories.client_repository import (
    ClientRepository,
    ObjectRepository,
)
from src.services.calculator_service import CalculatorService
from src.services.dtos import CalculationInput


COLOR_BG = "#F8FAFC"
COLOR_CARD = "#FFFFFF"
COLOR_BORDER = "#E2E8F0"
COLOR_TEXT_PRIMARY = "#0F172A"
COLOR_TEXT_SECONDARY = "#64748B"
COLOR_PRIMARY = "#0EA5A4"


class CalculatorView(QWidget):
    """Экран калькулятора.

    Signals:
        save_requested: Запрос сохранения заказа. Аргумент: dict.
    """

    save_requested = pyqtSignal(dict)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализирует экран."""
        super().__init__(parent)
        self.calculator = CalculatorService()
        self.client_repo = ClientRepository()
        self.object_repo = ObjectRepository()
        self._last_result = None

        self.setStyleSheet(f"background-color: {COLOR_BG};")
        self._build_ui()
        self._load_clients()
        self._recalculate()

    def _build_ui(self) -> None:
        """Собирает интерфейс."""
        main = QVBoxLayout(self)
        main.setContentsMargins(32, 32, 32, 32)
        main.setSpacing(24)

        title = QLabel("Калькулятор стоимости")
        title.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 24px; font-weight: 700;"
        )
        main.addWidget(title)

        columns = QHBoxLayout()
        columns.setSpacing(24)

        columns.addWidget(self._create_form(), 3)
        columns.addWidget(self._create_summary(), 2)

        main.addLayout(columns, 1)

    def _create_form(self) -> QWidget:
        """Создаёт форму ввода."""
        form = QFrame()
        form.setStyleSheet(
            f"QFrame {{ background-color: {COLOR_CARD}; "
            f"border: 1px solid {COLOR_BORDER}; border-radius: 12px; }}"
        )
        layout = QVBoxLayout(form)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        # Клиент
        layout.addWidget(self._label("Клиент"))
        client_row = QHBoxLayout()
        self.client_combo = QComboBox()
        self.client_combo.setFixedHeight(40)
        self.client_combo.setStyleSheet(self._input_style())
        self.client_combo.currentIndexChanged.connect(self._on_client_changed)
        client_row.addWidget(self.client_combo, 1)

        new_client_btn = QPushButton("+")
        new_client_btn.setFixedSize(40, 40)
        new_client_btn.setToolTip("Новый клиент")
        new_client_btn.setCursor(Qt.PointingHandCursor)
        new_client_btn.setStyleSheet(self._small_button_style())
        new_client_btn.clicked.connect(self._on_new_client)
        client_row.addWidget(new_client_btn)
        layout.addLayout(client_row)

        # Объект
        layout.addWidget(self._label("Объект"))
        obj_row = QHBoxLayout()
        self.object_combo = QComboBox()
        self.object_combo.setFixedHeight(40)
        self.object_combo.setStyleSheet(self._input_style())
        self.object_combo.currentIndexChanged.connect(self._on_object_changed)
        obj_row.addWidget(self.object_combo, 1)

        new_obj_btn = QPushButton("+")
        new_obj_btn.setFixedSize(40, 40)
        new_obj_btn.setToolTip("Новый объект")
        new_obj_btn.setCursor(Qt.PointingHandCursor)
        new_obj_btn.setStyleSheet(self._small_button_style())
        new_obj_btn.clicked.connect(self._on_new_object)
        obj_row.addWidget(new_obj_btn)
        layout.addLayout(obj_row)

        # Площадь
        layout.addWidget(self._label("Площадь (м²)"))
        self.area_input = QDoubleSpinBox()
        self.area_input.setRange(1.0, 10000.0)
        self.area_input.setValue(60.0)
        self.area_input.setSuffix(" м²")
        self.area_input.setFixedHeight(40)
        self.area_input.setStyleSheet(self._input_style())
        self.area_input.valueChanged.connect(self._recalculate)
        layout.addWidget(self.area_input)

        # Тип уборки
        layout.addWidget(self._label("Тип уборки"))
        self.cleaning_type = QComboBox()
        self.cleaning_type.addItem("Поддерживающая", "maintenance")
        self.cleaning_type.addItem("Генеральная", "general")
        self.cleaning_type.addItem("После ремонта", "post_renovation")
        self.cleaning_type.addItem("Мойка окон", "windows")
        self.cleaning_type.setCurrentIndex(1)
        self.cleaning_type.setFixedHeight(40)
        self.cleaning_type.setStyleSheet(self._input_style())
        self.cleaning_type.currentIndexChanged.connect(self._recalculate)
        layout.addWidget(self.cleaning_type)

        # Дата и время
        dt_row = QHBoxLayout()

        d_box = QVBoxLayout()
        d_box.addWidget(self._label("Дата"))
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setFixedHeight(40)
        self.date_edit.setStyleSheet(self._input_style())
        d_box.addWidget(self.date_edit)

        t_box = QVBoxLayout()
        t_box.addWidget(self._label("Время"))
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime(10, 0))
        self.time_edit.setFixedHeight(40)
        self.time_edit.setStyleSheet(self._input_style())
        t_box.addWidget(self.time_edit)

        dt_row.addLayout(d_box)
        dt_row.addLayout(t_box)
        layout.addLayout(dt_row)

        # Коэффициенты
        c_row = QHBoxLayout()

        c1 = QVBoxLayout()
        c1.addWidget(self._label("Срочность"))
        self.urgency = QDoubleSpinBox()
        self.urgency.setRange(1.0, 3.0)
        self.urgency.setSingleStep(0.1)
        self.urgency.setValue(1.0)
        self.urgency.setPrefix("× ")
        self.urgency.setFixedHeight(40)
        self.urgency.setStyleSheet(self._input_style())
        self.urgency.valueChanged.connect(self._recalculate)
        c1.addWidget(self.urgency)

        c2 = QVBoxLayout()
        c2.addWidget(self._label("Загрязнение"))
        self.dirt = QDoubleSpinBox()
        self.dirt.setRange(1.0, 3.0)
        self.dirt.setSingleStep(0.1)
        self.dirt.setValue(1.0)
        self.dirt.setPrefix("× ")
        self.dirt.setFixedHeight(40)
        self.dirt.setStyleSheet(self._input_style())
        self.dirt.valueChanged.connect(self._recalculate)
        c2.addWidget(self.dirt)

        c_row.addLayout(c1)
        c_row.addLayout(c2)
        layout.addLayout(c_row)

        # Транспорт и скидка
        e_row = QHBoxLayout()

        t2 = QVBoxLayout()
        t2.addWidget(self._label("Транспорт (₽)"))
        self.transport = QDoubleSpinBox()
        self.transport.setRange(0.0, 10000.0)
        self.transport.setSuffix(" ₽")
        self.transport.setFixedHeight(40)
        self.transport.setStyleSheet(self._input_style())
        self.transport.valueChanged.connect(self._recalculate)
        t2.addWidget(self.transport)

        d2 = QVBoxLayout()
        d2.addWidget(self._label("Скидка (₽)"))
        self.discount = QDoubleSpinBox()
        self.discount.setRange(0.0, 100000.0)
        self.discount.setSuffix(" ₽")
        self.discount.setFixedHeight(40)
        self.discount.setStyleSheet(self._input_style())
        self.discount.valueChanged.connect(self._recalculate)
        d2.addWidget(self.discount)

        e_row.addLayout(t2)
        e_row.addLayout(d2)
        layout.addLayout(e_row)

        layout.addStretch()
        return form

    def _create_summary(self) -> QWidget:
        """Создаёт смету."""
        summary = QFrame()
        summary.setStyleSheet(
            f"QFrame {{ background-color: {COLOR_CARD}; "
            f"border: 1px solid {COLOR_BORDER}; border-radius: 12px; }}"
        )
        layout = QVBoxLayout(summary)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)

        h = QLabel("Смета")
        h.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 18px; font-weight: 600; border: none;"
        )
        layout.addWidget(h)
        layout.addWidget(self._divider())

        self.base_label = self._summary_row(layout, "Базовая стоимость")
        self.tariff_label = self._summary_row(layout, "Тариф")
        self.subtotal_label = self._summary_row(layout, "С коэффициентами")
        self.items_label = self._summary_row(layout, "Доп. услуги")
        self.transport_label = self._summary_row(layout, "Транспорт")
        self.discount_label = self._summary_row(layout, "Скидка")

        layout.addWidget(self._divider())

        t_row = QHBoxLayout()
        ttl = QLabel("ИТОГО:")
        ttl.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 18px; font-weight: 700; border: none;"
        )
        t_row.addWidget(ttl)
        t_row.addStretch()

        self.total_label = QLabel("0 ₽")
        self.total_label.setStyleSheet(
            f"color: {COLOR_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 24px; font-weight: 700; border: none;"
        )
        t_row.addWidget(self.total_label)
        layout.addLayout(t_row)

        layout.addStretch()

        btn = QPushButton("Сохранить заказ")
        btn.setFixedHeight(48)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(self._button_style())
        btn.clicked.connect(self._on_save)
        layout.addWidget(btn)

        return summary

    def _label(self, text: str) -> QLabel:
        """Создаёт label."""
        label = QLabel(text)
        label.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-family: 'Inter'; "
            f"font-size: 13px; border: none;"
        )
        return label

    def _summary_row(self, layout: QVBoxLayout, title: str) -> QLabel:
        """Строка сметы."""
        row = QHBoxLayout()
        t = QLabel(title)
        t.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-family: 'Inter'; "
            f"font-size: 13px; border: none;"
        )
        row.addWidget(t)
        row.addStretch()

        v = QLabel("0 ₽")
        v.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 13px; font-weight: 500; border: none;"
        )
        row.addWidget(v)
        layout.addLayout(row)
        return v

    def _divider(self) -> QFrame:
        """Разделитель."""
        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet(f"background-color: {COLOR_BORDER}; border: none;")
        return line

    def _input_style(self) -> str:
        """QSS для полей."""
        return f"""
            QDoubleSpinBox, QComboBox, QDateEdit, QTimeEdit {{
                background-color: {COLOR_CARD};
                border: 1px solid {COLOR_BORDER};
                border-radius: 6px;
                padding: 8px 12px;
                font-family: 'Inter';
                font-size: 14px;
                color: {COLOR_TEXT_PRIMARY};
            }}
            QDoubleSpinBox:focus, QComboBox:focus, QDateEdit:focus, QTimeEdit:focus {{
                border: 2px solid {COLOR_PRIMARY};
            }}
        """

    def _button_style(self) -> str:
        """QSS кнопки."""
        return f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: white;
                border: none;
                border-radius: 8px;
                font-family: 'Inter';
                font-size: 15px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #0F766E; }}
        """

    def _load_clients(self) -> None:
        """Загружает клиентов."""
        self.client_combo.clear()
        clients = self.client_repo.get_all()
        for c in clients:
            self.client_combo.addItem(c.name, c.client_id)
        if clients:
            self._on_client_changed()

    def _small_button_style(self) -> str:
        """QSS для маленькой кнопки +."""
        return f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: white;
                border: none;
                border-radius: 6px;
                font-family: 'Inter';
                font-size: 20px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #0F766E; }}
        """

    def _on_new_client(self) -> None:
        """Открывает модалку создания клиента."""
        from src.views.clients.client_form_dialog import ClientFormDialog

        dialog = ClientFormDialog(parent=self)
        if dialog.exec_() == dialog.Accepted:
            data = dialog.get_data()
            client = self.client_repo.create(**data)
            print(f"[CalculatorView] Создан клиент: {data['name']}")
            self._load_clients()
            idx = self.client_combo.findData(client.client_id)
            if idx >= 0:
                self.client_combo.setCurrentIndex(idx)

    def _on_new_object(self) -> None:
        """Открывает модалку создания объекта."""
        from src.views.clients.object_form_dialog import ObjectFormDialog

        client_id = self.client_combo.currentData()
        if not client_id:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите клиента")
            return

        dialog = ObjectFormDialog(client_id=client_id, parent=self)
        if dialog.exec_() == dialog.Accepted:
            data = dialog.get_data()
            obj = self.object_repo.create(**data)
            print(f"[CalculatorView] Создан объект: {data['address']}")
            self._on_client_changed()
            idx = self.object_combo.findData(obj.object_id)
            if idx >= 0:
                self.object_combo.setCurrentIndex(idx)

    def _on_client_changed(self) -> None:
        """Загружает объекты клиента."""
        self.object_combo.clear()
        client_id = self.client_combo.currentData()
        if not client_id:
            return
        objects = self.object_repo.get_by_client(client_id)
        for o in objects:
            label = f"{o.address} ({float(o.area):.0f} м²)"
            self.object_combo.addItem(label, o.object_id)
        if objects:
            self.area_input.setValue(float(objects[0].area))

    def _on_object_changed(self) -> None:
        """Обновляет площадь."""
        object_id = self.object_combo.currentData()
        if not object_id:
            return
        obj = self.object_repo.get_by_id(object_id)
        if obj:
            self.area_input.setValue(float(obj.area))

    def _recalculate(self) -> None:
        """Пересчитывает смету."""
        data = CalculationInput(
            area=self.area_input.value(),
            cleaning_type=self.cleaning_type.currentData(),
            urgency_coef=self.urgency.value(),
            dirt_coef=self.dirt.value(),
            transport_cost=self.transport.value(),
            discount=self.discount.value(),
        )
        result = self.calculator.calculate(data)
        self._last_result = result

        self.base_label.setText(f"{result.base_price:,.2f} ₽")
        self.tariff_label.setText(f"{result.tariff:,.0f} ₽/м²")
        self.subtotal_label.setText(f"{result.subtotal:,.2f} ₽")
        self.items_label.setText(f"{result.items_sum:,.2f} ₽")
        self.transport_label.setText(f"{result.transport_cost:,.2f} ₽")
        self.discount_label.setText(f"− {result.discount:,.2f} ₽")
        self.total_label.setText(f"{result.total:,.2f} ₽")

    def _on_save(self) -> None:
        """Сохраняет заказ."""
        client_id = self.client_combo.currentData()
        object_id = self.object_combo.currentData()

        if not client_id:
            QMessageBox.warning(self, "Ошибка", "Выберите клиента")
            return
        if not object_id:
            QMessageBox.warning(self, "Ошибка", "Выберите объект")
            return

        d_q = self.date_edit.date()
        t_q = self.time_edit.time()

        dto = {
            "client_id": client_id,
            "object_id": object_id,
            "cleaning_type": self.cleaning_type.currentData(),
            "area": self.area_input.value(),
            "urgency_coef": self.urgency.value(),
            "dirt_coef": self.dirt.value(),
            "discount": self.discount.value(),
            "total_price": self._last_result.total if self._last_result else 0.0,
            "planned_date": date(d_q.year(), d_q.month(), d_q.day()),
            "planned_start": time(t_q.hour(), t_q.minute()),
            "notes": None,
        }

        print(f"[CalculatorView] Сохранение: {dto}")
        self.save_requested.emit(dto)
