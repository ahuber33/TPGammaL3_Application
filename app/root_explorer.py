import numpy as np
import matplotlib.pyplot as plt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QListWidget, QMessageBox,
    QMenu, QInputDialog, QLabel, QSplitter
)
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from histogram import load_branch_data, apply_resolution
from fit_tools import fit_gaussian_zone

class RootExplorer(QWidget):
    """Explorateur ROOT intégré dans un onglet"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Explorateur ROOT")
        self.setMinimumSize(900, 800)
        self.layout = QVBoxLayout(self)

        # -----------------------
        # Boutons et labels
        # -----------------------
        self.open_btn = QPushButton("Ouvrir un fichier ROOT")
        self.open_btn.clicked.connect(self.open_file)
        self.layout.addWidget(self.open_btn)

        self.nbins = 500
        self.bins_btn = QPushButton("Définir le nombre de bins")
        self.bins_btn.clicked.connect(self.set_bins)
        self.layout.addWidget(self.bins_btn)

        self.E_ref = None
        self.R_ref = None
        self.resolution_btn = QPushButton("Définir résolution pour énergie donnée")
        self.resolution_btn.clicked.connect(self.set_resolution)
        self.layout.addWidget(self.resolution_btn)

        self.plot_btn = QPushButton("Tracer histogramme")
        self.plot_btn.clicked.connect(self.plot_histogram)
        self.layout.addWidget(self.plot_btn)

        self.param_label = QLabel(self)
        self.layout.addWidget(self.param_label)
        self.update_param_label()

        # -----------------------
        # QSplitter pour liste et canvas
        # -----------------------
        self.branch_list = QListWidget()
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.fig)

        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.addWidget(self.branch_list)
        self.splitter.addWidget(self.canvas)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 3)
        self.layout.addWidget(self.splitter)

        self.toolbar = NavigationToolbar(self.canvas, self)
        self.layout.addWidget(self.toolbar)

        # -----------------------
        # Boutons supplémentaires
        # -----------------------
        self.fit_btn = QPushButton("Fit Gaussien")
        self.fit_btn.clicked.connect(self.fit_gaussian)
        self.layout.addWidget(self.fit_btn)

        self.reset_range_btn = QPushButton("Réinitialiser bornes et fit")
        self.reset_range_btn.clicked.connect(self.reset_range)
        self.layout.addWidget(self.reset_range_btn)

        self.fit_info_label = QLabel(self)
        self.layout.addWidget(self.fit_info_label)

        # Menu contextuel
        self.canvas.setContextMenuPolicy(Qt.CustomContextMenu)
        self.canvas.customContextMenuRequested.connect(self.show_context_menu)

        # Variables
        self.file = None
        self.tree = None
        self.last_hist_data = None
        self.range_min = None
        self.range_max = None
        self.span_patch = None
        self.fit_line = None

        self.canvas.mpl_connect('button_press_event', self.on_click)

    # -----------------------
    # Fonctions diverses
    # -----------------------
    def update_param_label(self):
        text = f"Bins = {self.nbins}"
        if self.E_ref is not None and self.R_ref is not None:
            text += f" | E_ref = {self.E_ref} keV | R_ref = {self.R_ref} %"
        else:
            text += " | Pas de résolution définie"
        self.param_label.setText(text)

    def open_file(self):
        from PySide6.QtWidgets import QFileDialog
        from pathlib import Path

        # Définir le dossier "Résultats" comme répertoire initial
        base_path = Path(__file__).parent.parent  # chemin vers TPGammaL3_App
        results_dir = base_path / "Resultats"
        results_dir.mkdir(exist_ok=True)  # création si n'existe pas

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Ouvrir un fichier ROOT",
            str(results_dir),  # <-- dossier de départ
            "ROOT files (*.root)"
        )
        if filename:
            try:
                import uproot
                self.file = uproot.open(filename)
                first_key = list(self.file.keys())[0]
                self.tree = self.file[first_key]

                self.branch_list.clear()
                for branch in self.tree.keys():
                    self.branch_list.addItem(branch)

            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de lire le fichier:\n{e}")


    def plot_histogram(self):
        selected = self.branch_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une branche dans la liste.")
            return

        branch_name = selected.text()
        try:
            data = load_branch_data(self.tree, branch_name)
            if self.E_ref and self.R_ref:
                data = apply_resolution(data, self.E_ref, self.R_ref)

            if self.range_min is not None and self.range_max is not None:
                data = data[(data >= self.range_min) & (data <= self.range_max)]

            self.ax.clear()
            counts, bins, _ = self.ax.hist(data, bins=self.nbins, histtype="step", color="blue")
            self.ax.set_title(f"Histogramme de {branch_name}")
            self.ax.set_xlabel(branch_name)
            self.ax.set_ylabel("Entries")
            self.canvas.draw()

            self.last_hist_data = (counts, bins)

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de tracer la branche {branch_name}:\n{e}")

    def set_bins(self):
        nbins, ok = QInputDialog.getInt(self, "Définir le nombre de bins", "Nombre de bins :", self.nbins, 1, 1000)
        if ok:
            self.nbins = nbins
            self.update_param_label()

    def set_resolution(self):
        E_ref, ok1 = QInputDialog.getDouble(self, "Énergie de référence", "E_ref (keV) :", 1000.0, 0.1, 1e6, 3)
        if not ok1:
            return
        R_ref, ok2 = QInputDialog.getDouble(self, "Résolution de référence", "R_ref (%) :", 8.1, 0.0, 100.0, 2)
        if not ok2:
            return
        self.E_ref = E_ref
        self.R_ref = R_ref
        self.update_param_label()

    # -----------------------
    # Gestion de la zone
    # -----------------------
    def on_click(self, event):
        if event.inaxes != self.ax:
            return
        if self.range_min is None:
            self.range_min = event.xdata
            QMessageBox.information(self, "Borne min", f"Borne inférieure définie à {self.range_min:.2f}")
        elif self.range_max is None:
            self.range_max = event.xdata
            if self.range_max < self.range_min:
                self.range_min, self.range_max = self.range_max, self.range_min
            self.span_patch = self.ax.axvspan(self.range_min, self.range_max, color='yellow', alpha=0.3)
            self.canvas.draw()
        else:
            self.range_min = event.xdata
            self.range_max = None
            if self.span_patch:
                self.span_patch.remove()
                self.span_patch = None
            if self.fit_line:
                self.fit_line.remove()
                self.fit_line = None
            self.fit_info_label.setText("")
            self.canvas.draw()
            QMessageBox.information(self, "Borne min", f"Borne inférieure réinitialisée à {self.range_min:.2f}")

    def reset_range(self):
        self.range_min = None
        self.range_max = None
        if self.span_patch:
            self.span_patch.remove()
            self.span_patch = None
        if self.fit_line:
            self.fit_line.remove()
            self.fit_line = None
        self.fit_info_label.setText("")
        self.canvas.draw()

    # -----------------------
    # Fit
    # -----------------------
    def fit_gaussian(self):
        if self.last_hist_data is None:
            QMessageBox.warning(self, "Attention", "Tracez d'abord un histogramme !")
            return
        if self.range_min is None or self.range_max is None:
            QMessageBox.warning(self, "Attention", "Veuillez définir une zone pour le fit.")
            return

        counts, bin_edges = self.last_hist_data
        bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
        bin_widths = np.diff(bin_edges)
        mask = (counts > 0) & (bin_centers >= self.range_min) & (bin_centers <= self.range_max)
        bin_centers_fit = bin_centers[mask]
        counts_fit = counts[mask]
        widths_fit = bin_widths[mask]

        if len(bin_centers_fit) < 3:
            QMessageBox.warning(self, "Attention", "Pas assez de données pour un fit.")
            return

        try:
            params, chi2_ndf, integral = fit_gaussian_zone(bin_centers_fit, counts_fit, widths_fit)
            if self.fit_line:
                self.fit_line.remove()
            x_fit = np.linspace(bin_centers_fit.min(), bin_centers_fit.max(), 1000)
            y_fit = params[0]*np.exp(-(x_fit - params[1])**2/(2*params[2]**2))
            self.fit_line, = self.ax.plot(x_fit, y_fit, color='red', linestyle='--', label='Fit Gaussien')
            self.ax.legend()
            self.canvas.draw()
            self.fit_info_label.setText(
                f"Fit : A={params[0]:.2f}, μ={params[1]:.2f}, σ={params[2]:.2f} | Chi²/ndf={chi2_ndf:.2f} | Intégrale={integral:.2f}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Fit impossible :\n{e}")

    # -----------------------
    # Menu contextuel
    # -----------------------
    def show_context_menu(self, pos):
        menu = QMenu(self)
        logy_action = menu.addAction("Basculer échelle Log Y")
        logx_action = menu.addAction("Basculer échelle Log X")
        save_action = menu.addAction("Sauvegarder en PNG")

        action = menu.exec_(self.canvas.mapToGlobal(pos))
        if action == logy_action:
            self.ax.set_yscale("log" if self.ax.get_yscale() == "linear" else "linear")
            self.canvas.draw()
        elif action == logx_action:
            self.ax.set_xscale("log" if self.ax.get_xscale() == "linear" else "linear")
            self.canvas.draw()
        elif action == save_action:
            self.fig.savefig("histogramme.png")
            QMessageBox.information(self, "Sauvegarde", "Histogramme sauvegardé en histogramme.png")
