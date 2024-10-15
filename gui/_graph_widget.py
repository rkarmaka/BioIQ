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

# from _widgets.utils import DATA_PATH

PCA = "test"


class GraphWidget(QGroupBox):
    pointSelected = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.data_df: pd.DataFrame | None = None

        self.on_add: Callable | None = None

        self.pca: Axes | None = None

        self.pca_type_combo = QComboBox()
        self.pca_type_combo.addItems(["", PCA])
        self.pca_type_combo.currentTextChanged.connect(self._plot)

        self.channel_combo = QComboBox()
        self.channel_combo.addItems(["Channel 1", "Channel 2", "Channel 3"])
        self.channel_combo.currentTextChanged.connect(self._plot)

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

    def set_dataframe(self, image_name: str) -> None:
        ...
        # self.data_df = pd.read_csv(f"{DATA_PATH['csv_files']}/{image_name}.csv")

        # if text := self.combobox.currentText():
        #     self._plot(text)

    def _plot(self, plot_type: str) -> None:
        self.figure.clear()

        if plot_type == "": # or self.data_df is None:
            self.canvas.draw()
            return

        if plot_type == PCA:
            ax = self.figure.add_subplot(1, 1, 1)

            x = np.random.rand(100)
            y = np.random.rand(100)
            self.pca = ax.scatter(x, y, c="green")

            cursor = mplcursors.cursor(ax)

        else:
            return

        @cursor.connect("add")  # type: ignore [misc]
        def on_add(sel: mplcursors.Selection, signal: bool = True) -> None:
            # hide the annotation when the point is deselected
            with contextlib.suppress(AttributeError):
                sel.annotation.set_visible(False)
            if plot_type:
                graph = self.pca if plot_type == PCA else None
                if graph is None:
                    return
                # reset all face colors to green and set the selected point to magenta
                colors = ["green"] * len(self.pca.get_offsets())
                colors[sel.target.index] = "magenta"
                self.pca.set_facecolors(colors)
                self.canvas.draw_idle()
            # if signal:
            #     self.pointSelected.emit(info)

        self.on_add = on_add

        self.canvas.draw()
