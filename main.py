from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line, Triangle, Ellipse
import math

def to_fraction_str(val):
    if val <= 0:
        return '0"'
    whole = int(math.floor(val))
    rem = val - whole
    eighths = int(round(rem * 8))
    
    if eighths == 0:
        return f'{whole}"'
    if eighths == 8:
        return f'{whole + 1}"'
        
    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a

    div = gcd(eighths, 8)
    num = eighths // div
    den = 8 // div
    
    if whole > 0:
        return f'{whole} {num}/{den}"'
    return f'{num}/{den}"'

class CobraTapeWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.target_val = 4.25
        self.bind(pos=self.redraw, size=self.redraw)

    def set_target(self, val):
        self.target_val = max(0.0, val)
        self.redraw()

    def redraw(self, *args):
        self.canvas.clear()
        w = self.width
        h = self.height
        if w < 50 or h < 20:
            return

        window_span = 3.0
        start_inch = max(0.0, self.target_val - (window_span / 2.0))
        pixels_per_inch = w / window_span

        with self.canvas:
            # 1. Yellow Tape Body
            Color(0.99, 0.88, 0.28, 1)
            tape_y = self.y + 10
            tape_h = h - 20
            Rectangle(pos=(self.x, tape_y), size=(w, tape_h))

            # 2. Cobra 7-lines / inch ticks
            Color(0.06, 0.09, 0.16, 1)
            total_eighths = int(window_span * 8) + 2
            first_eighth_idx = int(start_inch * 8)

            for i in range(total_eighths + 2):
                cur_8 = first_eighth_idx + i
                cur_inch_val = cur_8 / 8.0
                x_pos = self.x + (cur_inch_val - start_inch) * pixels_per_inch

                if x_pos < self.x or x_pos > (self.x + w):
                    continue

                sub_idx = cur_8 % 8
                if sub_idx == 0:
                    Line(points=[x_pos, tape_y + tape_h, x_pos, tape_y + tape_h - 35], width=2)
                elif sub_idx == 4:
                    Line(points=[x_pos, tape_y + tape_h, x_pos, tape_y + tape_h - 24], width=1.5)
                elif sub_idx in (2, 6):
                    Line(points=[x_pos, tape_y + tape_h, x_pos, tape_y + tape_h - 16], width=1.2)
                else:
                    Line(points=[x_pos, tape_y + tape_h, x_pos, tape_y + tape_h - 10], width=1.0)

            # 3. Red Laser Pointer
            red_x = self.x + (self.target_val - start_inch) * pixels_per_inch
            if self.x <= red_x <= (self.x + w):
                Color(0.86, 0.15, 0.15, 1)
                Line(points=[red_x, self.y, red_x, self.y + h], width=2.5)
                Triangle(points=[red_x - 8, self.y + h, red_x + 8, self.y + h, red_x, self.y + h - 14])
                Ellipse(pos=(red_x - 4, tape_y + 12), size=(8, 8))

class MasterTapeApp(App):
    def build(self):
        self.calc_expr = "38"
        self.active_val = 38.0
        self.active_mark = (38.0 / 8.0) - 0.5
        self.active_label = 'Cap Drop (1/8 - 1/2")'

        root = BoxLayout(orientation='vertical', padding=10, spacing=6)

        self.lbl_display = Label(text='38" = 96.5 cm', font_size='22sp', size_hint_y=0.08, color=(0.96, 0.62, 0.04, 1), bold=True)
        root.add_widget(self.lbl_display)

        self.lbl_target = Label(text=f'{self.active_label} : {to_fraction_str(self.active_mark)}', font_size='16sp', size_hint_y=0.06, color=(0.9, 0.2, 0.2, 1), bold=True)
        root.add_widget(self.lbl_target)

        self.tape_widget = CobraTapeWidget(size_hint_y=0.18)
        root.add_widget(self.tape_widget)

        # Scale Buttons Grid
        scale_grid = GridLayout(cols=2, spacing=4, size_hint_y=0.32)
        scales = [
            ("1/2 (Halves)", 2.0), ("1/3 (3rds)", 3.0),
            ("1/4 (4ths)", 4.0),   ("1/6 (6ths)", 6.0),
            ("1/8 (8ths)", 8.0),   ("1/12 (12ths)", 12.0),
            ("1/16 (16ths)", 16.0),("1/24 (24ths)", 24.0),
            ("Cap Drop (-1/2\")", 'cap'), ("Bicep (-1/2\")", 'bic')
        ]
        for name, div in scales:
            btn = Button(text=name, font_size='12sp', background_color=(0.12, 0.16, 0.23, 1), color=(0.22, 0.74, 0.97, 1), bold=True)
            btn.bind(on_press=lambda inst, n=name, d=div: self.on_scale_click(n, d))
            scale_grid.add_widget(btn)
        root.add_widget(scale_grid)

        # Numpad & Operators
        pad_grid = GridLayout(cols=4, spacing=4, size_hint_y=0.36)
        pad_keys = [
            ('C', (0.9, 0.2, 0.2, 1)), ('(', (0.2, 0.25, 0.33, 1)), (')', (0.2, 0.25, 0.33, 1)), ('/', (0.96, 0.62, 0.04, 1)),
            ('7', (0.06, 0.09, 0.16, 1)), ('8', (0.06, 0.09, 0.16, 1)), ('9', (0.06, 0.09, 0.16, 1)), ('*', (0.96, 0.62, 0.04, 1)),
            ('4', (0.06, 0.09, 0.16, 1)), ('5', (0.06, 0.09, 0.16, 1)), ('6', (0.06, 0.09, 0.16, 1)), ('-', (0.96, 0.62, 0.04, 1)),
            ('1', (0.06, 0.09, 0.16, 1)), ('2', (0.06, 0.09, 0.16, 1)), ('3', (0.06, 0.09, 0.16, 1)), ('+', (0.96, 0.62, 0.04, 1)),
            ('0', (0.06, 0.09, 0.16, 1)), ('.', (0.06, 0.09, 0.16, 1)), ('+1/2', (0.01, 0.52, 0.78, 1)), ('=', (0.06, 0.72, 0.5, 1))
        ]
        for key, col in pad_keys:
            btn = Button(text=key, font_size='16sp', background_color=col, bold=True)
            btn.bind(on_press=lambda inst, k=key: self.on_pad_click(k))
            pad_grid.add_widget(btn)
        root.add_widget(pad_grid)

        return root

    def on_pad_click(self, key):
        if key == 'C':
            self.calc_expr = "0"
        elif key == '=':
            try:
                res = eval(self.calc_expr)
                self.calc_expr = str(round(res, 3))
                self.active_val = float(res)
            except:
                self.calc_expr = "Error"
        elif key == '+1/2':
            try:
                res = eval(self.calc_expr) + 0.5
                self.calc_expr = str(round(res, 3))
                self.active_val = float(res)
            except:
                pass
        else:
            if self.calc_expr in ("0", "Error"):
                self.calc_expr = key
            else:
                self.calc_expr += key

        try:
            self.active_val = float(eval(self.calc_expr))
            self.lbl_display.text = f"{self.calc_expr}\" = {(self.active_val*2.54):.1f} cm"
        except:
            pass

        self.on_scale_click(self.active_label, 'cap')

    def on_scale_click(self, name, div):
        self.active_label = name
        if div == 'cap':
            self.active_mark = (self.active_val / 8.0) - 0.5
        elif div == 'bic':
            self.active_mark = (self.active_val / 4.0) - 0.5
        else:
            self.active_mark = self.active_val / div

        self.lbl_target.text = f"{name} : {to_fraction_str(self.active_mark)}"
        self.tape_widget.set_target(self.active_mark)

if __name__ == '__main__':
    MasterTapeApp().run()
