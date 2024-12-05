import showcaser
import exceptions

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

class SettingsPopup(QWidget):
    def __init__(self, main, parent=None):
        super(SettingsPopup, self).__init__(parent)

        #self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        #self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.main = main
        
        self.setWindowTitle("Настройки")
        self.setWindowIcon(QIcon('donut_devs.png'))
        
        self.setStyleSheet('''
                              QLabel {color: #C5705D; font: bold 18px}
                              QWidget{background-color: #DFD3C3;}
                              QLineEdit {selection-color: #F8EDE3; selection-background-color: #C5705D;}
                              QPushButton {selection-color: #F8EDE3; selection-background-color: #C5705D;}
                           ''')

        self.left_text = QLabel("a: ")
        self.right_text = QLabel("b: ")
        self.number_text = QLabel("eps: ")
        
        self.left_text.setFixedWidth(40)
        self.right_text.setFixedWidth(40)
        self.number_text.setFixedWidth(40)
        
        self.setFixedSize(QSize(300,300))
        
        self.left_border = QLineEdit(str(main.a))
        self.left_border.setFixedWidth(100)
        
        self.right_border = QLineEdit(str(main.b))
        self.right_border.setFixedWidth(100)

        self.number_input = QLineEdit(str(main.eps))
        self.number_input.setFixedWidth(100)

        self.extremum_min_button = QRadioButton("Искать точку минимума")
        self.extremum_max_button = QRadioButton("Искать точку максимума")
        
        if self.main.extremum_bool: self.extremum_min_button.toggle()
        else: self.extremum_max_button.toggle()
            

        self.extremum_min_button.toggled.connect(lambda x: self.set_extremum_bool(True))
        self.extremum_max_button.toggled.connect(lambda x: self.set_extremum_bool(False))
        
        self.save_button = QPushButton('Сохранить')
        self.save_button.pressed.connect(self.set_bounds)

        self.showcase_switch = QCheckBox("Показать работу метода")
        self.showcase_switch.setChecked(self.main.showcase_mode)
        self.showcase_switch.stateChanged.connect(self.start_showcase)
        self.showcase_switch.stateChanged.connect(self.set_showcase_mode)
        
        layout = QFormLayout()
        left = QHBoxLayout()
        right = QHBoxLayout()
        num = QHBoxLayout()
        
        left.addWidget(self.left_text)
        left.addWidget(self.left_border)

        right.addWidget(self.right_text)
        right.addWidget(self.right_border)

        num.addWidget(self.number_text)
        num.addWidget(self.number_input)
        
        layout.addRow(left)
        layout.addRow(right)
        layout.addRow(num)
        layout.addWidget(self.extremum_min_button)
        layout.addWidget(self.extremum_max_button)
        layout.addWidget(self.save_button)
        layout.addWidget(self.showcase_switch)

        self.setLayout(layout)

    def set_extremum_bool(self, boolean):
        if boolean: self.main.extremum_label.setText("Xmin: ")
        else: self.main.extremum_label.setText("Xmax: ")
        
        self.main.extremum_bool = boolean
        self.main.make_extremum_point(self.main.get_selected_function())
        
    def set_bounds(self):
        #exception IncorrectRangeException
        #exception InvalidNumAmount
        try:
            a = float(self.left_border.text())
            b = float(self.right_border.text())
            eps = float(self.number_input.text())

            if a == self.main.a and b == self.main.b:
                needToRedraw = False
            else:
                needToRedraw = True
                
            if(a > b): raise exceptions.InvalidRangeException
            if(eps <= 0): raise exceptions.InvalidNumberException
               
            self.main.a = a
            self.main.b = b
            self.main.eps = eps

            QMessageBox.information(None, "Успех", "Значения были изменены!")

            self.main.make_extremum_point(self.main.get_selected_function())
            self.main.make_borders()
            self.main.draw_function(self.main.get_selected_function(), needToRedraw)
            
            #self.closeEvent(QEvent.Type.Close)

        except exceptions.InvalidRangeException:
            QMessageBox.critical(None, "Ошибка", "Значение 'a' дожно быть строго больше 'b'.")
            print("DEBUG: значение 'a' дожно быть строго больше 'b'.")

        except exceptions.InvalidNumberException:
            QMessageBox.critical(None, "Ошибка", "Значение 'eps' должно быть строго больше 0.")
            print("DEBUG: погрешность 'eps' должна быть больше 0.")

        except ValueError:
            QMessageBox.critical(None, "Ошибка", "Использованы нечисловые символы.")
            print("DEBUG: Использованы нечисловые символы")
            
    def set_showcase_mode(self):
        self.main.showcase_mode = self.showcase_switch.isChecked()
    
    def start_showcase(self):
        if self.showcase_switch.isChecked() and len(self.main.lines) == 0:
            self.sc = showcaser.Showcaser(self.main)
            self.sc.current_x.connect(self.main.draw_line)
            self.sc.draw_a.connect(self.main.draw_line)
            self.sc.draw_b.connect(self.main.draw_line)
            self.sc.delete_signal.connect(self.main.delete_line)
            self.sc.start()
            

    def closeEvent(self, event):
        self.main.showcase_mode = False
        self.main.settings_opened = False
        self.close()
