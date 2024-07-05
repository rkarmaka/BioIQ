import numpy as np
from skimage import io
from skimage.util import img_as_float, img_as_ubyte
from scipy.stats import entropy, skew, kurtosis
from skimage.feature import graycomatrix, graycoprops

def extract_intensity_features(image, bit_depth=None):
    """
    Extracts intensity-based features from an image.

    Parameters:
    - image (ndarray): Image file.

    Returns:
    - dict: A dictionary containing the extracted features.
    """
    if bit_depth is not None:
        num_bins = 2**bit_depth
    else:
        bit_depth = _get_bit_depth(image)
        num_bins = 2**bit_depth

    
    features = {}
    features['mean_intensity'] = np.mean(image)
    features['median_intensity'] = np.median(image)
    features['std_intensity'] = np.std(image)
    features['variance'] = np.var(image)
    features['min_intensity'] = np.min(image)
    features['max_intensity'] = np.max(image)
    features['range'] = np.max(image) - np.min(image)
    features['bit_depth'] = bit_depth
    
    image = img_as_float(image/num_bins)
    hist, bin_edges = np.histogram(image, bins=num_bins, range=(0, 1))
    features['histogram'] = hist
    features['entropy'] = entropy(hist)
    features['skewness'] = skew(image.flatten())
    features['kurtosis'] = kurtosis(image.flatten())
    
    return features




def extract_glcm_features(image, bit_depth=None, distances=None, angles=None):
    """
    Extracts texture-based features from an image using GLCM, adjusting for bit depth.

    Parameters:

    - bit_depth (int): The bit depth of the image (e.g., 8, 12, 16).

    Returns:
    - dict: A dictionary containing the extracted texture features.
    """

    # Define distances and angles for GLCM
    if distances is None:
        distances = [1, 2, 4, 8]
    
    if angles is None:
        angles = [0, np.pi/4, np.pi/2, 3*np.pi/4]
    
    # Compute GLCM
    print(image.max(), image.dtype)
    image=_img_to_uint8(image)
    print(image.max())
    glcm = graycomatrix(image, distances=distances, angles=angles, symmetric=True, normed=True)
    
    # Extract texture features
    features = {}
    features['contrast'] = graycoprops(glcm, 'contrast').mean()
    features['dissimilarity'] = graycoprops(glcm, 'dissimilarity').mean()
    features['homogeneity'] = graycoprops(glcm, 'homogeneity').mean()
    features['energy'] = graycoprops(glcm, 'energy').mean()
    features['correlation'] = graycoprops(glcm, 'correlation').mean()
    features['ASM'] = graycoprops(glcm, 'ASM').mean()
    
    return features



def _get_bit_depth(image):
    bit_depth = int(np.ceil(np.log2(np.max(image))))
    if bit_depth<=8:
        return 8
    elif bit_depth<=12:
        return 12
    elif bit_depth<=16:
        return 16
    else:
        print('The image is more than 16-bit.')
        return None
    
def _img_to_uint8(image):
    bit_depth = _get_bit_depth(image)
    num_levels = 2**bit_depth
    return (255*(image/num_levels)).astype('uint8')