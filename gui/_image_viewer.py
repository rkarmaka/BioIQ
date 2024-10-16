from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from fonticon_mdi6 import MDI6
from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from superqt import QLabeledRangeSlider
from superqt.fonticon import icon
from superqt.utils import signals_blocked
from vispy import scene
from ndv import NDViewer


if TYPE_CHECKING:
    from typing import Literal


SS = """
QSlider::groove:horizontal {
    height: 15px;
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(128, 128, 128, 0.25),
        stop:1 rgba(128, 128, 128, 0.1)
    );
    border-radius: 3px;
}

QSlider::handle:horizontal {
    width: 38px;
    background: #999999;
    border-radius: 3px;
}

QLabel { font-size: 12px; }

QRangeSlider { qproperty-barColor: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(100, 80, 120, 0.2),
        stop:1 rgba(100, 80, 120, 0.4)
    )}

SliderLabel {
    font-size: 12px;
    color: white;
}
"""


def show_error_dialog(parent: QWidget, message: str) -> None:
    """Show an error dialog with the given message."""
    dialog = QMessageBox(parent)
    dialog.setWindowTitle("Error")
    dialog.setText(message)
    dialog.setIcon(QMessageBox.Icon.Critical)
    dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
    dialog.exec()


class ImageViewer(QGroupBox):
    """A widget for displaying an image."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)

        self._viewer = _ImageCanvas(parent=self)

        self._image: None | str | Path = None

        # LUT controls -----------------------------------------------------------

        # LUT slider
        self._clims = QLabeledRangeSlider(Qt.Orientation.Horizontal)
        self._clims.setStyleSheet(SS)
        self._clims.setHandleLabelPosition(
            QLabeledRangeSlider.LabelPosition.LabelsOnHandle
        )
        self._clims.setEdgeLabelMode(QLabeledRangeSlider.EdgeLabelMode.NoLabel)
        self._clims.setRange(0, 2**8)
        self._clims.valueChanged.connect(self._on_clims_changed)
        # auto contrast checkbox
        self._auto_clim = QPushButton("Auto")
        self._auto_clim.setCheckable(True)
        self._auto_clim.setChecked(True)
        self._auto_clim.toggled.connect(self._clims_auto)
        # reset view button
        self._reset_view = QPushButton()
        self._reset_view.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._reset_view.setToolTip("Reset View")
        self._reset_view.setIcon(icon(MDI6.fullscreen))
        self._reset_view.clicked.connect(self._reset)
        # ndv button
        self._ndv = QPushButton()
        self._ndv.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._ndv.setToolTip("Open in ndv")
        self._ndv.setIcon(icon(MDI6.play_box_multiple_outline))
        self._ndv.clicked.connect(self._open_with_ndv)
        # bottom widget
        lut_wdg = QWidget()
        lut_wdg_layout = QHBoxLayout(lut_wdg)
        lut_wdg_layout.setContentsMargins(0, 0, 0, 0)
        lut_wdg_layout.addWidget(self._clims)
        lut_wdg_layout.addWidget(self._auto_clim)
        lut_wdg_layout.addWidget(self._reset_view)
        lut_wdg_layout.addWidget(self._ndv)

        # Layout ------------------------------------------------------------------
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self._viewer)
        main_layout.addWidget(lut_wdg)

    def setData(self, image: np.ndarray) -> None:
        """Set the image data."""
        self.clear()
        if image is None:
            return

        if len(image.shape) > 2:
            show_error_dialog(self, "Only 2D images are supported!")
            return

        self._clims.setRange(image.min(), image.max())

        self._viewer.update_image(image)

        with signals_blocked(self._auto_clim):
            self._auto_clim.setChecked(True)
            self._clims_auto(True)

    def data(self) -> np.ndarray | None:
        """Return the image data."""
        return self._viewer.image._data if self._viewer.image is not None else None
    
    def clear(self) -> None:
        """Clear the image."""
        if self._viewer.image is not None:
            self._viewer.image.parent = None
            self._viewer.image = None
        self._viewer.view.camera.set_range(margin=0)

    def _on_clims_changed(self, range: tuple[float, float]) -> None:
        """Update the LUT range."""
        self._viewer.clims = range
        self._auto_clim.setChecked(False)

    def _clims_auto(self, state: bool) -> None:
        """Set the LUT range to auto."""
        self._viewer.clims = "auto" if state else self._clims.value()
        if self._viewer.image is not None:
            data = self._viewer.image._data
            with signals_blocked(self._clims):
                self._clims.setValue((data.min(), data.max()))

    def _reset(self) -> None:
        """Reset the view."""
        self._viewer.view.camera.set_range(margin=0)

    def _open_with_ndv(self) -> None:
        # if self._image is None:
        #     return
        # data = ...
        import numpy as np
        data = np.random.rand(10, 3, 100, 100)
        ndv = NDViewer(data, parent=self)
        ndv.setWindowFlags(Qt.WindowType.Dialog)
        ndv.show()

class _ImageCanvas(QWidget):
    """A Widget that displays an image."""

    def __init__(self, parent: ImageViewer):
        super().__init__(parent=parent)
        self._viewer = parent
        self._imcls = scene.visuals.Image
        self._clims: tuple[float, float] | Literal["auto"] = "auto"
        self._cmap: str = "grays"

        self._canvas = scene.SceneCanvas(keys="interactive", parent=self)
        self.view = self._canvas.central_widget.add_view(camera="panzoom")
        self.view.camera.aspect = 1

        self._lbl = None

        self.image: scene.visuals.Image | None = None

        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self._canvas.native)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    @property
    def clims(self) -> tuple[float, float] | Literal["auto"]:
        """Get the contrast limits of the image."""
        return self._clims

    @clims.setter
    def clims(self, clims: tuple[float, float] | Literal["auto"] = "auto") -> None:
        """Set the contrast limits of the image.

        Parameters
        ----------
        clims : tuple[float, float], or "auto"
            The contrast limits to set.
        """
        if self.image is not None:
            self.image.clim = clims
        self._clims = clims

    @property
    def cmap(self) -> str:
        """Get the colormap (lookup table) of the image."""
        return self._cmap

    @cmap.setter
    def cmap(self, cmap: str = "grays") -> None:
        """Set the colormap (lookup table) of the image.

        Parameters
        ----------
        cmap : str
            The colormap to use.
        """
        if self.image is not None:
            self.image.cmap = cmap
        self._cmap = cmap

    def update_image(self, image: np.ndarray) -> None:
        clim = (image.min(), image.max())
        self.image = self._imcls(
            image, cmap=self._cmap, clim=clim, parent=self.view.scene
        )
        self.image.set_gl_state("additive", depth_test=False)
        self.image.interactive = True
        self.view.camera.set_range(margin=0)
