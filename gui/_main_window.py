import pandas as pd
from qtpy.QtWidgets import (
    QWidget,
    QMainWindow,
    QMenuBar,
    QSplitter,
    QHBoxLayout,
    QFileDialog
)
from qtpy.QtCore import Qt
from ._graph_widget import GraphWidget
from ._image_viewer import ImageViewer
from ._metadata_summary_widget import MetaSummaryWidget

from biaqc.metadata import Metadata
from biaqc.utils import ND2ImageProcessor
from biaqc.analysis import FeaturePCA, MetadataAnalysis
from gui._load_csv_widget import LoadCSVWidget
        

class QCMainWindow(QMainWindow):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setWindowTitle("QC Main Window")

        self.nd2_processor: ND2ImageProcessor | None = None
        self.metadata: Metadata | None = None
        self.feature_pca: FeaturePCA | None = None
        self.feature_pca_df: pd.DataFrame | None = None
        self.metadata_analysis: MetadataAnalysis | None = None
        self.metadata_analysis_list: list[str] | None = None

        self.menubar = QMenuBar(self)
        self.setMenuBar(self.menubar)

        self.files = self.menubar.addMenu("Files")
        self.opened = self.files.addAction("Open Folder and Run Analysis")
        self.opened.triggered.connect(self._on_open)
        self.open_csv = self.files.addAction("Open .csv")
        self.open_csv.triggered.connect(self._on_open_csv)

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

    def _on_open(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")

        if folder_path:
            self.nd2_processor = ND2ImageProcessor()
            csv_file = folder_path.split("/")[-1]
            self.nd2_processor.process_folder(
                folder_path=folder_path,
                output_csv=f"{folder_path}/{csv_file}_features.csv",
            )
            self.feature_pca = FeaturePCA()
            self.feature_pca.set_data(self.nd2_processor.df)
            self.feature_pca_df = self.feature_pca.combine_pcas()

            self.graph.set_dataframe(self.feature_pca_df)

            self.metadata = Metadata()
            self.metadata.process_folder(
                folder_path=folder_path,
                output_csv=f"{folder_path}/{csv_file}_metadata.csv",
            )
            self.metadata_analysis = MetadataAnalysis()
            self.metadata_analysis.set_data(self.metadata.df)
            self.metadata_analysis_list = self.metadata_analysis.generate_report()

            self.metadata_summary.setText(self.metadata_analysis_list)

    def _on_open_csv(self):
        load_csv = LoadCSVWidget()
        if load_csv.exec_():

            csv_path, meta_path = load_csv.value()
            if not csv_path or not meta_path:
                raise ValueError("Both CSV and Metadata CSV paths are required.")

            self.feature_pca = FeaturePCA()
            self.feature_pca.set_data(pd.read_csv(csv_path))
            self.feature_pca_df = self.feature_pca.combine_pcas()
            self.graph.set_dataframe(self.feature_pca_df)
            
            self.metadata_analysis = MetadataAnalysis()
            self.metadata_analysis.set_data(pd.read_csv(csv_path))
            self.metadata_analysis_list = self.metadata_analysis.generate_report()
            self.metadata_summary.setText(self.metadata_analysis_list)
