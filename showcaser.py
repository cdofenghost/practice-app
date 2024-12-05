import pyqtgraph as pg
import random, numpy, time

from sympy import sympify, symbols

from PyQt6.QtCore import QThread, pyqtSignal

class Showcaser(QThread):

    current_x = pyqtSignal(object, object)
    draw_a = pyqtSignal(object, object, object)
    draw_b = pyqtSignal(object, object, object)
    delete_signal = pyqtSignal()
    
    def __init__(self, main):
        super().__init__()
        self.main = main
        self.timeframe = None

    def run(self):
        dots = self.fib_method()
        
        equation = self.main.get_selected_function()
        
        x = symbols('x')
        
        current_a = self.main.a
        current_b = self.main.b

        while(self.main.showcase_mode):
            c = 0
            for dot in dots:
                c += 1
                
                print(c)
                if(not(self.main.showcase_mode)):
                    break       
                print(dot)
                
                if abs(current_a-dot) < abs(current_b-dot):
                    current_a = dot
                else:
                    current_b = dot
                    
                self.draw_a.emit(current_a, float(equation.subs(x, dot)), pg.mkPen(color=(255, 0, 0), width=4))
                self.draw_b.emit(current_b, float(equation.subs(x, dot)), pg.mkPen(color=(255, 0, 0), width=4))

                self.current_x.emit((current_b+current_a)/2, float((current_a+current_b)/2))
                
                time.sleep(self.timeframe)
                
                self.delete_signal.emit()
                self.delete_signal.emit()
                self.delete_signal.emit()

    def fib_method(self, n=10):
        fib = [1, 1]
        x = symbols('x')
        equation = self.main.get_selected_function()
        
        wanted_eps = self.main.eps
        
        dots = []
        
        for i in range(2, n+2):
            fib.append(fib[i-1] + fib[i-2])

        a = self.main.pw_list[equation].getData()[0][1]-0.1
        b = self.main.pw_list[equation].getData()[0][-1]

        estimated_eps = (b-a)/fib[n+1]
            
        if wanted_eps < estimated_eps:
            return self.fib_method(n+1)
        
        else:
            self.timeframe = 10/n
            for i in range(2, n):
                x1 = a + ((b-a)*fib[n-i+1]/fib[n-i+3])
                x2 = a + ((b-a)*fib[n-i+2]/fib[n-i+3])

                y1 = float(equation.subs(x, x1))
                y2 = float(equation.subs(x, x2))
                
                #для минимума
                if self.main.extremum_bool:
                    if(y1 <= y2):
                        b = x2
                        dots.append(x2)
                    else:
                        a = x1
                        dots.append(x1)

                else:
                    if(y1 > y2):
                        b = x2
                        dots.append(x2)
                    else:
                        a = x1
                        dots.append(x1)
                        
            return dots
