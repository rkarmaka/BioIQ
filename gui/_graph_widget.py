from __future__ import annotations
import contextlib
from typing import Callable

import numpy as np
from qtpy.QtWidgets import (
    QGroupBox,
    QComboBox,
    QLabel,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
)
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd
import mplcursors
from matplotlib.axes import Axes
from qtpy.QtCore import Signal
from superqt.utils import signals_blocked



# from _widgets.utils import DATA_PATH

ALL = "All Features"
INTENSITY = "Intensity Features"
NOISE = "Noise Features"
SHARPNESS = "Sharpness Features"
TEXTURE = "Texture Features"

ITEMS = [ALL, INTENSITY, NOISE, SHARPNESS, TEXTURE]


class GraphWidget(QGroupBox):
    pointSelected = Signal(object)  # path, c, z, t or None

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.feature_pca_df: pd.DataFrame | None = None

        self.all: Axes | None = None
        self.intensity: Axes | None = None
        self.noise: Axes | None = None
        self.sharpness: Axes | None = None
        self.texture: Axes | None = None

        self.pca_type_combo = QComboBox()
        self.pca_type_combo.addItems(["", *ITEMS])

        self.channel_combo = QComboBox()
        self.channel_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        label = QLabel("Plot:")
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(10, 10, 10, 10)
        top_layout.setSpacing(5)
        top_layout.addWidget(label, stretch=0)
        top_layout.addWidget(self.pca_type_combo, stretch=1)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        combo_layout = QHBoxLayout()
        combo_layout.setContentsMargins(0, 0, 0, 0)
        combo_layout.setSpacing(5)
        combo_layout.addWidget(QLabel("Plot Type:"), stretch=0)
        combo_layout.addWidget(self.pca_type_combo, stretch=1)
        combo_layout.addWidget(self.channel_combo, stretch=0)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)
        main_layout.addLayout(combo_layout)
        main_layout.addWidget(self.canvas)

        # connections
        self.pca_type_combo.currentTextChanged.connect(self._plot)
        self.channel_combo.currentTextChanged.connect(self._plot)

    def set_dataframe(self, dataframe: pd.DataFrame) -> None:
        self.feature_pca_df = dataframe

        num_channels = dataframe.C.nunique()
        chs = [f"Channels {ch+1}" for ch in range(num_channels)]
        with signals_blocked(self.channel_combo):
            self.channel_combo.clear()
            self.channel_combo.addItems(chs)

        self._plot()

    def _plot(self) -> None:
        self.figure.clear()

        plot_type = self.pca_type_combo.currentText()

        if plot_type == "" or self.feature_pca_df is None:
            self.canvas.draw()
            self.pointSelected.emit(None)
            return
        
        ch = self.channel_combo.currentIndex()
        temp_data = self.feature_pca_df[self.feature_pca_df.C==ch]
        ax = self.figure.add_subplot(1, 1, 1)

        if plot_type == ALL:
            self.all = ax.scatter(temp_data['all_pca_1'], temp_data['all_pca_2'], c='green')
            ax.set_xlabel('PCA 1 for All Features')
            ax.set_ylabel('PCA 2 for All Features')
        
        elif plot_type == INTENSITY:
            self.intensity = ax.scatter(temp_data['intensity_pca_1'], temp_data['intensity_pca_2'], c='green')
            ax.set_xlabel('PCA 1 for Intensity Features')
            ax.set_ylabel('PCA 2 for Intensity Features')
        
        elif plot_type == NOISE:
            self.noise = ax.scatter(temp_data['noise_noise_level'], temp_data['noise_snr'], c='green')
            ax.set_xlabel('Noise Level')
            ax.set_ylabel('Signal to Noise Ratio')
        
        elif plot_type == SHARPNESS:
            self.sharpness = ax.scatter(temp_data['sharpness_pca_1'], temp_data['sharpness_pca_2'], c='green')
            ax.set_xlabel('PCA 1 for Sharpness Features')
            ax.set_ylabel('PCA 2 for Sharpness Features')
        
        elif plot_type == TEXTURE:
            self.texture = ax.scatter(temp_data['texture_pca_1'], temp_data['texture_pca_2'], c='green')
            ax.set_xlabel('PCA 1 for Texture Features')
            ax.set_ylabel('PCA 2 for Texture Features')

        else:
            self.canvas.draw()
            self.pointSelected.emit(None)
            return

        cursor = mplcursors.cursor(ax)

        @cursor.connect("add")  # type: ignore [misc]
        def on_add(sel: mplcursors.Selection) -> None:
            # hide the annotation when the point is deselected
            with contextlib.suppress(AttributeError):
                sel.annotation.set_visible(False)
            print(plot_type)
            if plot_type:
                graph = self._get_graph(plot_type)
                if graph is None:
                    return
                # reset all face colors to green and set the selected point to magenta
                colors = ["green"] * len(graph.get_offsets())
                colors[sel.index] = "magenta"
                graph.set_facecolors(colors)
                self.canvas.draw_idle()

            path = self.feature_pca_df['file_path'][sel.index]
            c = self.feature_pca_df['C'][sel.index]
            z = self.feature_pca_df['Z'][sel.index]
            t = self.feature_pca_df['T'][sel.index]
            self.pointSelected.emit((path, c, z, t))

        self.canvas.draw()
    
    def _get_graph(self, plot_type: str) -> Axes | None:
        if plot_type == INTENSITY:
            return self.intensity
        if plot_type == NOISE:
            return self.noise
        if plot_type == SHARPNESS:
            return self.sharpness
        if plot_type == TEXTURE:
            return self.texture
        if plot_type == ALL:
            return self.all
        return None
