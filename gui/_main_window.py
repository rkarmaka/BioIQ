from qtpy.QtWidgets import QWidget, QMainWindow, QGridLayout, QMenuBar, QSplitter, QHBoxLayout
from qtpy.QtCore import Qt
from ._graph_widget import GraphWidget
from ._image_viewer import ImageViewer
from ._metadata_summary_widget import MetaSummaryWidget


class MenuBar(QMenuBar):
    def __init__(self, parent: QWidget | None = None):

        super().__init__(parent)
        self.files = self.addMenu('Files')
        self.opened = self.files.addAction('Open Folder')

        self.opened.triggered.connect(self.open_text)

    def open_text(self):
        print('Opening')


class QCMainWindow(QMainWindow):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setWindowTitle("QC Main Window")

        self.menubar = MenuBar(self)
        self.setMenuBar(self.menubar)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.graph = GraphWidget(self.central_widget)
        self.image_viewer = ImageViewer(self.central_widget)
        self.metadata_summary = MetaSummaryWidget(self.central_widget)

        # vertical splitter
        splitter1 = QSplitter(self.central_widget)
        splitter1.setOrientation(Qt.Orientation.Vertical)
        splitter1.addWidget(self.graph)
        splitter1.addWidget(self.metadata_summary)

        # horizontal splitter
        splitter2 = QSplitter(self.central_widget)
        splitter2.setOrientation(Qt.Orientation.Horizontal)
        splitter2.addWidget(splitter1)
        splitter2.addWidget(self.image_viewer)

        layout = QHBoxLayout(self.central_widget)
        layout.addWidget(splitter2)
