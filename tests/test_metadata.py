from biaqc.metadata import read_tiff_metadata

# Example usage:
tiff_file_path = '../sample_images/NoRI/Fused_S10.tif'
metadata = read_tiff_metadata(tiff_file_path)
for key, value in metadata.items():
    if key in ['ImageWidth', 'ImageLength', 'BitsPerSample', 'channels']:
        print(f"{key}: {value}")
    elif key in ['IJMetadata']:
        k = 'Ranges'
        print(f"{k}: {value[k]}")