import os
import tifffile
import pandas as pd
from bioio import BioImage
import bioio_nd2
from ome_types import to_dict
from typing import Any, Dict, List, Optional
import logging

# Configure logging for the module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def read_tiff_metadata(file_path):
    """
    Reads metadata from a TIFF file.

    Parameters:
    - file_path (str): Path to the TIFF file.

    Returns:
    - dict: A dictionary containing the metadata.
    """
    with tifffile.TiffFile(file_path) as tif:
        metadata = tif.pages[0].tags
        metadata_dict = {tag.name: tag.value for tag in metadata.values()}

    return metadata_dict


class Metadata:
    """
    A class to handle metadata extraction from ND2 image files.
    TODO: Clean up extractions methods. Remove repeats.
    """

    def __init__(self) -> None:
        """
        Initializes the Metadata instance with default values.
        """
        self.file_path: Optional[str] = None
        self.image_extension: Optional[str] = None
        self.image_name: Optional[str] = None
        self.df: pd.DataFrame = None

    def set_image_path(self, file_path: str) -> None:
        """
        Sets the image file path and extracts its name and extension.

        Args:
            file_path (str): The path to the ND2 image file.
        """
        self.file_path = file_path
        self.image_extension = self._extract_file_extension()
        self.image_name = self._extract_image_name()

    def _extract_file_extension(self) -> str:
        """Extracts the file extension from the file path."""
        return self.file_path.split("/")[-1].split(".")[-1]

    def _extract_image_name(self) -> str:
        """Extracts the image name (without extension) from the file path."""
        return self.file_path.split("/")[-1].split(".")[0]

    def _initialize_basic_metadata(self) -> Dict[str, Any]:
        """Creates a dictionary with basic metadata."""
        return {
            "file_path": self.file_path,
            "image_name": self.image_name,
            "extension": self.image_extension,
        }

    class ReadND2:
        """
        A nested class to handle reading and extracting metadata from ND2 files.
        """

        def __init__(self, parent: "Metadata") -> None:
            """Initializes the ReadND2 class with a reference to the parent Metadata instance."""
            self.parent = parent
            self.plane_metadata_list: List[Dict[str, Any]] = []
            self.image: Optional[Any] = None
            self.metadata_dict: Dict[str, Any] = {}
            self.number_of_planes: int = 0

        def load_image(self) -> None:
            """Loads the ND2 image using BioImage and the specified reader."""
            self.image = BioImage(f"{self.parent.file_path}", reader=bioio_nd2.Reader)

        def convert_metadata_to_dict(self) -> None:
            """Converts the image metadata to a dictionary."""
            self.metadata_dict = to_dict(self.image.metadata)

        def extract_instrument_metadata(self) -> Dict[str, Any]:
            """Extracts instrument-related metadata from the metadata dictionary."""
            instruments = self.metadata_dict.get("instruments", [])
            if not instruments:
                raise KeyError("No instruments information found in metadata.")
            detector = instruments[0].get("detectors", [])[0]
            objective = instruments[0].get("objectives", [])[0]
            return {
                "instrument_model": detector.get("model", "Unknown Model"),
                "instrument_serial_number": detector.get(
                    "serial_number", "Unknown Serial Number"
                ),
                "objective_lens_na": objective.get("lens_na", "Unknown NA"),
                "objective_nominal_magnification": objective.get(
                    "nominal_magnification", "Unknown Magnification"
                ),
            }
        
        def extract_pixels_metadata(self) -> Dict[str, Any]:
            """Extracts pixel-related metadata from the metadata dictionary."""
            images = self.metadata_dict.get("images", [])
            pixels = images[0].get("pixels", {})
            return {
                "significant_bits": pixels.get("significant_bits", []),
                "size_x": pixels.get("size_x", []),
                "size_y": pixels.get("size_y", []),
                "size_z": pixels.get("size_z", []),
                "size_c": pixels.get("size_c", []),
                "size_t": pixels.get("size_t", []),
                "physical_size_x": pixels.get("physical_size_x", []),
                "physical_size_y": pixels.get("physical_size_y", []),
                "physical_size_z": pixels.get("physical_size_z", [])
            }



        def determine_number_of_planes(self) -> None:
            """Retrieves the number of planes in the image."""
            images = self.metadata_dict.get("images", [])
            pixels = images[0].get("pixels", {})
            self.number_of_planes = len(pixels.get("planes", []))

        def extract_planes_metadata(self) -> None:
            """Processes each plane to extract and compile metadata."""
            images = self.metadata_dict.get("images", [])
            pixels = images[0].get("pixels", {})
            planes = pixels.get("planes", [])

            for i in range(self.number_of_planes):
                metadata: Dict[str, Any] = self.parent._initialize_basic_metadata()
                instrument_metadata = self.extract_instrument_metadata()
                metadata.update(instrument_metadata)
                pixels_metadata = self.extract_pixels_metadata()
                metadata.update(pixels_metadata)
                plane_metadata = planes[i]
                metadata.update(plane_metadata)
                self.plane_metadata_list.append(metadata)

        def extract_all_metadata(self) -> List[Dict[str, Any]]:
            """Orchestrates the reading and processing of all ND2 metadata."""
            self.load_image()
            self.convert_metadata_to_dict()
            self.determine_number_of_planes()
            self.extract_planes_metadata()
            return self.plane_metadata_list

    def get_nd2_metadata(self) -> List[Dict[str, Any]]:
        """Retrieves ND2 metadata using the nested ReadND2 class."""
        reader = self.ReadND2(self)
        return reader.extract_all_metadata()

    def process_folder(self, folder_path: str, output_csv: str) -> None:
        """
        Processes all ND2 files in a folder and saves their metadata to a CSV file.

        Args:
            folder_path (str): The path to the folder containing ND2 files.
            output_csv (str): The path to the output CSV file.
        """
        all_metadata = []
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".nd2"):
                file_path = os.path.join(folder_path, file_name)
                self.set_image_path(file_path)
                metadata = self.get_nd2_metadata()
                all_metadata.extend(metadata)

        # Save results to CSV
        # Convert metadata list to a pandas DataFrame and save to CSV
        self.df = pd.DataFrame(all_metadata)
        self.df.to_csv(output_csv, index=False)


# def read_nd2_metadata(file_path):
#     img = BioImage(f'{file_path}', reader=bioio_nd2.Reader)
#     metadata = img.metadata
#     metadata_dict = to_dict(metadata)
#     image_name = file_path.split('/')[-1].split('.')[0]
#     m = []


#     for i in range(len(metadata_dict['images'][0]['pixels']['planes'])):
#         meta = {}
#         meta['file_path'] = file_path
#         meta['image_name'] = image_name
#         meta['extension'] = file_path.split('/')[-1].split('.')[-1]
#         meta.update({k:metadata_dict['images'][0]['pixels'][k] for k in metadata_dict['images'][0]['pixels'].keys() if k not in ['id', 'metadata_only', 'planes', 'channels']})
#         meta.update(metadata_dict['images'][0]['pixels']['planes'][i])
#         m.append(meta)
#         # print(metadata_dict['images'][0]['pixels']['planes'][i]['delta_t'])
#         # print(meta['delta_t'])

#     # print(metadata_dict['images'][0]['pixels']['planes'][0].keys())

#     # metadata = {k:metadata_dict['images'][0]['pixels'][k] for k in metadata_dict['images'][0]['pixels'].keys() if k not in ['id', 'metadata_only', 'planes', 'channels']}
#     # print(m)
#     pd.DataFrame(m).to_csv(f'metadata_{image_name}.csv')
#     return m


# def read_tiff_metadata(file_path):
#     img = BioImage(f'{file_path}', reader=bioio_nd2.Reader)
#     metadata = img.metadata
#     metadata_dict = to_dict(metadata)
#     image_name = file_path.split('/')[-1].split('.')[0]
#     m = []
#     meta = {}

#     for i in range(len(metadata_dict['images'][0]['pixels']['planes'])):
#         meta = {}
#         meta['file_path'] = file_path
#         meta['image_name'] = image_name
#         meta['extension'] = file_path.split('/')[-1].split('.')[-1]
#         meta.update({k:metadata_dict['images'][0]['pixels'][k] for k in metadata_dict['images'][0]['pixels'].keys() if k not in ['id', 'metadata_only', 'planes', 'channels']})
#         meta.update(metadata_dict['images'][0]['pixels']['planes'][i])
#         m.append(meta)
#         # print(metadata_dict['images'][0]['pixels']['planes'][i]['delta_t'])
#         # print(meta['delta_t'])

#     # print(metadata_dict['images'][0]['pixels']['planes'][0].keys())

#     # metadata = {k:metadata_dict['images'][0]['pixels'][k] for k in metadata_dict['images'][0]['pixels'].keys() if k not in ['id', 'metadata_only', 'planes', 'channels']}
#     # print(m)
#     pd.DataFrame(m).to_csv(f'metadata_{image_name}.csv')
#     return m
