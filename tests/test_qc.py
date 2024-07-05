import os
from biaqc.utils import get_file_types, get_tiff_file_names, read_tiff_file, write_image_info_to_csv
from biaqc.metadata import read_tiff_metadata
from biaqc.feature_extraction import extract_intensity_features, extract_glcm_features

image_dir = '../sample_images/NoRI'

# Check how many different file types there are in the folder and their count
extensions = get_file_types(image_dir)
# print(extensions)

# Read all file names with .tif or .tiff extensions
tiff_files = get_tiff_file_names(image_dir)

# Read tiff files
for file_name in tiff_files:
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


        image_info = {
            'image_path' : full_image_path,
            'image_name' : file_name.split('.')[0],
            'image_extension' : file_name.split('.')[-1],
            'image_width' : metadata['ImageWidth'],
            'image_height' : metadata['ImageLength'],
            'num_channels' : num_channels,
            'bits_per_sample' : metadata['BitsPerSample'],
            'channel' : ch+1,
            'mean_intensity' : intensity_features['mean_intensity'],
            'median_intensity' : intensity_features['median_intensity'],
            'std_intensity' : intensity_features['std_intensity'],
            'variance' : intensity_features['variance'],
            'min_intensity' : intensity_features['min_intensity'],
            'max_intensity' : intensity_features['max_intensity'],
            'range' : intensity_features['range'],
            'bit_depth' : intensity_features['bit_depth'],
            'entropy' : intensity_features['entropy'],
            'skewness' : intensity_features['skewness'],
            'kurtosis' : intensity_features['kurtosis'],
            'contrast' : glcm_features['contrast'],
            'dissimilarity' : glcm_features['dissimilarity'],
            'homogeneity' : glcm_features['homogeneity'],
            'energy' : glcm_features['energy'],
            'correlation' : glcm_features['correlation'],
            'ASM' : glcm_features['ASM'],
        }

        # print(image_info)
        write_image_info_to_csv(image_info, image_dir)

