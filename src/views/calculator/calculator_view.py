"""Экран калькулятора стоимости.

Реализует F-1.1–F-1.8: расчёт стоимости заказа по формуле из ТЗ.
Две колонки: слева — форма ввода, справа — живая смета.

Соответствует макету из Figma.
"""

from typing import Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.services.calculator_service import CalculatorService
from src.services.dtos import CalculationInput


# Цвета из Figma
COLOR_BG = "#F8FAFC"
COLOR_CARD = "#FFFFFF"
COLOR_BORDER = "#E2E8F0"
COLOR_TEXT_PRIMARY = "#0F172A"
COLOR_TEXT_SECONDARY = "#64748B"
COLOR_PRIMARY = "#0EA5A4"
COLOR_SUCCESS = "#22C55E"
COLOR_ERROR = "#EF4444"


class CalculatorView(QWidget):
    """Экран калькулятора.

    Signals:
        save_requested: Запрос сохранения заказа. Аргумент: dict с данными.
    """

    save_requested = pyqtSignal(dict)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализирует экран калькулятора.

        Args:
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self.calculator = CalculatorService()

        self.setStyleSheet(f"background-color: {COLOR_BG};")
        self._build_ui()
        self._recalculate()

    def _build_ui(self) -> None:
        """Собирает интерфейс."""
        main = QVBoxLayout(self)
        main.setContentsMargins(32, 32, 32, 32)
        main.setSpacing(24)

        # Заголовок
        title = QLabel("Калькулятор стоимости")
        title.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 24px; font-weight: 700;"
        )
        main.addWidget(title)

        # Две колонки
        columns = QHBoxLayout()
        columns.setSpacing(24)

        # Левая — форма
        form = self._create_form()
        columns.addWidget(form, 3)

        # Правая — смета
        summary = self._create_summary()
        columns.addWidget(summary, 2)

        main.addLayout(columns, 1)

    def _create_form(self) -> QWidget:
        """Создаёт форму ввода (левая колонка).

        Returns:
            Виджет формы.
        """
        form = QFrame()
        form.setStyleSheet(
            f"QFrame {{ background-color: {COLOR_CARD}; "
            f"border: 1px solid {COLOR_BORDER}; border-radius: 12px; }}"
        )
        layout = QVBoxLayout(form)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Площадь
        layout.addWidget(self._create_label("Площадь (м²)"))
        self.area_input = QDoubleSpinBox()
        self.area_input.setRange(1.0, 10000.0)
        self.area_input.setValue(60.0)
        self.area_input.setSuffix(" м²")
        self.area_input.setStyleSheet(self._input_style())
        self.area_input.valueChanged.connect(self._recalculate)
        layout.addWidget(self.area_input)

        # Тип уборки
        layout.addWidget(self._create_label("Тип уборки"))
        self.cleaning_type = QComboBox()
        self.cleaning_type.addItem("Поддерживающая", "maintenance")
        self.cleaning_type.addItem("Генеральная", "general")
        self.cleaning_type.addItem("После ремонта", "post_renovation")
        self.cleaning_type.addItem("Мойка окон", "windows")
        self.cleaning_type.setCurrentIndex(1)  # Генеральная по умолчанию
        self.cleaning_type.setStyleSheet(self._input_style())
        self.cleaning_type.currentIndexChanged.connect(self._recalculate)
        layout.addWidget(self.cleaning_type)

        # Коэффициенты
        coef_row = QHBoxLayout()

        coef_left = QVBoxLayout()
        coef_left.addWidget(self._create_label("Срочность"))
        self.urgency = QDoubleSpinBox()
        self.urgency.setRange(1.0, 3.0)
        self.urgency.setSingleStep(0.1)
        self.urgency.setValue(1.0)
        self.urgency.setPrefix("× ")
        self.urgency.setStyleSheet(self._input_style())
        self.urgency.valueChanged.connect(self._recalculate)
        coef_left.addWidget(self.urgency)

        coef_right = QVBoxLayout()
        coef_right.addWidget(self._create_label("Загрязнение"))
        self.dirt = QDoubleSpinBox()
        self.dirt.setRange(1.0, 3.0)
        self.dirt.setSingleStep(0.1)
        self.dirt.setValue(1.0)
        self.dirt.setPrefix("× ")
        self.dirt.setStyleSheet(self._input_style())
        self.dirt.valueChanged.connect(self._recalculate)
        coef_right.addWidget(self.dirt)

        coef_row.addLayout(coef_left)
        coef_row.addLayout(coef_right)
        layout.addLayout(coef_row)

        # Транспорт
        layout.addWidget(self._create_label("Транспортные расходы (₽)"))
        self.transport = QDoubleSpinBox()
        self.transport.setRange(0.0, 10000.0)
        self.transport.setValue(0.0)
        self.transport.setSuffix(" ₽")
        self.transport.setStyleSheet(self._input_style())
        self.transport.valueChanged.connect(self._recalculate)
        layout.addWidget(self.transport)

        # Скидка
        layout.addWidget(self._create_label("Скидка (₽)"))
        self.discount = QDoubleSpinBox()
        self.discount.setRange(0.0, 100000.0)
        self.discount.setValue(0.0)
        self.discount.setSuffix(" ₽")
        self.discount.setStyleSheet(self._input_style())
        self.discount.valueChanged.connect(self._recalculate)
        layout.addWidget(self.discount)

        layout.addStretch()
        return form

    def _create_summary(self) -> QWidget:
        """Создаёт блок сметы (правая колонка).

        Returns:
            Виджет сметы.
        """
        summary = QFrame()
        summary.setStyleSheet(
            f"QFrame {{ background-color: {COLOR_CARD}; "
            f"border: 1px solid {COLOR_BORDER}; border-radius: 12px; }}"
        )
        layout = QVBoxLayout(summary)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        # Заголовок
        header = QLabel("Смета")
        header.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 18px; font-weight: 600; border: none;"
        )
        layout.addWidget(header)

        # Разделитель
        layout.addWidget(self._divider())

        # Строки расчёта
        self.base_label = self._add_summary_row(layout, "Базовая стоимость")
        self.tariff_label = self._add_summary_row(layout, "Тариф")
        self.subtotal_label = self._add_summary_row(layout, "С коэффициентами")
        self.items_label = self._add_summary_row(layout, "Доп. услуги")
        self.transport_label = self._add_summary_row(layout, "Транспорт")
        self.discount_label = self._add_summary_row(layout, "Скидка")

        layout.addWidget(self._divider())

        # ИТОГО
        total_row = QHBoxLayout()
        total_title = QLabel("ИТОГО:")
        total_title.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 18px; font-weight: 700; border: none;"
        )
        total_row.addWidget(total_title)
        total_row.addStretch()

        self.total_label = QLabel("0 ₽")
        self.total_label.setStyleSheet(
            f"color: {COLOR_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 24px; font-weight: 700; border: none;"
        )
        total_row.addWidget(self.total_label)
        layout.addLayout(total_row)

        layout.addStretch()

        # Кнопки
        save_btn = QPushButton("Сохранить заказ")
        save_btn.setFixedHeight(44)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet(self._button_style(COLOR_PRIMARY))
        save_btn.clicked.connect(self._on_save)
        layout.addWidget(save_btn)

        export_btn = QPushButton("Экспорт PDF")
        export_btn.setFixedHeight(44)
        export_btn.setCursor(Qt.PointingHandCursor)
        export_btn.setStyleSheet(self._button_style_outline())
        layout.addWidget(export_btn)

        return summary

    def _create_label(self, text: str) -> QLabel:
        """Создаёт label для формы.

        Args:
            text: Текст.

        Returns:
            QLabel с серым текстом.
        """
        label = QLabel(text)
        label.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-family: 'Inter'; "
            f"font-size: 13px; border: none;"
        )
        return label

    def _add_summary_row(self, layout: QVBoxLayout, title: str) -> QLabel:
        """Добавляет строку в смету.

        Args:
            layout: Layout сметы.
            title: Название строки.

        Returns:
            QLabel со значением (для обновления).
        """
        row = QHBoxLayout()

        title_label = QLabel(title)
        title_label.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-family: 'Inter'; "
            f"font-size: 13px; border: none;"
        )
        row.addWidget(title_label)
        row.addStretch()

        value_label = QLabel("0 ₽")
        value_label.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 13px; font-weight: 500; border: none;"
        )
        row.addWidget(value_label)

        layout.addLayout(row)
        return value_label

    def _divider(self) -> QFrame:
        """Создаёт разделитель.

        Returns:
            QFrame-линия.
        """
        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet(f"background-color: {COLOR_BORDER}; border: none;")
        return line

    def _input_style(self) -> str:
        """QSS для полей ввода."""
        return f"""
            QDoubleSpinBox, QComboBox, QLineEdit {{
                background-color: {COLOR_CARD};
                border: 1px solid {COLOR_BORDER};
                border-radius: 6px;
                padding: 8px 12px;
                font-family: 'Inter';
                font-size: 14px;
                color: {COLOR_TEXT_PRIMARY};
                min-height: 24px;
            }}
            QDoubleSpinBox:focus, QComboBox:focus, QLineEdit:focus {{
                border: 2px solid {COLOR_PRIMARY};
            }}
        """

    def _button_style(self, color: str) -> str:
        """QSS для главной кнопки."""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                font-family: 'Inter';
                font-size: 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #0F766E; }}
        """

    def _button_style_outline(self) -> str:
        """QSS для второстепенной кнопки."""
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {COLOR_TEXT_SECONDARY};
                border: 1px solid {COLOR_BORDER};
                border-radius: 8px;
                font-family: 'Inter';
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #F1F5F9;
                color: {COLOR_TEXT_PRIMARY};
            }}
        """

    def _recalculate(self) -> None:
        """Пересчитывает смету при любом изменении полей."""
        data = CalculationInput(
            area=self.area_input.value(),
            cleaning_type=self.cleaning_type.currentData(),
            urgency_coef=self.urgency.value(),
            dirt_coef=self.dirt.value(),
            transport_cost=self.transport.value(),
            discount=self.discount.value(),
        )
        result = self.calculator.calculate(data)

        # Обновляем смету
        self.base_label.setText(f"{result.base_price:,.2f} ₽")
        self.tariff_label.setText(f"{result.tariff:,.0f} ₽/м²")
        self.subtotal_label.setText(f"{result.subtotal:,.2f} ₽")
        self.items_label.setText(f"{result.items_sum:,.2f} ₽")
        self.transport_label.setText(f"{result.transport_cost:,.2f} ₽")
        self.discount_label.setText(f"− {result.discount:,.2f} ₽")
        self.total_label.setText(f"{result.total:,.2f} ₽")

    def _on_save(self) -> None:
        """Обрабатывает сохранение заказа."""
        data = {
            "area": self.area_input.value(),
            "cleaning_type": self.cleaning_type.currentData(),
            "urgency_coef": self.urgency.value(),
            "dirt_coef": self.dirt.value(),
            "transport": self.transport.value(),
            "discount": self.discount.value(),
            "total": self.total_label.text(),
        }
        print(f"[CalculatorView] Сохранение: {data}")
        self.save_requested.emit(data)
