import numpy as np
from skimage import io
from skimage.util import img_as_float, img_as_ubyte
from scipy.stats import entropy, skew, kurtosis
from skimage.feature import graycomatrix, graycoprops, local_binary_pattern, canny
from skimage.restoration import estimate_sigma
import cv2 as cv



# def extract_intensity_features(image, bit_depth=None):
#     """
#     Extracts intensity-based features from an image.

#     Parameters:
#     - image (ndarray): Image file.

#     Returns:
#     - dict: A dictionary containing the extracted features.
#     """
#     if bit_depth is not None:
#         num_bins = 2**bit_depth
#     else:
#         bit_depth = _get_bit_depth(image)
#         num_bins = 2**bit_depth

    
#     features = {}
#     features['mean_intensity'] = np.mean(image)
#     features['median_intensity'] = np.median(image)
#     features['std_intensity'] = np.std(image)
#     features['variance'] = np.var(image)
#     features['min_intensity'] = np.min(image)
#     features['max_intensity'] = np.max(image)
#     features['range'] = np.max(image) - np.min(image)
#     features['bit_depth'] = bit_depth
    
#     image = img_as_float(image/num_bins)
#     hist, bin_edges = np.histogram(image, bins=num_bins, range=(0, 1))
#     features['histogram'] = hist
#     features['entropy'] = entropy(hist)
#     features['skewness'] = skew(image.flatten())
#     features['kurtosis'] = kurtosis(image.flatten())
    
#     return features




# def extract_glcm_features(image, distances=None, angles=None):
#     """
#     Extracts texture-based features from an image using GLCM, adjusting for bit depth.

#     Parameters:

#     - bit_depth (int): The bit depth of the image (e.g., 8, 12, 16).

#     Returns:
#     - dict: A dictionary containing the extracted texture features.
#     """

#     # Define distances and angles for GLCM
#     if distances is None:
#         distances = [1, 2, 4, 8]
    
#     if angles is None:
#         angles = [0, np.pi/4, np.pi/2, 3*np.pi/4]
    
#     # Compute GLCM
#     image=_img_to_uint8(image)
#     glcm = graycomatrix(image, distances=distances, angles=angles, symmetric=True, normed=True)
    
#     # Extract texture features
#     features = {}
#     features['contrast'] = graycoprops(glcm, 'contrast').mean()
#     features['dissimilarity'] = graycoprops(glcm, 'dissimilarity').mean()
#     features['homogeneity'] = graycoprops(glcm, 'homogeneity').mean()
#     features['energy'] = graycoprops(glcm, 'energy').mean()
#     features['correlation'] = graycoprops(glcm, 'correlation').mean()
#     features['ASM'] = graycoprops(glcm, 'ASM').mean()
    
#     return features


# def extract_lbp_features(image, radius=1, n_points=8):
#     """
#     Extracts texture-based features from an image using Local Binary Patterns (LBP).

#     Parameters:
#     - image (ndarray): The input image.
#     - radius (int): The radius of the circle.
#     - n_points (int): Number of points to consider for LBP.

#     Returns:
#     - dict: A dictionary containing the extracted LBP features.
#     """

#     lbp = local_binary_pattern(image, n_points, radius, method='uniform')
#     n_bins = int(lbp.max() + 1)
#     lbp_hist, _ = np.histogram(lbp, bins=n_bins, range=(0, n_bins), density=True)
    
#     features = {}
#     for i in range(n_bins):
#         features[f'lbp_bin_{i}'] = lbp_hist[i]
    
#     return features


# def extract_fourier_features(image):
#     """
#     Extracts frequency-based features from an image using the Fourier Transform.

#     Parameters:
#     - image (ndarray): The input image.

#     Returns:
#     - dict: A dictionary containing the extracted Fourier transform features.
#     """

#     f_transform = np.fft.fft2(image)
#     f_transform_shifted = np.fft.fftshift(f_transform)
#     magnitude_spectrum = np.abs(f_transform_shifted)

#     features = {}
#     features['dominant_frequency'] = np.unravel_index(np.argmax(magnitude_spectrum), magnitude_spectrum.shape)
#     features['total_energy'] = np.sum(magnitude_spectrum**2)
    
#     return features


# def extract_edge_features(image):
#     """
#     Extracts edge-based features from an image using Canny edge detection.

#     Parameters:
#     - image (ndarray): The input image.

#     Returns:
#     - dict: A dictionary containing the extracted edge features.
#     """

#     edges = canny(image)
#     print(edges.sum())


#     features = {}
#     features['edge_density'] = np.sum(edges) / edges.size
#     features['mean_edge_intensity'] = np.mean(image[edges])
    
#     return features


# def _get_bit_depth(image):
#     bit_depth = int(np.ceil(np.log2(np.max(image))))
#     if bit_depth<=8:
#         return 8
#     elif bit_depth<=12:
#         return 12
#     elif bit_depth<=16:
#         return 16
#     else:
#         print('The image is more than 16-bit.')
#         return None
    
# def _img_to_uint8(image):
#     bit_depth = _get_bit_depth(image)
#     num_levels = 2**bit_depth
#     return (255*(image/num_levels)).astype('uint8')


class Sharpness:
    image: np.ndarray | None = None

    # def __init__(self, image: np.ndarray) -> None:
    #     if not isinstance(image, np.ndarray):
    #         raise TypeError("Input must be Numpy array")
        
    #     self.image = image

    def set_image(self, image: np.ndarray) -> None:
        if not isinstance(image, np.ndarray):
            raise TypeError("Input must be Numpy array")
        
        self.image = image


    def variance_of_laplacian(self):
        """
        Computes the variance of the Laplacian of the image.
        """
        laplacian = cv.Laplacian(self.image, cv.CV_64F)
        variance = laplacian.var()
        return variance

    def tenengrad(self):
        """
        Computes the Tenengrad focus measure.
        """
        # Convert to 64-bit float for precision
        image_float = self.image.astype(np.float64)
        # Sobel filters
        gx = cv.Sobel(image_float, cv.CV_64F, 1, 0, ksize=3)
        gy = cv.Sobel(image_float, cv.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(gx**2 + gy**2)
        tenengrad_value = np.mean(gradient_magnitude)
        return tenengrad_value

    def brenners_gradient(self):
        """
        Computes Brenner's gradient focus measure.
        """
        shifted_image = np.roll(self.image, -2, axis=0)
        diff = (self.image - shifted_image) ** 2
        brenner_value = np.sum(diff)
        return brenner_value
    
    def fft_sharpness(self):
        
        # Convert to float32 for precision
        img_float = np.float32(self.image)

        # Step 2: Apply Fourier Transform
        f = np.fft.fft2(img_float)

        # Step 3: Shift the zero-frequency component to the center
        fshift = np.fft.fftshift(f)

        # Compute the magnitude spectrum
        magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1)  # Added 1 to avoid log(0)

        return np.mean(magnitude_spectrum)
    
    def extract_all_features(self):
        return {
            'laplacian' : self.variance_of_laplacian(),
            'tenengrad' : self.tenengrad(),
            'brenners_gradient' : self.brenners_gradient(),
            'fourier_magnitude' : self.fft_sharpness()
        }
    


class Noise:
    image: np.ndarray | None = None

    # def __init__(self, image: np.ndarray) -> None:
    #     if not isinstance(image, np.ndarray):
    #         raise TypeError("Input must be Numpy array")
        
    #     self.image = image

    def set_image(self, image: np.ndarray) -> None:
        if not isinstance(image, np.ndarray):
            raise TypeError("Input must be Numpy array")
        
        self.image = image

    def noise_level_estimation(self):
        """
        Estimates the noise level in the image.
        """
        sigma_est = estimate_sigma(self.image, average_sigmas=True)

        if np.isnan(sigma_est):
            return 0

        return sigma_est
    
    def signal_to_noise_ratio(self):
        """
        Computes the SNR of the image.
        If signal_region_coords is provided, it should be a tuple: (x, y, width, height)
        defining the region containing the signal.
        """
        # Assuming the background is the darker region
        mean_signal = np.mean(self.image)
        std_noise = np.std(self.image)
        snr = mean_signal / std_noise if std_noise != 0 else 0
        
        return snr
    
    def extract_all_features(self):
        return {
            'noise_level' : self.noise_level_estimation(),
            'snr' : self.signal_to_noise_ratio()
        }
    

class IntensityFeatures:
    def __init__(self, image=None, bit_depth=None):
        """
        Initializes the IntensityFeatures.

        Parameters:
        - image (ndarray, optional): Image array.
        - bit_depth (int, optional): Bit depth of the image.
        """
        self.bit_depth = bit_depth
        if image is not None:
            self.set_image(image)

    def set_image(self, image):
        """
        Sets the image and computes necessary parameters.

        Parameters:
        - image (ndarray): Image array.
        """
        self.image = image
        if self.bit_depth is None:
            self.bit_depth = self._get_bit_depth()
        self.num_bins = 2 ** self.bit_depth
        self.normalized_image = self._normalize_image()

    def _get_bit_depth(self):
        return 12
        # bit_depth = int(np.ceil(np.log2(np.max(self.image))))
        # if bit_depth<=8:
        #     return 8
        # elif bit_depth<=12:
        #     return 12
        # elif bit_depth<=16:
        #     return 16
        # else:
        #     print('The image is more than 16-bit.')
        #     return None

    def _normalize_image(self):
        """
        Normalizes the image for histogram and statistical calculations.

        Returns:
        - ndarray: Normalized image.
        """
        image = self.image.astype(np.float64)
        image /= (self.num_bins - 1)
        return img_as_float(image)

    def mean_intensity(self):
        """Calculates the mean intensity of the image."""
        return np.mean(self.image)

    def median_intensity(self):
        """Calculates the median intensity of the image."""
        return np.median(self.image)

    def std_intensity(self):
        """Calculates the standard deviation of the image intensity."""
        return np.std(self.image)

    def variance(self):
        """Calculates the variance of the image intensity."""
        return np.var(self.image)

    def min_intensity(self):
        """Finds the minimum intensity in the image."""
        return np.min(self.image)

    def max_intensity(self):
        """Finds the maximum intensity in the image."""
        return np.max(self.image)

    def dynamic_range(self):
        """Calculates the range of intensities in the image."""
        return self.max_intensity() - self.min_intensity()
    
    def dynamic_range_utilization(self):
        """Calculates the range of intensities in the image."""
        return self.dynamic_range()/(2**self.bit_depth - 1)

    def histogram(self):
        """Calculates the histogram of the image."""
        hist, _ = np.histogram(self.normalized_image.flatten(), bins=self.num_bins, range=(0, 1))
        return hist

    def entropy(self):
        """Calculates the entropy of the image histogram."""
        hist = self.histogram()
        hist = hist / np.sum(hist)  # Normalize histogram to probabilities
        return entropy(hist)

    def skewness(self):
        """Calculates the skewness of the image intensity distribution."""
        sk = skew(self.normalized_image.flatten())
        if np.isnan(sk):
            return 0

        return sk

    def kurtosis(self):
        """Calculates the kurtosis of the image intensity distribution."""
        kurt =  kurtosis(self.normalized_image.flatten())
        if np.isnan(kurt):
            return 0
    
        return kurt

    def extract_all_features(self):
        """
        Extracts all intensity-based features from the image.

        Returns:
        - dict: A dictionary containing all extracted features.
        """
        return {
            'mean_intensity': self.mean_intensity(),
            'median_intensity': self.median_intensity(),
            'std_intensity': self.std_intensity(),
            'variance': self.variance(),
            'min_intensity': self.min_intensity(),
            'max_intensity': self.max_intensity(),
            'dynamic_range': self.dynamic_range(),
            'dynamic_range_utilization': self.dynamic_range_utilization(),
            'bit_depth': self.bit_depth,
            'histogram': self.histogram(),
            'entropy': self.entropy(),
            'skewness': self.skewness(),
            'kurtosis': self.kurtosis(),
        }
    

class TextureFeatures:
    def __init__(self):
        self.image = None

    def set_image(self, image):
        """
        Sets the image for feature extraction.

        Parameters:
        - image (ndarray): The input image.
        """
        self.image = image

    def _img_to_uint8(self, image):
        """
        Converts an image to uint8 format, adjusting for bit depth.

        Parameters:
        - image (ndarray): The input image.

        Returns:
        - ndarray: The image converted to uint8 format.
        """
        # Normalize the image to the range 0-255 and convert to uint8
        image = image - image.min()
        if image.max() > 0:
            image = (image / image.max()) * 255
        return image.astype(np.uint8)

    def glcm_features(self, distances=None, angles=None):
        """
        Extracts texture-based features from the image using GLCM.

        Parameters:
        - distances (list of int, optional): Distances for GLCM computation.
        - angles (list of float, optional): Angles for GLCM computation.

        Returns:
        - dict: A dictionary containing the extracted texture features.
        """
        if self.image is None:
            raise ValueError("Image not set. Use set_image method to set the image.")

        # Define default distances and angles if not provided
        if distances is None:
            distances = [1, 2, 4, 8]
        if angles is None:
            angles = [0, np.pi/4, np.pi/2, 3*np.pi/4]

        # Convert image to uint8
        image_uint8 = self._img_to_uint8(self.image)

        # Compute GLCM
        glcm = graycomatrix(
            image_uint8,
            distances=distances,
            angles=angles,
            symmetric=True,
            normed=True
        )

        # Extract texture features
        features = {
            'contrast': graycoprops(glcm, 'contrast').mean(),
            'dissimilarity': graycoprops(glcm, 'dissimilarity').mean(),
            'homogeneity': graycoprops(glcm, 'homogeneity').mean(),
            'energy': graycoprops(glcm, 'energy').mean(),
            'correlation': graycoprops(glcm, 'correlation').mean(),
            'ASM': graycoprops(glcm, 'ASM').mean(),
        }

        return features

    def lbp_features(self, radius=1, n_points=8):
        """
        Extracts texture-based features from the image using Local Binary Patterns (LBP).

        Parameters:
        - radius (int, optional): The radius of the circle. Default is 1.
        - n_points (int, optional): Number of points to consider for LBP. Default is 8.

        Returns:
        - dict: A dictionary containing the extracted LBP features.
        """
        if self.image is None:
            raise ValueError("Image not set. Use set_image method to set the image.")

        # Compute LBP
        lbp = local_binary_pattern(
            self.image,
            n_points,
            radius,
            method='uniform'
        )
        
        # Fixed number of bins for uniform LBP
        n_bins = n_points + 2  # +2 accounts for uniform and non-uniform patterns
        
        lbp_hist, _ = np.histogram(
            lbp,
            bins=n_bins,
            range=(0, n_bins),
            density=True
        )
        
        # Ensure the histogram length is always n_bins, even if some bins have 0 values
        features = {f'lbp_bin_{i}': lbp_hist[i] if i < len(lbp_hist) else 0 for i in range(n_bins)}

        return features

    
    def extract_all_features(self):
        """
        Extracts all texture features from the image by combining GLCM and LBP features.

        Returns:
        - dict: A dictionary containing all the extracted texture features.
        """
        if self.image is None:
            raise ValueError("Image not set. Use set_image method to set the image.")

        # Extract GLCM features
        glcm_feats = self.glcm_features()

        # Extract LBP features
        lbp_feats = self.lbp_features()

        # Combine the features
        all_features = {**glcm_feats, **lbp_feats}

        return all_features
