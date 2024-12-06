import exceptions
import settings
import showcaser
import helpy

import sys
import random
import time
import numpy

from math import fabs, sqrt

from sympy import sympify, symbols
from sympy.parsing.sympy_parser import parse_expr
     
import pyqtgraph as pg
from PyQt6.QtGui import QIcon, QFont, QMouseEvent
from PyQt6.QtCore import QSize, Qt, QRect
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QLineEdit,
    QWidget,
    QHBoxLayout,
    QFormLayout,
    QComboBox,
    QPushButton,
    QStyle,
    QStyleFactory,
    QCheckBox,
    QMessageBox
)

class Graph(pg.PlotWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        
    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if event.buttons() == Qt.MouseButton.NoButton:
            self.main.change_bg_fading_color(event.pos().x()+14, event.pos().y()+100)
            
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet('''
                              QLabel {color: #C5705D; font: bold 18px;}
                              QWidget{background-color: #DFD3C3;}
                              QLineEdit {selection-color: #F8EDE3; selection-background-color: #C5705D;}
                              QPushButton {selection-color: #F8EDE3; selection-background-color: #C5705D;}
                           ''')
        self.setWindowIcon(QIcon('donut_devs.png'))
        print(QStyleFactory.keys())

        #Свойства, переменные и тд
        self.a = -5
        self.b = 5
        self.eps = 0.001
        self.extremum_bool = True
        self.showcase_mode = False
        self.settings_opened = False
        self.help_opened = False
        self.selected_expoint = None
        self.settings_window = None
        self.help_window = None
        self.lines = []
        self.borders = []
        #self.last_positions = [ [x,y,scalex, scaley] ]
        
        self.setWindowTitle("Нахождение локального экстремума")
        
        self.top_label = QLabel()
        self.top_label.setText("Метод Фиббоначи\n")
        self.top_label.setMouseTracking(True)
        self.top_label.setAlignment(Qt.AlignmentFlag.AlignBottom)

        self.help_button = QPushButton("?")
        self.help_button.setMouseTracking(True)
        self.help_button.setFixedSize(24, 24)
        self.help_button.released.connect(self.open_help)

        #Header
        self.n_label = QLabel()
        self.n_label.setText("Количество вычислений целевой функции (N) по заданной точности (eps): ")
        self.n_label.setStyleSheet('color: #000000; font: 18px')
        self.n_label.setMouseTracking(True)
        
        self.extremum_label = QLabel()
        self.extremum_label.setText("Xmin: ")
        self.extremum_label.setStyleSheet('color: #000000; font: 18px')
        self.extremum_label.setMouseTracking(True)

        self.n_value_label = QLabel()
        self.n_value_label.setText("-")
        self.n_value_label.setStyleSheet('color: #000000; font: bold 18px')
        self.n_value_label.setMouseTracking(True)

        self.extremum_value_label = QLabel()
        self.extremum_value_label.setText("нет значения")
        self.extremum_value_label.setStyleSheet('color: #000000; font: bold 18px')
        self.extremum_value_label.setMouseTracking(True)

        self.y_extremum_label = QLabel()
        self.y_extremum_label.setText("f(Xmin): ")
        self.y_extremum_label.setStyleSheet('color: #000000; font: 18px')
        self.y_extremum_label.setMouseTracking(True)
        self.y_extremum_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.y_extremum_value_label = QLabel()
        self.y_extremum_value_label.setText("не определено")
        self.y_extremum_value_label.setStyleSheet('color: #000000; font: bold 18px')
        self.y_extremum_value_label.setMouseTracking(True)
        self.y_extremum_value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        #График
        self.pw = Graph(self)
        self.pw.hideButtons()
        self.pw.setBackground('#F8EDE3')
        self.pw.showGrid(x=True, y=True, alpha=1)
        self.pw_list = {}
        self.pw.setMouseTracking(True)
        
        #Нижняя линия (строка и выбор функций)
        self.function_box = QComboBox()
        self.function_box.setStyleSheet("combobox-popup: 0")
        self.function_box.setMaxCount(15)
        self.function_box.setMinimumContentsLength(10)
        self.function_box.setMaxVisibleItems(10)
        self.function_box.activated.connect(lambda: self.draw_function(parse_expr(self.function_box.currentText(), transformations="all")))
        self.function_box.setMouseTracking(True)

        #Занесение 3 функций-примеров, рисование первой функции
        self.function_box.addItem("x^2", [-5, 5])
        self.function_box.addItem("3x^4 - 4x^3 - 12x^2 - 2", [-5, 5])
        self.function_box.addItem("x - x^3/6 + x^5/120", [-5, 5])
        self.draw_function(self.get_selected_function())
        
        self.function_input = QLineEdit()
        self.function_input.returnPressed.connect(self.add_new_function)
        self.function_input.setPlaceholderText("5x + 3")
        self.function_input.setMouseTracking(True)
        
        self.delete_button = QPushButton("Удалить функцию")
        self.delete_button.released.connect(self.delete_function)
        self.delete_button.setMouseTracking(True)
        
        self.settings_button = QPushButton("Настройки")
        self.settings_button.released.connect(self.open_settings)
        self.settings_button.setMouseTracking(True)

        #Лейауты
        layout_header = QHBoxLayout()
        layout_top = QFormLayout()
        layout_bottom = QHBoxLayout()
        layout_n = QHBoxLayout()
        layout_extremum = QHBoxLayout()
        
        #Размещение виджетов на экране
        layout_header.addWidget(self.top_label)
        layout_header.addWidget(self.help_button)
        layout_header.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        layout_bottom.addWidget(self.function_box)
        layout_bottom.addWidget(self.function_input)
        layout_bottom.addWidget(self.delete_button)
        layout_bottom.addWidget(self.settings_button)

        layout_n.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout_n.addWidget(self.n_label)
        layout_n.addWidget(self.n_value_label)

        layout_extremum.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout_extremum.addWidget(self.extremum_label)
        layout_extremum.addWidget(self.extremum_value_label)
        layout_extremum.addWidget(self.y_extremum_label)
        layout_extremum.addWidget(self.y_extremum_value_label)
        
        widget = QWidget()
        widget.setLayout(layout_top)

        layout_top.addRow(layout_header)
        layout_top.addRow(layout_n)
        layout_top.addRow(layout_extremum)
        layout_top.addWidget(self.pw)
        layout_top.addRow(layout_bottom)

        self.setMouseTracking(True)
        self.setCentralWidget(widget)
        widget.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.NoButton:
            self.change_bg_fading_color(event.pos().x(), event.pos().y())
        else:
            pass
        
    def open_settings(self):
        print(self.settings_opened)
        if(not(self.settings_opened)):
            print("executed")
            self.settings_opened = True
            self.settings_window = settings.SettingsPopup(self)
            
            self.settings_window.show()
            print(self.settings_opened)
        
        else:
            if self.settings_window.windowState() == Qt.WindowState.WindowActive or self.settings_window.windowState() == Qt.WindowState.WindowNoState:
                self.settings_window.setWindowState(Qt.WindowState.WindowMinimized)
            else:
                self.settings_window.setWindowState(Qt.WindowState.WindowActive)
            
    def open_help(self):
        print(self.help_opened)
        if(not(self.help_opened)):
            print("executed")
            self.help_opened = True
            self.help_window = helpy.HelpPopup(self)
            
            self.help_window.show()
            print(self.help_opened)
        
        else:
            if self.help_window.windowState() == Qt.WindowState.WindowActive or self.help_window.windowState() == Qt.WindowState.WindowNoState:
                self.help_window.setWindowState(Qt.WindowState.WindowMinimized)
            else:
                self.help_window.setWindowState(Qt.WindowState.WindowActive)

    def get_typed_function(self):
        print("че за Х")
        try:
            s = parse_expr(self.function_input.text(), transformations="all")
            
        except:
            print("DEBUG: Функция задана не по правилам!")
            s = 0
            
        return s
    
    def get_selected_function(self): 
        return parse_expr(self.function_box.currentText(), transformations="all")

    def get_function_values(self, equation):
        x = symbols('x')
        
        data_row = []
        for i in numpy.arange(self.a, self.b+0.1, 0.1):
            y = float(equation.subs(x, i))
            data_row.append(y)
                
        return data_row

    def draw_function(self, equation, byForce=False):
        self.showcase_mode = False
        self.pw.enableAutoRange(self.pw.getViewBox().XYAxes, True)
        if len(self.pw_list) > 0:
            self.pw.clear()
            
        x = symbols('x')

        if equation in self.pw_list.keys() and not byForce:
            self.pw.addItem(self.pw_list[equation])
            self.make_borders()
            self.make_extremum_point(equation)

        else:
            pen = pg.mkPen(color=(random.randint(0,255), random.randint(0,255), random.randint(0,255)), width=4)
            
            try:
                data_row = self.get_function_values(equation)
                
            except TypeError:
                QMessageBox.critical(None, "Ошибка", "привет")
                self.function_box.removeItem(self.function_box.findText(self.function_box.currentText()))
                return
            
            self.pw_list[equation] = self.pw.plot(numpy.arange(self.a, self.b+0.1, 0.1), data_row, pen=pen)

            self.make_extremum_point(equation)
            self.make_borders()

    def make_borders(self):
        if len(self.borders) != 0:
            for border in self.borders:
                self.pw.removeItem(border)
            
        red_pen = pg.mkPen(color=(200, 0, 0), width=4, style=Qt.PenStyle.DotLine)

        max_length = max(self.get_function_values(self.get_selected_function()))

        self.borders.append(self.pw.plot([self.a, self.a], [max_length*(-1), max_length], pen=red_pen, skipFiniteCheck = True))
        self.borders.append(self.pw.plot([self.b, self.b], [max_length*(-1), max_length], pen=red_pen, skipFiniteCheck = True))
    
    def make_extremum_point(self, equation):
        for item in self.pw.items():
            if type(item) is pg.ScatterPlotItem:
                self.pw.removeItem(item)

        x = symbols('x')
        
        result = self.fib_method(equation, self.extremum_bool)
        m = result[0]
        n = result[1]

        numbers_after_dot = len(str(self.eps))-2
        if numbers_after_dot >= 0:
            formatted_value = '{0:.' +  str(numbers_after_dot) + 'f}'
        else:
            formatted_value = '1'
        self.n_value_label.setText(str(n))
        self.extremum_value_label.setText(formatted_value.format(m))
        self.y_extremum_value_label.setText(formatted_value.format(equation.subs(x, m)))
        
        scatter = pg.ScatterPlotItem(hoverable=True, tip='x: {x:.3g}\ny: {y:.3g}\ndata={data}'.format)
        
        scatter.sigClicked.connect(self.select_extremum_point)
        
        scatter.addPoints([m], [equation.subs(x, m)])
        self.pw.addItem(scatter)

    def select_extremum_point(self, clicked_point):
        brush_selected = pg.mkBrush(color=(255, 0, 0))
        brush_normal = pg.mkBrush(color=(50, 50, 50))
         
        if(self.selected_expoint != None):
            self.selected_expoint.setBrush(brush_normal)
            
        if(self.selected_expoint == clicked_point):
            self.selected_expoint = None
            return
        
        self.selected_expoint = clicked_point
        self.selected_expoint.setBrush(brush_selected)
        print("Hello")
            
    def add_new_function(self):
        if self.function_box.findText(self.function_input.text()) != -1:
            return
        
        equation = self.get_typed_function()

        if equation == 0:
            QMessageBox.critical(None, "Ошибка", "Неправильный формат функции")
            return
        print(self.function_box.count())
        if self.function_box.maxCount() == self.function_box.count():
            QMessageBox.critical(None, "Ошибка", f"Добавлять в список можно максимум {self.function_box.maxCount()} функций!\nДля того, чтобы добавить новую функцию, удалите прежние.")
            return
            
        self.function_box.addItem(self.function_input.text(), [self.a, self.b])
        self.function_box.setCurrentText(self.function_input.text())
        self.draw_function(equation)
        self.function_input.clear()
        
    def delete_function(self):
        self.showcase_mode = False

        try:
            item_to_remove = self.function_box.currentText()
            self.pw.removeItem(self.pw_list.pop(parse_expr(item_to_remove, transformations='all')))
                
            print(self.function_box.currentText() + " removed")
            self.function_box.removeItem(self.function_box.currentIndex())

            if(self.function_box.currentIndex() != -1):
                self.draw_function(parse_expr(self.function_box.currentText(), transformations='all'))
            print(self.pw_list)
            
        except:
            pass
        
    def draw_line(self, x, offset_y, pen=None):
        if pen == None:
            pen = pg.mkPen(color=(random.randint(0,255), random.randint(0,255), random.randint(0,255)), width=4)

        max_length = max(self.get_function_values(self.get_selected_function()))
        self.lines.append(self.pw.plot([x, x], [max_length*(-1)+offset_y, max_length+offset_y], pen=pen, skipFiniteCheck = True))
        
    def delete_line(self):
        while(len(self.lines) > 0):
            self.pw.removeItem(self.lines.pop())

    def change_bg_fading_color(self, mpos_x, mpos_y):

        size_avg = (self.size().height() + self.size().width()) / 2
        change = ((mpos_x - self.size().width()/2)**2 + (mpos_y - self.size().height()/2)**2) ** 0.5
        #print(self.size().height(), self.size().width(), mpos_y, mpos_x, change)
        
        r = hex(223 - int(change/(size_avg/(256-223)*2)))
        g = hex(211 - int(change/(size_avg/(256-211)*2)))
        b = hex(195 - int(change/(size_avg/(256-195)*2)))

        r1 = hex(248 - int(change/(size_avg/(256-223)*4)))
        g1 = hex(237 - int(change/(size_avg/(256-211)*4)))
        b1 = hex(227 - int(change/(size_avg/(256-195)*4)))

        r2 = hex(197 - int(change/(size_avg/(256-223))))
        g2 = hex(112 - int(change/(size_avg/(256-223))))
        b2 = hex(93 - int(change/(size_avg/(256-223))))

        bg_color = "QWidget{background-color: #" + (str(r[2:]) + str(g[2:]) + str(b[2:])).upper() + ";}"
        pw_color = "#" + (str(r1[2:]) + str(g1[2:]) + str(b1[2:])).upper()
        label_color = "QLabel {color: #" + (str(r2[2:]) + str(g2[2:]) + str(b2[2:])).upper() + "; font: bold 18px;}"
        
        self.pw.setBackground(pw_color)
        self.setStyleSheet(bg_color + "QLineEdit {selection-color: #F8EDE3; selection-background-color: #C5705D;} QPushButton {selection-color: #F8EDE3; selection-background-color: #C5705D;}" + label_color)
        pass

    def fib_method(self, eq, find_minimum=True, n=10):
        fib = [1, 1]
        x = symbols('x')
        equation = eq
        wanted_eps = self.eps
            
        for i in range(2, n+2):
            fib.append(fib[i-1] + fib[i-2])

        a = self.a
        b = self.b

        estimated_eps = (b-a)/fib[n+1]

        if wanted_eps < estimated_eps:
            print(wanted_eps, estimated_eps)
            return self.fib_method(equation, find_minimum, n+1)

        else:
            for i in range(2, n):
                x1 = a + ((b-a)*fib[n-i+1]/fib[n-i+3])
                x2 = a + ((b-a)*fib[n-i+2]/fib[n-i+3])

                y1 = float(equation.subs(x, x1))
                y2 = float(equation.subs(x, x2))

                if find_minimum:
                    if(y1 <= y2):
                        b = x2
                    else:
                        a = x1

                else:
                    if(y1 > y2):
                        b = x2
                    else:
                        a = x1
                        
            return [(a+b)/2, n]

sf_pro = QFont("SF Pro Text")
app = QApplication(sys.argv)
app.setStyle("Fusion")
app.setFont(sf_pro)
window = MainWindow()
window.show()

app.exec()
