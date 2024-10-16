import pandas as pd
from qtpy.QtWidgets import (
    QWidget,
    QMainWindow,
    QMenuBar,
    QSplitter,
    QHBoxLayout,
    QFileDialog,
)
from qtpy.QtCore import Qt
from ._graph_widget import GraphWidget
from ._image_viewer import ImageViewer
from ._metadata_summary_widget import MetaSummaryWidget
from bioio import BioImage
import bioio_nd2
from biaqc.metadata import Metadata
from biaqc.utils import ND2ImageProcessor
from biaqc.analysis import FeaturePCA, MetadataAnalysis
from gui._load_csv_widget import LoadCSVWidget
from xarray import DataArray


class QCMainWindow(QMainWindow):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setWindowTitle("QC Main Window")

        self.feature_pca_df: pd.DataFrame | None = None
        self.metadata_analysis_list: list[str] | None = None

        self._files: dict[str, DataArray] = {}

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

        # connections
        self.graph.pointSelected.connect(self._on_point_selected)

    def _on_open(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")

        if folder_path:
            self._files.clear()

            nd2_processor = ND2ImageProcessor()
            csv_file = folder_path.split("/")[-1]
            nd2_processor.process_folder(
                folder_path=folder_path,
                output_csv=f"{folder_path}/{csv_file}_features.csv",
            )
            feature_pca = FeaturePCA()
            feature_pca.set_data(nd2_processor.df)
            self.feature_pca_df = feature_pca.combine_pcas()
            self.graph.set_dataframe(self.feature_pca_df)

            metadata = Metadata()
            metadata.process_folder(
                folder_path=folder_path,
                output_csv=f"{folder_path}/{csv_file}_metadata.csv",
            )
            metadata_analysis = MetadataAnalysis()
            metadata_analysis.set_data(metadata.df)
            self.metadata_analysis_list = metadata_analysis.generate_report()
            self.metadata_summary.setText(self.metadata_analysis_list)

    def _on_open_csv(self):
        load_csv = LoadCSVWidget()
        if load_csv.exec_():
            self._files.clear()
            csv_path, meta_path = load_csv.value()
            if not csv_path or not meta_path:
                raise ValueError("Both CSV and Metadata CSV paths are required.")

            feature_pca = FeaturePCA()
            feature_pca.set_data(pd.read_csv(csv_path))
            self.feature_pca_df = feature_pca.combine_pcas()
            self.graph.set_dataframe(self.feature_pca_df)

            metadata_analysis = MetadataAnalysis()
            metadata_analysis.set_data(pd.read_csv(meta_path))
            self.metadata_analysis_list = metadata_analysis.generate_report()
            self.metadata_summary.setText(self.metadata_analysis_list)

    def _on_point_selected(self, args: None | int | str) -> None:
        if args is None:
            self.image_viewer.clear()
            return
        path, c, z, t = args

        if path in self._files:
            image = self._files[path].isel(C=c, Z=z, T=t).to_numpy()
        else:
            print(f"Loading {path}...")
            _file = BioImage(path, reader=bioio_nd2.Reader)
            self._files[path] = _file.xarray_data
            image = _file.xarray_data.isel(C=c, Z=z, T=t).to_numpy()
        self.image_viewer.setData(image)
        self.image_viewer.ndv_file = (self._files[path], c, z, t)
        print(
            f"-----------\nfile_shape: {self._files[path].shape},\n"
            f"C: {c}, Z: {z}, T: {t},\nimage shape: {image.shape},\n"
            f"path: {path}\n-----------"
        )
