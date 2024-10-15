import os
import csv
from collections import Counter
import numpy as np
import tifffile
from datetime import datetime
from bioio import BioImage
import bioio_nd2
import pandas as pd

from feature_extraction import IntensityFeatures, Noise, Sharpness, TextureFeatures


from typing import Any, Dict, List, Optional
import logging

# Configure logging for the module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_file_types(path):
    file_names = os.listdir(path)
    extensions = [f.split('.')[-1] for f in file_names]

    extension_count = Counter(extensions).items()
    for key, value in extension_count:
        print(key, value)

    return np.unique(extensions)

# def get_file_names(path, extension):
#     if extension in ['tif', 'tiff']:
#         files = [f for f in os.listdir(path) if f.lower().endswith(('.tif', '.tiff'))]
    
#     if extension in ['nd2']:
#         files = [f for f in os.listdir(path) if f.lower().endswith(('.nd2'))]
    
#     return files


def get_file_names(path):
    files = [f for f in os.listdir(path)]
    
    # if extension in ['nd2']:
    #     files = [f for f in os.listdir(path) if f.lower().endswith(('.nd2'))]
    
    return files

def read_tiff_file(image_path):
    if image_path.lower().endswith(('.tif', '.tiff')):
        image = tifffile.imread(image_path)
        if image.ndim < 3:
            ch = 1
            return image, ch
        else:
            print(image.shape)
            h, w, c = image.shape
            loc_ch = np.argmin((h, w, c))
            image = np.moveaxis(image, loc_ch, -1)
            _, _, ch = image.shape
            print(image.shape)
            return image, ch
    else:
        print('Not a valid tiff file.')
        return None


def write_image_info_to_csv(image_info, folder_path, csv_filename):
    """
    Writes the image_info dictionary to a CSV file.

    Parameters:
    - image_info (dict): Dictionary containing image information.
    - folder_path (str): Path to the folder where the CSV file will be created.
    """

    # Define the default CSV filename
    # csv_filename = 'image_info.csv'
    csv_path = os.path.join(folder_path, csv_filename)

    # Check if the file exists
    # if os.path.isfile(csv_path):
    #     # # If it exists, append date and time to the filename
    #     # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    #     # csv_filename = f'image_info_{timestamp}.csv'
    #     # csv_path = os.path.join(folder_path, csv_filename)

    with open(csv_path, mode='a', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=image_info.keys())
        
        # Write the header if the file is newly created
        if os.path.getsize(csv_path) == 0:
            writer.writeheader()

        # Write the image_info dictionary rows
        writer.writerow(image_info)

    # print(f"CSV file created at: {csv_path}")




class ND2ImageProcessor:
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

    def read_nd2(self):
        """Reads an ND2 file and returns a BioImage object."""
        image = BioImage(self.file_path, reader=bioio_nd2.Reader)
        return image
    

    def _extract_file_extension(self) -> str:
        """
        Extracts the file extension from the file path.

        Returns:
            str: The file extension.
        """
        extension = self.file_path.split('/')[-1].split('.')[-1]
        logger.debug(f"Extracted file extension: {extension}")
        return extension

    def extract_XY_slices(self, image):
        """Extracts XY slices from the ND2 image across all Z, C, and T."""
        dims_order = image.dims.order
        dim_map = {dim: i for i, dim in enumerate(dims_order)}
        Z_size = image.dims.Z
        C_size = image.dims.C
        T_size = image.dims.T

        slices = []
        for t in range(T_size):
            for c in range(C_size):
                for z in range(Z_size):
                    indices = [slice(None)] * len(image.shape)
                    indices[dim_map['T']] = t
                    indices[dim_map['C']] = c
                    indices[dim_map['Z']] = z
                    XY_image = image.data[tuple(indices)]
                    slices.append((t, c, z, XY_image))  # Append the XY slice with its T, C, Z coordinates
        return slices
    
    def _initialize_features_dict(self):
        features_dict = {
            'file_path': self.file_path,
            'image_name': self.image_name,
            'extension': self.image_extension,

        }

        return features_dict
    
    def _extract_image_name(self) -> str:
        """
        Extracts the image name (without extension) from the file path.

        Returns:
            str: The image name.
        """
        name = self.file_path.split('/')[-1].split('.')[0]
        logger.debug(f"Extracted image name: {name}")
        return name

    def extract_features_from_slice(self, XY_image):
        """Extract features from the given XY slice. You can modify this method based on your feature extraction logic."""
        intensity = IntensityFeatures()
        intensity.set_image(image=XY_image)
        intensity_features = intensity.extract_all_features()
        # all_features.update(intensity_features)

        noise = Noise()
        noise.set_image(image=XY_image)
        noise_features = noise.extract_all_features()
        # all_features.update(noise_features)

        sharp = Sharpness()
        sharp.set_image(image=XY_image)
        sharp_features = sharp.extract_all_features()
        # all_features.update(sharp_features)

        tex = TextureFeatures()
        tex.set_image(image=XY_image)
        tex_features = tex.extract_all_features()
        # all_features.update(tex_features)

        all_features = {**sharp_features, **noise_features, **intensity_features, **tex_features}

        return all_features

    def process_image(self):
        """Processes the ND2 image and returns a list of feature dictionaries for each XY slice."""
        results = []
        image = self.read_nd2()
        slices = self.extract_XY_slices(image)

        # Extract features for each XY slice and add to results list
        for t, c, z, XY_image in slices:
            features = self._initialize_features_dict()
            row = {
                'T': t,
                'C': c,
                'Z': z,
            }
            features.update(row)
            features.update(self.extract_features_from_slice(XY_image))
            
            results.append(features)
        
        return results
    
    def process_folder(self, folder_path: str, output_csv: str):
        """Processes all ND2 files in the specified folder and saves the extracted features to a CSV file.
        
        Args:
            folder_path (str): Path to the folder containing ND2 files.
            output_csv (str): Path to the CSV file where results will be saved.
        """
        # Collect all results from all files
        all_results = []

        # Iterate through all files in the folder
        for file_name in os.listdir(folder_path):
            if file_name.endswith('.nd2'):  # Process only ND2 files
                self.set_image_path(os.path.join(folder_path, file_name))
                image_results = self.process_image()
                all_results.extend(image_results)

        # Save results to CSV
        # Convert metadata list to a pandas DataFrame and save to CSV
        df = pd.DataFrame(all_results)
        df.to_csv(output_csv, index=False)