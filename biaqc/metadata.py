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
    """

    def __init__(self) -> None:
        """
        Initializes the Metadata instance with default values.
        """
        self.file_path: Optional[str] = None
        self.image_extension: Optional[str] = None
        self.image_name: Optional[str] = None

    def set_image_path(self, file_path: str) -> None:
        """
        Sets the image file path and extracts its name and extension.

        Args:
            file_path (str): The path to the ND2 image file.
        """
        self.file_path = file_path
        self.image_extension = self._extract_file_extension()
        self.image_name = self._extract_image_name()
        logger.debug(f"Set image path: {self.file_path}, "
                     f"Name: {self.image_name}, Extension: {self.image_extension}")

    def _extract_file_extension(self) -> str:
        """
        Extracts the file extension from the file path.

        Returns:
            str: The file extension.
        """
        extension = self.file_path.split('/')[-1].split('.')[-1]
        logger.debug(f"Extracted file extension: {extension}")
        return extension

    def _extract_image_name(self) -> str:
        """
        Extracts the image name (without extension) from the file path.

        Returns:
            str: The image name.
        """
        name = self.file_path.split('/')[-1].split('.')[0]
        logger.debug(f"Extracted image name: {name}")
        return name

    def _initialize_basic_metadata(self) -> Dict[str, Any]:
        """
        Creates a dictionary with basic metadata.

        Returns:
            Dict[str, Any]: The basic metadata dictionary.
        """
        metadata = {
            'file_path': self.file_path,
            'image_name': self.image_name,
            'extension': self.image_extension
        }
        logger.debug(f"Initialized basic metadata: {metadata}")
        return metadata

    class ReadND2:
        """
        A nested class to handle reading and extracting metadata from ND2 files.
        """

        def __init__(self, parent: 'Metadata') -> None:
            """
            Initializes the ReadND2 class with a reference to the parent Metadata instance.

            Args:
                parent (Metadata): The parent Metadata instance.
            """
            self.parent = parent
            self.plane_metadata_list: List[Dict[str, Any]] = []
            self.image: Optional[Any] = None  # Replace Any with actual BioImage type
            self.metadata_dict: Dict[str, Any] = {}
            self.number_of_planes: int = 0

        def load_image(self) -> None:
            """
            Loads the ND2 image using BioImage and the specified reader.

            Raises:
                ValueError: If the file path is not set in the parent Metadata instance.
            """
            if not self.parent.file_path:
                logger.error("File path is not set in the parent Metadata instance.")
                raise ValueError("File path is not set in the parent Metadata instance.")

            logger.info(f"Loading ND2 image from: {self.parent.file_path}")
            self.image = BioImage(
                f'{self.parent.file_path}',
                reader=bioio_nd2.Reader
            )
            logger.debug("ND2 image loaded successfully.")

        def convert_metadata_to_dict(self) -> None:
            """
            Converts the image metadata to a dictionary.

            Raises:
                AttributeError: If the image has not been loaded.
            """
            if not self.image:
                logger.debug("Image not loaded; loading now.")
                self.load_image()
            self.metadata_dict = to_dict(self.image.metadata)
            logger.debug(f"Converted metadata to dictionary: {self.metadata_dict}")

        def extract_instrument_metadata(self) -> Dict[str, Any]:
            """
            Extracts instrument-related metadata from the metadata dictionary.

            Returns:
                Dict[str, Any]: A dictionary containing instrument metadata.

            Raises:
                KeyError: If required instrument information is missing.
            """
            instruments = self.metadata_dict.get('instruments', [])
            if not instruments:
                logger.error("No instruments information found in metadata.")
                raise KeyError("No instruments information found in metadata.")

            detectors = instruments[0].get('detectors', [])
            objectives = instruments[0].get('objectives', [])

            if not detectors or not objectives:
                logger.error("Detectors or objectives information is missing in instruments metadata.")
                raise KeyError("Detectors or objectives information is missing in instruments metadata.")

            detector = detectors[0]
            objective = objectives[0]

            model = detector.get('model', 'Unknown Model')
            serial_number = detector.get('serial_number', 'Unknown Serial Number')
            lens_na = objective.get('lens_na', 'Unknown NA')
            nominal_magnification = objective.get('nominal_magnification', 'Unknown Magnification')

            instrument_metadata = {
                'instrument_model': model,
                'instrument_serial_number': serial_number,
                'objective_lens_na': lens_na,
                'objective_nominal_magnification': nominal_magnification
            }
            logger.debug(f"Extracted instrument metadata: {instrument_metadata}")
            return instrument_metadata

        def determine_number_of_planes(self) -> None:
            """
            Retrieves the number of planes in the image.

            Raises:
                KeyError: If image or plane information is missing.
            """
            images = self.metadata_dict.get('images', [])
            if not images:
                logger.error("No images information found in metadata.")
                raise KeyError("No images information found in metadata.")

            pixels = images[0].get('pixels', {})
            planes = pixels.get('planes', [])

            self.number_of_planes = len(planes)
            logger.info(f"Number of planes: {self.number_of_planes}")

        def extract_planes_metadata(self) -> None:
            """
            Processes each plane to extract and compile metadata.

            Raises:
                KeyError: If image or pixel information is missing.
                TypeError: If plane metadata is not a dictionary.
            """
            images = self.metadata_dict.get('images', [])
            if not images:
                logger.error("No images information found in metadata.")
                raise KeyError("No images information found in metadata.")

            pixels = images[0].get('pixels', {})
            planes = pixels.get('planes', [])

            for i in range(self.number_of_planes):
                metadata: Dict[str, Any] = self.parent._initialize_basic_metadata()

                # Extract and update with instrument metadata
                instrument_metadata = self.extract_instrument_metadata()
                metadata.update(instrument_metadata)

                # Extract and update with pixel metadata excluding specific keys
                pixel_metadata = {
                    key: value
                    for key, value in pixels.items()
                    if key not in ['id', 'metadata_only', 'planes', 'channels']
                }
                metadata.update(pixel_metadata)

                # Extract and update with plane-specific metadata
                plane_metadata = planes[i]
                if not isinstance(plane_metadata, dict):
                    logger.error(f"Expected dict for plane metadata, got {type(plane_metadata)}")
                    raise TypeError(f"Expected dict for plane metadata, got {type(plane_metadata)}")
                metadata.update(plane_metadata)

                logger.debug(f"Metadata for plane {i}: {metadata}")
                self.plane_metadata_list.append(metadata)

        def extract_all_metadata(self) -> List[Dict[str, Any]]:
            """
            Orchestrates the reading and processing of all ND2 metadata.

            Returns:
                List[Dict[str, Any]]: A list of dictionaries containing metadata for each plane.
            """
            logger.info("Starting metadata extraction process.")
            self.load_image()
            self.convert_metadata_to_dict()
            self.determine_number_of_planes()
            self.extract_planes_metadata()
            logger.info("Completed metadata extraction process.")
            return self.plane_metadata_list
        
    def get_nd2_metadata(self) -> List[Dict[str, Any]]:
        """
        Retrieves ND2 metadata by utilizing the nested ReadND2 class.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing metadata for each plane.
        
        Raises:
            Exception: Propagates exceptions raised during metadata extraction.
        """
        reader = Metadata.ReadND2(self)
        return reader.extract_all_metadata()

    def get_nd2_metadata(self) -> List[Dict[str, Any]]:
        """
        Public method to get ND2 metadata using the nested ReadND2 class.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing metadata for each plane.
        """
        reader = self.ReadND2(self)
        return reader.extract_all_metadata()



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


