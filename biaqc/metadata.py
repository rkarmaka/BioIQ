import tifffile

def read_tiff_metadata(file_path):
    """
    Reads metadata from a TIFF file.

    Parameters:
    - file_path (str): Path to the TIFF file.

    Returns:
    - dict: A dictionary containing the metadata.
    """
    with tifffile.TiffFile(file_path) as tif:
        metadata = tif.pages[0].tags
        metadata_dict = {tag.name: tag.value for tag in metadata.values()}

    return metadata_dict

