from qtpy.QtWidgets import (
    QWidget,
    QDialog,
    QHBoxLayout,
    QFileDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QDialogButtonBox,
    QGridLayout,
)


class _BrowseCSVWidget(QWidget):
    def __init__(
        self,
        parent: QWidget | None = None,
        label: str = "",
        path: str | None = None,
        tooltip: str = "",
        *,
        is_dir: bool = True,
    ) -> None:
        super().__init__(parent)

        self._is_dir = is_dir

        self._current_path = path or ""

        self._label_text = label

        self._label = QLabel(f"{self._label_text}:")
        self._label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._label.setToolTip(tooltip)

        self._path = QLineEdit()
        self._path.setText(self._current_path)
        self._browse_btn = QPushButton("Browse")
        self._browse_btn.clicked.connect(self._on_browse)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        layout.addWidget(self._label)
        layout.addWidget(self._path)
        layout.addWidget(self._browse_btn)

    def value(self) -> str:
        return self._path.text()  # type: ignore

    def setValue(self, path: str) -> None:
        self._path.setText(path)

    def _on_browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, f"Select the {self._label_text}.", "", "CSV (*.csv)"
        )
        if path:
            self._path.setText(path)


class LoadCSVWidget(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.features_csv = _BrowseCSVWidget(
            self, label="Features .csv", tooltip="Select the features CSV file."
        )
        self.metadata_csv = _BrowseCSVWidget(
            self, label="Metadata .csv", tooltip="Select the metadata CSV file."
        )

        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QGridLayout(self)
        layout.addWidget(self.features_csv, 0, 0)
        layout.addWidget(self.metadata_csv, 1, 0)
        layout.addWidget(self.buttonBox, 2, 0)

    def value(self) -> tuple[str, str]:
        return self.features_csv.value(), self.metadata_csv.value()
