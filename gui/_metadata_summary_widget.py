from qtpy.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox

META = [
    "[x] All images are acquired using ecmC10600-10B.",
    "[v] All images are acquired with 0.75.",
    "[?] All images are acquired with 20x.",
    "[ ] All images are acquired with 12.",
    "[?] Time series data with 175 frames per image.",
    "[?] Not a z-stack.",
    "[ ] Multi-channel image with 3 channels per image.",
    "[ ] Images have width 1344.",
    "[ ] Images have height 1024.",
    "[ ] All images acquired have 0.3225 micrometers physical size x.",
    "[ ] All images acquired have 0.3225 micrometers physical size y.",
    "[ ] Time between frames: 7.9997 +/- 0.016 seconds.",
]


class MetaSummaryWidget(QGroupBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setTitle("Metadata Summary")

        self.label = QLabel()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(self.label)
        layout.addStretch()

    def setText(self, text: list[str]) -> None:
        text = "<br>".join(text)
        text = text.replace("[x]", "<font color='red'><b>\u2716</b></font>")
        text = text.replace("[v]", "<font color='green'><b>\u2713</b></font>")
        text = text.replace("[?]", "<font color='orange'><b>\u003f</b></font>")
        # Replace newline characters with <br> to preserve line breaks
        text = text.replace("\n", "<br>")
        self.label.setText(text)
