import os
import multiprocessing as mp
from biaqc.utils import get_file_types, get_file_names, read_tiff_file, write_image_info_to_csv
from biaqc.metadata import read_tiff_metadata
from biaqc.feature_extraction import extract_intensity_features, extract_glcm_features, extract_lbp_features, extract_fourier_features
from datetime import datetime
from time import time

def process_image(file_name, image_dir, csv_filename):
    full_image_path = os.path.join(image_dir, file_name)

    # Read image metadata
    metadata = read_tiff_metadata(full_image_path)
    
    # Read image
    image, num_channels = read_tiff_file(full_image_path)

    for ch in range(num_channels):
        # Extract intensity features
        intensity_features = extract_intensity_features(image[:,:,ch])

        # Extract GLCM features
        glcm_features = extract_glcm_features(image[:,:,ch])

        # Extract LBP features
        lbp_features = extract_lbp_features(image[:,:,ch])

        image_info = {
            'image_path' : full_image_path,
            'image_name' : file_name.split('.')[0],
            'image_extension' : file_name.split('.')[-1],
            'image_width' : metadata['ImageWidth'],
            'image_height' : metadata['ImageLength'],
            'num_channels' : num_channels,
            'bits_per_sample' : metadata['BitsPerSample'],
            'channel' : ch+1
        }

        image_info.update(intensity_features)
        image_info.update(glcm_features)
        image_info.update(lbp_features)

        write_image_info_to_csv(image_info, image_dir, csv_filename)

def main():
    image_dir = '../sample_images/NoRI'
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f'image_info_{timestamp}.csv'

    # Check how many different file types there are in the folder and their count
    extensions = get_file_types(image_dir)

    # Read all file names with .tif or .tiff extensions
    tiff_files = get_file_names(image_dir)

    # Determine the number of available CPU cores
    num_cores = mp.cpu_count()

    # Use multiprocessing to process images in parallel
    st = time()
    with mp.Pool(num_cores) as pool:
        pool.starmap(process_image, [(file_name, image_dir, csv_filename) for file_name in tiff_files])
    en = time()

    print(en-st)
if __name__ == "__main__":
    main()