import pandas as pd
import numpy as np
from sklearn.decomposition import PCA

class FeaturePCA:
    def __init__(self):
        self.data = None
        self.pca_results = {}

    def set_data(self, data_path: str):
        """
        Loads and sets the data from a CSV file.

        Args:
            data_path (str): Path to the CSV file containing the data.
        """
        self.data = pd.read_csv(data_path)
    
    def _get_pca(self, df: pd.DataFrame, n_components=2):
        """
        Performs PCA on the given dataframe and returns the principal components.

        Args:
            df (pd.DataFrame): DataFrame with selected features.
            n_components (int): Number of principal components to compute.

        Returns:
            pd.DataFrame: DataFrame with principal components.
        """
        pca = PCA(n_components=n_components)
        pca_components = pca.fit_transform(df)
        columns = [f'pca_{i+1}' for i in range(n_components)]
        return pd.DataFrame(pca_components, columns=columns)

    def get_intensity_pca(self, n_components=2):
        """
        Performs PCA on the intensity features.

        Args:
            n_components (int): Number of principal components to compute.

        Returns:
            pd.DataFrame: DataFrame with intensity PCA results.
        """
        intensity_columns = ['mean_intensity', 'median_intensity', 'std_intensity', 'variance', 
                             'min_intensity', 'max_intensity', 'dynamic_range', 'dynamic_range_utilization', 
                             'bit_depth', 'entropy', 'skewness', 'kurtosis']
        intensity_df = self.data[intensity_columns]
        intensity_pca = self._get_pca(intensity_df, n_components)
        self.pca_results['intensity'] = intensity_pca
        return intensity_pca

    def get_texture_pca(self, n_components=2):
        """
        Performs PCA on the texture features.

        Args:
            n_components (int): Number of principal components to compute.

        Returns:
            pd.DataFrame: DataFrame with texture PCA results.
        """
        texture_columns = ['contrast', 'dissimilarity', 'homogeneity', 'energy', 'correlation', 'ASM', 
                           'lbp_bin_0', 'lbp_bin_1', 'lbp_bin_2', 'lbp_bin_3', 'lbp_bin_4', 'lbp_bin_5',
                             'lbp_bin_6', 'lbp_bin_7', 'lbp_bin_8', 'lbp_bin_9']
        texture_df = self.data[texture_columns]
        texture_pca = self._get_pca(texture_df, n_components)
        self.pca_results['texture'] = texture_pca
        return texture_pca

    def get_noise_pca(self, n_components=2):
        """
        Performs PCA on the noise features.

        Args:
            n_components (int): Number of principal components to compute.

        Returns:
            pd.DataFrame: DataFrame with noise PCA results.
        """
        noise_columns = ['noise_level', 'snr']
        noise_df = self.data[noise_columns]
        self.pca_results['noise'] = noise_df
        return noise_df

    def get_sharpness_pca(self, n_components=2):
        """
        Performs PCA on the sharpness features.

        Args:
            n_components (int): Number of principal components to compute.

        Returns:
            pd.DataFrame: DataFrame with sharpness PCA results.
        """
        sharpness_columns = ['laplacian', 'tenengrad', 'brenners_gradient', 'fourier_magnitude']
        sharpness_df = self.data[sharpness_columns]
        sharpness_pca = self._get_pca(sharpness_df, n_components)
        self.pca_results['sharpness'] = sharpness_pca
        return sharpness_pca

    def get_all_pca(self, n_components=2):
        """
        Performs PCA on all features.

        Args:
            n_components (int): Number of principal components to compute.

        Returns:
            pd.DataFrame: DataFrame with all PCA results.
        """
        feature_columns = [col for col in self.data.columns if col not in ['file_path', 'image_name', 'extension', 'T', 'C', 'Z', 'histogram']]
        feature_df = self.data[feature_columns]
        all_pca = self._get_pca(feature_df, n_components)
        self.pca_results['all'] = all_pca
        return all_pca

    def combine_pcas(self):
        """
        Combines all PCA results into a single dataframe with additional columns for the PCA components.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries with the image file path and PCA results for intensity, texture, noise, and sharpness.
        """
        combined_df = pd.DataFrame()
        combined_df[['file_path', 'image_name', 'extension', 'T', 'C', 'Z', 'histogram']] = self.data[['file_path', 'image_name', 'extension', 'T', 'C', 'Z', 'histogram']]

        # Add all PCA components for each feature group to the combined dataframe
        if 'intensity' in self.pca_results:
            combined_df = pd.concat([combined_df, self.pca_results['intensity'].add_prefix('intensity_')], axis=1)
        if 'texture' in self.pca_results:
            combined_df = pd.concat([combined_df, self.pca_results['texture'].add_prefix('texture_')], axis=1)
        if 'noise' in self.pca_results:
            combined_df = pd.concat([combined_df, self.pca_results['noise'].add_prefix('noise_')], axis=1)
        if 'sharpness' in self.pca_results:
            combined_df = pd.concat([combined_df, self.pca_results['sharpness'].add_prefix('sharpness_')], axis=1)
        if 'all' in self.pca_results:
            combined_df = pd.concat([combined_df, self.pca_results['all'].add_prefix('pca_all_')], axis=1)

        # Convert the combined dataframe to a list of dictionaries
        return combined_df.to_dict(orient='records')
    

class MetadataAnalysis:
    """
    A class to analyze ND2 metadata from a CSV file and perform various checks.
    """

    def __init__(self):
        self.metadata = None
        self.csv_path = None

    def set_csv_path(self, path: str):
        """Sets the CSV path and loads the data."""
        self.csv_path = path
        self.metadata = pd.read_csv(path)
        self.metadata['delta_time'] = self.metadata.groupby(['image_name', 'the_c'])['delta_t'].diff()

    def _convert_time(self):
        df = self.metadata
        time_unit = df.delta_t_unit.unique()[0].split('.')[-1].lower()
        delta_time = df.delta_time[3]
        units = ['millisecond', 'second', 'minute', 'hour', 'day', 'month', 'year']
        index = units.index(time_unit)
        divisers = [1000, 60, 60, 24, 30, 12, 365]
        diviser = 1
        for i, d in enumerate(divisers[index:]):
            if (delta_time/d) > 1:
                delta_time = delta_time/d
                diviser = diviser*d
            else:
                return diviser, units[i-1]

    def _get_generic_info(self, column):
        """Generic function to return the number of unique items and their values."""
        n_unique = self.metadata[column].nunique()
        unique_values = self.metadata[column].unique()
        return n_unique, unique_values

    def get_extension(self):
        n_extension, extensions = self._get_generic_info('extension')
        
        if n_extension > 1:
            return f"[x] More than one image type found. Found extensions are {extensions}."
        return f"[v] All images are of {extensions[0]} type."

    def get_instrument(self):
        n_instrument, instruments = self._get_generic_info('instrument_model')

        if n_instrument is None:
            return f"[x] Could not find the instrument name."
        
        if n_instrument > 1:
            return f"[x] More than one instrument found. Found instruments are {instruments}."
        
        return f"[v] All images are acquired using {instruments[0]}."

    def get_lensNA(self):
        n_lensNA, lensNA = self._get_generic_info('objective_lens_na')

        if n_lensNA is None:
            return f"[x] Could not find the lens objective."
        
        if n_lensNA > 1:
            return f"[x] More than single lens objective found. Found lens objectives are {lensNA}."
        
        return f"[v] All images are acquired with {lensNA[0]} objective."

    def get_magnification(self):
        n_magnification, magnifications = self._get_generic_info('objective_nominal_magnification')

        if n_magnification is None:
            return f"[x] Could not find the lens magnification."
        
        if n_magnification > 1:
            return f"[x] More than single magnification found. Found magnifications are {magnifications}."
        return f"[v] All images are acquired with {int(magnifications[0])}x."

    def get_bit_depth(self):
        n_bit_depth, bit_depths = self._get_generic_info('significant_bits')
        if n_bit_depth is None:
            return f"[x] Could not find bit depth."
        
        if n_bit_depth > 1:
            return f"[x] More than single bit depth found. Found bit depths are {bit_depths}."
        return f"[v] All images are acquired with {bit_depths[0]}."

    def get_size_x(self):
        n_size_x, size_x = self._get_generic_info('size_x')
        if n_size_x is None:
            return f"[x] Could not find image width."
        
        if n_size_x > 1:
            return f"[x] Different image widths found."
        return f"[v] Images have width {size_x[0]}."

    def get_size_y(self):
        n_size_y, size_y = self._get_generic_info('size_y')
        if n_size_y is None:
            return f"[x] Could not find image height."
        
        if n_size_y > 1:
            return f"[x] Different image heights found."
        return f"[v] Images have height {size_y[0]}."

    def get_size_z(self):
        n_size_z, size_z = self._get_generic_info('size_z')
        if n_size_z is None:
            return f"[x] Could not find z-depth."
        
        if n_size_z > 1:
            return f"[?] 3D z-stack with different z-depth."
        elif size_z != 1:
            return f"[?] 3D z-stack with single z-depth of {size_z[0]}."
        return f"[?] Not a z-stack."

    def get_size_t(self):
        n_size_t, size_t = self._get_generic_info('size_t')
        if n_size_t is None:
            return f"[?] Could not find t or not a time series."
        if n_size_t > 1:
            return f"[?] Time series data with different time."
        elif size_t != 1:
            return f"[?] Time series data with {size_t[0]} frames per image."
        return f"[?] Not a time series data."

    def get_size_c(self):
        n_size_c, size_c = self._get_generic_info('size_c')
        if n_size_c is None:
            return f"[x] Could not find number of channels."
        
        if n_size_c > 1:
            return f"[x] Different number of channels found."
        elif size_c == 1:
            return f"[?] Single channel image."
        return f"[v] Multi-channel image with {size_c[0]} channels per image."

    def get_physical_x(self):
        n_physical_size_x, physical_size_x = self._get_generic_info('physical_size_x')
        if n_physical_size_x is None:
            return f"[x] Could not find physical x size."
        
        if n_physical_size_x > 1:
            return f"[x] Different physical size x found. Found physical size x are {np.round(physical_size_x, 4)}."
        return f"[v] All images acquired have {np.round(physical_size_x[0], 4)} micrometers physical size x."

    def get_physical_y(self):
        n_physical_size_y, physical_size_y = self._get_generic_info('physical_size_y')
        if n_physical_size_y is None:
            return f"[x] Could not find physical y size."
        
        if n_physical_size_y > 1:
            return f"[x] Different physical size y found. Found physical size y are {np.round(physical_size_y, 4)}."
        return f"[v] All images acquired have {np.round(physical_size_y[0], 4)} micrometers physical size y."

    def get_delta_t(self):
        try:
            diviser, unit = self._convert_time()
            self.metadata['delta_time'] = np.round(self.metadata['delta_time'] / diviser, 2)
            mean_time = self.metadata['delta_time'].mean()
            std_time = self.metadata['delta_time'].std()
            return f"[v] Time between frames: {np.round(mean_time, 4)} +/- {np.round(std_time, 4)} {unit}s."
        
        except:
            return f"[x] Cound not find time delta."

    def generate_report(self):
        """Generates a report by calling all functions and combining their outputs into a list of strings."""
        report = []
        report.append(self.get_extension())
        report.append(self.get_instrument())
        report.append(self.get_lensNA())
        report.append(self.get_magnification())
        report.append(self.get_bit_depth())
        report.append(self.get_size_t())
        report.append(self.get_size_z())
        report.append(self.get_size_c())
        report.append(self.get_size_x())
        report.append(self.get_size_y())
        report.append(self.get_physical_x())
        report.append(self.get_physical_y())
        report.append(self.get_delta_t())
        return report