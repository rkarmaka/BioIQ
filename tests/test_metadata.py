# from biaqc.metadata import read_tiff_metadata

# # Example usage:
# tiff_file_path = '../sample_images/NoRI/Fused_S10.tif'
# metadata = read_tiff_metadata(tiff_file_path)
# for key, value in metadata.items():
#     if key in ['ImageWidth', 'ImageLength', 'BitsPerSample', 'channels']:
#         print(f"{key}: {value}")
#     elif key in ['IJMetadata']:
#         k = 'Ranges'
#         print(f"{k}: {value[k]}")


import os
from biaqc.utils import get_file_types, get_file_names, write_image_info_to_csv
from biaqc.metadata import read_nd2_metadata, read_tiff_metadata
import pandas as pd

image_path = '../sample_images/nori'
# extensions = get_file_types(image_path)

file_names = get_file_names(image_path)

# all_metadata = []
header_written = True

for file_name in file_names:
    ext = file_name.split('.')[-1]
    if ext in ['tif', 'tiff']:
        metadata = read_tiff_metadata(f'{image_path}/{file_name}')
        # df_metadata = pd.DataFrame(metadata)  # Use a list of metadata dictionaries
        # # Append the metadata to the CSV file
        # df_metadata.to_csv('metadata_tiff.csv', mode='a', header=header_written, index=False)
        # # After the first write, set header_written to True
        # if header_written:
        #     header_written = False
    
    if ext=='nd2':
        metadata = read_nd2_metadata(f'{image_path}/{file_name}')

        df_metadata = pd.DataFrame(metadata)  # Use a list of metadata dictionaries
        
        # Append the metadata to the CSV file
        df_metadata.to_csv(f'{image_path}/metadata_nd2.csv', mode='a', header=header_written, index=False)
        
        # After the first write, set header_written to True
        if header_written:
            header_written = False
