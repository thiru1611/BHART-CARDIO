# Standard library imports
import os
import re

# Third-party imports
from pytesseract import pytesseract, TesseractNotFoundError

# Application-specific imports
from digitization.Image import Image
from digitization.DigitizationError import DigitizationError

# Set the path to the Tesseract executable
pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class MetadataExtractor:
    """
    OCR to extract metadata from an ECG.
    """
    
    def __init__(self):
        """
        Initialization of the Metadata OCR.
        """
        pass
    
    def extract_metadata(self, ecg: Image) -> str:
        """
        Extract the metadata of an ECG.

        Args:
            ecg (Image): ECG image.

        Raises:
            DigitizationError: Tesseract OCR-Engine it is not installed in the OS.

        Returns:
            str: String with the metadata of the ECG.
        """
        metadata = ""
        try:
            metadata = pytesseract.image_to_string(ecg.data)
        except TesseractNotFoundError:
            raise DigitizationError(f"Tesseract OCR-Engine installation not found.")
        else:
            # Format metadata
            metadata = re.sub(r"[^a-zA-Z0-9\s\t\n\/\\.,-]+", "", metadata)
            metadata = re.sub(r"(\n|\s|\t)(\n|\s|\t)+", r"\1", metadata)
            return metadata