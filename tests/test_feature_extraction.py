from biaqc.utils import read_tiff_file
from biaqc.feature_extraction import extract_intensity_features, extract_glcm_features

# Example usage:
image_path = '../sample_images/NoRI/Fused_S10.tif'
image, num_channels = read_tiff_file(image_path)

for c in range(num_channels):
    print(f'Channel: {c+1}')
    intensity_features = extract_intensity_features(image[:,:,c])
    for key, value in intensity_features.items():
        print(f"{key}: {value}")

    glcm_features = extract_glcm_features(image[:,:,c])
    for key, value in glcm_features.items():
        print(f"{key}: {value}")

