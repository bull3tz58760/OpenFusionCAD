from OCC.Display.backend import load_backend
load_backend("pyside6")

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QSpinBox, QListWidget, QMessageBox
)
from OCC.Display.qtDisplay import qtViewer3d
from OCC.Core.AIS import AIS_Shape
from OCC.Core.Quantity import Quantity_Color, Quantity_NOC_BLUE1
from core.sketcher import (
    make_rectangle_sketch, make_circle_sketch, extrude_sketch, revolve_sketch, make_sweep
)
import sys

class CADApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sketch Manager Editor")
        self.setGeometry(100, 100, 1200, 800)

        self.display = qtViewer3d(self)
        self.current_shape = None
        self.mode = 'rectangle'
        self.operation = 'extrude'
        self.sketches = []

        main_layout = QHBoxLayout(self)
        control_layout = QVBoxLayout()
        main_layout.addLayout(control_layout, 1)
        main_layout.addWidget(self.display, 3)

        btn_rect = QPushButton("Rectangle")
        btn_circle = QPushButton("Circle")
        btn_rect.clicked.connect(lambda: self.set_mode('rectangle'))
        btn_circle.clicked.connect(lambda: self.set_mode('circle'))
        control_layout.addWidget(btn_rect)
        control_layout.addWidget(btn_circle)

        self.inputs = {}
        self.inputs['width'] = self.create_input(control_layout, "Width", 60)
        self.inputs['height'] = self.create_input(control_layout, "Height", 40)
        self.inputs['radius'] = self.create_input(control_layout, "Radius", 25)
        self.inputs['depth'] = self.create_input(control_layout, "Depth", 30)

        btn_extrude = QPushButton("Use Extrude")
        btn_revolve = QPushButton("Use Revolve")
        btn_sweep = QPushButton("Use Sweep")
        btn_extrude.clicked.connect(lambda: self.set_operation('extrude'))
        btn_revolve.clicked.connect(lambda: self.set_operation('revolve'))
        btn_sweep.clicked.connect(lambda: self.set_operation('sweep'))
        control_layout.addWidget(btn_extrude)
        control_layout.addWidget(btn_revolve)
        control_layout.addWidget(btn_sweep)

        btn_save = QPushButton("Save Sketch")
        btn_save.clicked.connect(self.save_sketch)
        control_layout.addWidget(btn_save)

        self.sketch_list = QListWidget()
        self.sketch_list.itemClicked.connect(self.load_selected_sketch)
        control_layout.addWidget(self.sketch_list)

        self.display.InitDriver()
        self.draw_shape()

    def create_input(self, layout, label, default):
        row = QHBoxLayout()
        row.addWidget(QLabel(label))
        spin = QSpinBox()
        spin.setRange(1, 500)
        spin.setValue(default)
        row.addWidget(spin)
        layout.addLayout(row)
        return spin

    def set_mode(self, mode):
        self.mode = mode
        self.draw_shape()

    def set_operation(self, op):
        self.operation = op
        self.draw_shape()

    def draw_shape(self):
        print("▶ Drawing shape...")

        self.display._display.EraseAll()
        depth = self.inputs['depth'].value()

        if self.operation == 'sweep':
            solid = make_sweep()
            print("✅ Sweep shape.")
        else:
            if self.mode == 'rectangle':
                w = self.inputs['width'].value()
                h = self.inputs['height'].value()
                print(f"→ Rectangle: {w} x {h}")
                wire = make_rectangle_sketch(w, h)
            else:
                r = self.inputs['radius'].value()
                print(f"→ Circle Radius: {r}")
                wire = make_circle_sketch(r)

            if wire is None:
                print("❌ No wire generated!")
                return

            try:
                if self.operation == 'extrude':
                    solid = extrude_sketch(wire, depth)
                    print("✅ Extruded shape.")
                else:
                    solid = revolve_sketch(wire)
                    print("✅ Revolved shape.")
            except Exception as e:
                print("❌ Failed to build shape:", str(e))
                return

        self.current_shape = AIS_Shape(solid)
        self.current_shape.SetColor(Quantity_Color(Quantity_NOC_BLUE1))
        self.display._display.Context.RemoveAll(False)
        self.display._display.Context.Display(self.current_shape, True)
        self.display._display.FitAll()
        self.display._display.Repaint()
        print("✅ Shape displayed.\n")

    def save_sketch(self):
        name = f"Sketch {len(self.sketches) + 1}"
        params = {
            'depth': self.inputs['depth'].value(),
            'operation': self.operation,
            'type': self.mode
        }

        if self.mode == 'rectangle':
            params['width'] = self.inputs['width'].value()
            params['height'] = self.inputs['height'].value()
        else:
            params['radius'] = self.inputs['radius'].value()

        sketch_data = {'name': name, 'params': params}
        self.sketches.append(sketch_data)
        self.sketch_list.addItem(name)

    def load_selected_sketch(self, item):
        name = item.text()
        sketch = next((s for s in self.sketches if s['name'] == name), None)
        if not sketch:
            QMessageBox.warning(self, "Error", "Sketch not found.")
            return

        self.mode = sketch['params']['type']
        self.operation = sketch['params'].get('operation', 'extrude')
        self.inputs['depth'].setValue(sketch['params']['depth'])

        if self.mode == 'rectangle':
            self.inputs['width'].setValue(sketch['params']['width'])
            self.inputs['height'].setValue(sketch['params']['height'])
        else:
            self.inputs['radius'].setValue(sketch['params']['radius'])

        self.draw_shape()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = CADApp()
    viewer.show()
    sys.exit(app.exec())
