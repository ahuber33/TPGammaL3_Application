import sys
from pathlib import Path
import subprocess
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QLineEdit, QLabel, QFileDialog, QSpinBox, QCheckBox,
    QFormLayout, QTextEdit
)
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QTextCursor


class SimulationThread(QThread):
    output_signal = Signal(str)
    finished_signal = Signal()

    def __init__(self, cmd, cwd):
        super().__init__()
        self.cmd = cmd
        self.cwd = cwd
        self.process = None  # <-- on garde une référence au subprocess

    def run(self):
        try:
            self.process = subprocess.Popen(
                self.cmd,
                cwd=self.cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                universal_newlines=True
            )

            buffer_line = ""
            for char in iter(lambda: self.process.stdout.read(1), ''):
                buffer_line += char
                if char == '\r':
                    self.output_signal.emit(buffer_line.strip())
                    buffer_line = ""
                elif char == '\n':
                    self.output_signal.emit(buffer_line.strip())
                    buffer_line = ""

            if buffer_line:
                self.output_signal.emit(buffer_line.strip())

            self.process.wait()
        except Exception as e:
            self.output_signal.emit(f"Error: {e}")
        finally:
            self.finished_signal.emit()


class SimApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TPGammaL3 Simulation Launcher")
        layout = QVBoxLayout()

        # Macro selector
        self.macro_label = QLabel("Macro file:")
        self.macro_path = QLineEdit()
        self.browse_macro_btn = QPushButton("Choisir Macro")
        self.browse_macro_btn.clicked.connect(self.select_macro)
        layout.addWidget(self.macro_label)
        layout.addWidget(self.macro_path)
        layout.addWidget(self.browse_macro_btn)

        # Output name
        self.output_label = QLabel("Nom fichier de sortie (sans .root):")
        self.output_name = QLineEdit("test")
        layout.addWidget(self.output_label)
        layout.addWidget(self.output_name)

        # Events
        self.events_label = QLabel("Nombre d'évènements:")
        self.events_spin = QSpinBox()
        self.events_spin.setMinimum(1)
        self.events_spin.setMaximum(1000000)
        self.events_spin.setValue(10)
        layout.addWidget(self.events_label)
        layout.addWidget(self.events_spin)

        # ML and Visualization
        self.vis_checkbox = QCheckBox("Activer Visualisation")
        self.vis_checkbox.stateChanged.connect(self.toggle_visualization_mode)
        layout.addWidget(self.vis_checkbox)

        # Parameters
        self.param_layout = QFormLayout()
        self.params = {
            "RadiusNaI": QLineEdit("25.4 mm"),
            "ThicknessNaI": QLineEdit("50.8 mm"),
            "ThicknessHousing": QLineEdit("0.508 mm"),
            "ThicknessAbsorber": QLineEdit("10 mm"),
            "ThicknessDesk": QLineEdit("50 mm"),
            "ThicknessSourceHolder": QLineEdit("0.2 mm"),
            "DeskSourceDistance": QLineEdit("100 mm"),
            "SourceNaIDistance": QLineEdit("100 mm"),
            "AbsorberMaterial": QLineEdit("G4_Pb")
        }
        for name, widget in self.params.items():
            self.param_layout.addRow(name, widget)
        layout.addLayout(self.param_layout)

        # Run/Stop buttons
        self.run_btn = QPushButton("Run Simulation")
        self.run_btn.clicked.connect(self.run_simulation)
        layout.addWidget(self.run_btn)
        self.stop_btn = QPushButton("Stop Visualization")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_visualization)
        layout.addWidget(self.stop_btn)

        # Console
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        layout.addWidget(self.console)

        self.setLayout(layout)

        # Paths
        self.base_path = Path(__file__).parent.parent
        self.bundle_path = self.base_path / "bundle"
        self.macros_path = self.base_path / "app/macros"
        self.binary = self.bundle_path / "bin/TPGammaL3Sim"

        self.vis_process = None
        self.sim_thread = None

    def select_macro(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Select Macro File", str(self.macros_path), "Macro Files (*.mac)"
        )
        if file:
            self.macro_path.setText(file)

    def generate_macro(self, template_path: Path, params: dict, out_path: Path):
        with open(template_path, "r") as f:
            content = f.readlines()
        for i, line in enumerate(content):
            for key, widget in params.items():
                if f"/geometry/set{key}" in line:
                    content[i] = f"/geometry/set{key} {widget.text()}\n"
        with open(out_path, "w") as f:
            f.writelines(content)

    def toggle_visualization_mode(self, state):
        vis_enabled = self.vis_checkbox.isChecked()
        self.macro_path.setEnabled(not vis_enabled)
        self.browse_macro_btn.setEnabled(not vis_enabled)
        self.output_name.setEnabled(not vis_enabled)
        self.events_spin.setEnabled(not vis_enabled)
        self.stop_btn.setEnabled(vis_enabled)

    def parse_value(self, value: str) -> float:
        try:
            return float(value.split()[0])
        except:
            return None

    def append_console_line(self, line: str):
        """Ajoute une ligne dans le QTextEdit en simulant un flush pour '\r'."""
        cursor = self.console.textCursor()
        cursor.movePosition(QTextCursor.End)

        if line.startswith('[') and '%' in line:  # détection simple de la barre de progression
            # Supprime la dernière ligne
            cursor.select(QTextCursor.BlockUnderCursor)
            cursor.removeSelectedText()
            cursor.deletePreviousChar()  # supprime le '\n'
            self.console.setTextCursor(cursor)
            self.console.insertPlainText(line)
        else:
            self.console.insertPlainText(line + '\n')

        self.console.ensureCursorVisible()

    def apply_params_to_vis_macro(self):
        """Applique les paramètres actuels directement dans vis.mac"""
        vis_macro_path = self.bundle_path / "bin/vis.mac"

        with open(vis_macro_path, "r") as f:
            content = f.readlines()

        for i, line in enumerate(content):
            for key, widget in self.params.items():
                if f"/geometry/set{key}" in line:
                    content[i] = f"/geometry/set{key} {widget.text()}\n"

        with open(vis_macro_path, "w") as f:
            f.writelines(content)


    def parse_value(self, value: str) -> float:
        """Extrait la valeur numérique d'un string contenant une unité, ex: '10 mm' -> 10.0"""
        try:
            return float(value.split()[0])
        except:
            return None


    def run_simulation(self):
        # Vérification des paramètres globaux
        thickness_absorber = self.parse_value(self.params["ThicknessAbsorber"].text())
        source_naidistance = self.parse_value(self.params["SourceNaIDistance"].text())

        if thickness_absorber is None or source_naidistance is None:
            self.console.append("Error: Invalid numeric value in parameters.")
            return

        if thickness_absorber >= source_naidistance:
            self.console.append(
                "Error: ThicknessAbsorber must be strictly less than SourceNaIDistance."
            )
            return

        vis_enabled = self.vis_checkbox.isChecked()

        if vis_enabled:
            # Appliquer les paramètres dans vis.mac
            self.apply_params_to_vis_macro()

            # Lancer Geant4 en mode visu
            cmd = [str(self.binary), "visu"]
            cwd = self.bundle_path / "bin"
            self.vis_process = subprocess.Popen(cmd, cwd=cwd)
            self.stop_btn.setEnabled(True)

        else:
            # Mode batch classique
            macro = self.macro_path.text()
            output_name = self.output_name.text()
            n_events = self.events_spin.value()
            if not macro or not output_name:
                self.console.append("Erreur: Macro ou nom de fichier de sortie non défini!")
                return

            # Modifier la macro directement avec les paramètres modifiables
            with open(macro, "r") as f:
                lines = f.readlines()

            for i, line in enumerate(lines):
                for key, widget in self.params.items():
                    if f"/geometry/set{key}" in line:
                        lines[i] = f"/geometry/set{key} {widget.text()}\n"

            with open(macro, "w") as f:
                f.writelines(lines)                
            result_dir = self.base_path / "Resultats"
            result_dir.mkdir(exist_ok=True)
            output_path = result_dir / output_name
            cmd = [str(self.binary), str(output_path), str(n_events), str(macro), "OFF"]
            cwd = self.bundle_path

            self.sim_thread = SimulationThread(cmd, cwd=cwd)
            self.sim_thread.output_signal.connect(self.append_console_line)
            self.sim_thread.finished_signal.connect(lambda: self.console.append("Simulation terminée!"))
            self.sim_thread.start()



    def stop_visualization(self):
        if self.vis_process:
            # Termine le processus Geant4 et ferme la fenêtre
            self.vis_process.terminate()  
            self.vis_process.wait()
            self.vis_process = None
            self.console.append("Visualisation stoppée.")
            self.stop_btn.setEnabled(False)
