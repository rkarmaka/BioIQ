import os
import csv
from collections import Counter
import numpy as np
import tifffile
from datetime import datetime

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
