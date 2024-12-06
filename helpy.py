from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize, QEvent
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QMessageBox,
    QHBoxLayout,
    QFormLayout,
    QRadioButton
)

class HelpPopup(QWidget):
    def __init__(self, main):
        super(HelpPopup, self).__init__()

        self.main = main
        self.setWindowTitle("Помощь")
        self.setWindowIcon(QIcon('donut_devs.png'))       

        self.setStyleSheet('''
                              QWidget{background-color: #DFD3C3;}
                              QLineEdit {selection-color: #F8EDE3; selection-background-color: #C5705D;}
                              QPushButton {selection-color: #F8EDE3; selection-background-color: #C5705D;}
                           ''')

        self.help_text = QLabel()
        self.help_text.setWordWrap(True)
        self.help_text.setText(
            """
<b>Правила задания функции</b><br>
    - В поле ввода нужно задавать уравнение, зависимое от переменной x. Любые другие символы переменных (y, z, t) использовать нельзя.<br>
    - Не обязательно ставить знак умножения между переменной и ее коэффициентом<br>
<br>
<b>Обозначения операций</b><br>
    - Базовые операции: <b>+ - * /</b><br>
    - Возведение A в степень B+5: <b>A^(B+5)</b><br>
    - Квадратный корень: <b>sqrt()</b><br>
    - Синус: <b>sin()</b><br>
    - Косинус: <b>cos()</b><br>
    - Тангенс: <b>tan()</b><br>
    - Котангенс: <b>cotan()</b><br>
    - Число е в степени N, где n - любое выражение: <b>exp(N)</b><br>
    - Неопределенный интеграл: <b>integrate()</b>
    

            """
            )

        self.side_text = QLabel()
        self.side_text.setWordWrap(True)
        self.side_text.setText(
            """
<b>Изменение параметров</b><br>
- Изменить границы функции и начальное приближение<br>
- Выбрать поиск максимума/минимума функции<br>
- Графически отобразить работу метода<br>
Все это можно сделать в <b>Настройках!</b> Нажмите на кнопку <br>Настройки</b> в <b>левом нижнем углу</b>.
            """
            )
        
        layout = QFormLayout()
        labels = QHBoxLayout()
        labels.addWidget(self.help_text)
        labels.addWidget(self.side_text)
        layout.addRow(labels)
        self.setLayout(layout)
        
    def closeEvent(self, event):
        self.main.help_opened = False
        self.close()
