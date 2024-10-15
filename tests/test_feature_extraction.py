from biaqc.utils import read_tiff_file
from biaqc.feature_extraction import extract_intensity_features, extract_glcm_features, extract_lbp_features, extract_fourier_features, extract_edge_features

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

    lbp_features = extract_lbp_features(image[:,:,c])
    for key, value in lbp_features.items():
        print(f"{key}: {value}")

    fourier_features = extract_fourier_features(image[:,:,c])
    for key, value in fourier_features.items():
        print(f"{key}: {value}")

    # edge_features = extract_edge_features(image[:,:,c])
    # for key, value in edge_features.items():
    #     print(f"{key}: {value}")

