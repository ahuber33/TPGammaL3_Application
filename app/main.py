from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget
import sys
from simulation import SimApp        # ton code Simulation
from root_explorer import RootExplorer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TPGammaL3 App")
        self.resize(1200, 900)

        # Création des onglets
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Onglet Simulation
        self.sim_tab = SimApp()
        self.tabs.addTab(self.sim_tab, "Simulations")

        # Onglet Analyse
        self.analysis_tab = RootExplorer()   # RootExplorer est maintenant un QWidget
        self.tabs.addTab(self.analysis_tab, "Analyses")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
