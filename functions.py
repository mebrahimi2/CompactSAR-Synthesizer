import rasterio
from rasterio.errors import RasterioIOError
import numpy as np
import xml.etree.ElementTree as ET

def radarsat2_reader(paths):
    arrays = {}
    for polarization, path in paths.items():
        try:
            with rasterio.open(path) as dataset:
                arrays[polarization] = dataset.read()
        except RasterioIOError:
            print(f"File not found or cannot be opened: {path}")
            arrays[polarization] = None
    
    return arrays


def print_min_max_mean_std(array):
    print(array.min(), array.max(), np.mean(array), np.std(array))

def gains_offset_reader_xml(file_path):
    try:
        # Parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Try to find the 'offset' element
        offset_element = root.find("offset")
        if offset_element is None:
            raise ValueError("Offset element not found in XML file.")
        
        # Try to convert the offset to float
        offset = float(offset_element.text)
        
        # Try to find the 'gains' element
        gains_element = root.find("gains")
        if gains_element is None:
            raise ValueError("Gains element not found in XML file.")
        
        # Parse the gains values
        gains_text = gains_element.text
        gains = gains_text.strip().split()  # Splitting space-separated values
        
        # Convert the gains to a NumPy array
        gains_array = np.array(gains, dtype=np.float32)
        
        return offset, gains_array

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None, None

    except ET.ParseError:
        print(f"Error: Failed to parse XML file '{file_path}'.")
        return None, None

    except ValueError as ve:
        print(f"Error: {ve}")
        return None, None

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None, None
    
def Radarsat2_calibration(IQ_band, gains, offset, row_number):
    try:
        gains_array = np.tile(gains, (row_number, 1))
        
        I_calibrated = (IQ_band[0] - offset) / gains_array  # Real
        Q_calibrated = (IQ_band[1] - offset) / gains_array  # Imaginary

        return I_calibrated, Q_calibrated
    
    except Exception as e:
        print(f"An error occurred during calibration: {e}")
        return None, None
    
def db_to_linear_scale(db_array):
    array = 10 ** (db_array / 10)
    return array

def ALOS_calibration(IQ_band, const):
    try:
        I_calibrated = IQ_band.real * np.sqrt(const) # Real
        Q_calibrated = IQ_band.imag * np.sqrt(const) # Imagery
        # SNAP intensity == simga0, amplitude
        intensity = np.absolute(IQ_band) * np.sqrt(const)
        sigma0 = (np.absolute(IQ_band) ** 2) * const # amplitude
        return I_calibrated, Q_calibrated, intensity,  sigma0
    except Exception as e:
        print(f"An error occurred during calibration: {e}")
        return None, None
    
def FP_scattering_matrix(I_HH, Q_HH, I_HV, Q_HV, I_VH, Q_VH, I_VV, Q_VV):  # FP = Fully polarimetric
    try:
        # Step 1: Calculate real and imaginary components for each scattering element
        I_S11, Q_S11 = I_HH, Q_HH
        I_S12 = (I_HV + I_VH) / 2
        Q_S12 = (Q_HV + Q_VH) / 2
        I_S22, Q_S22 = I_VV, Q_VV
        
        # Step 2: Combine real and imaginary parts into complex numbers
        S11 = I_S11 + 1j * Q_S11
        S12 = I_S12 + 1j * Q_S12
        S22 = I_S22 + 1j * Q_S22
        
        return S11, S12, S22
    
    except Exception as e:
        print(f"An error occurred in FP_scattering_matrix: {e}")
        return None, None, None
    
def RHV_simulator(FP_S11, FP_S12, FP_S22): # Hybrid pol mode (transmits right circular)
    coefficent = 1 / np.sqrt(2)
    S_RH = coefficent * (FP_S11 - (complex(0, 1.0) * FP_S12))
    S_RV = coefficent * ((- (complex(0, 1.0) * FP_S22) + FP_S12))
    return S_RH, S_RV

def LHV_simulator(FP_S11, FP_S12, FP_S22): # Hybrid pol mode (transmits left circular)
    coefficent = 1 / np.sqrt(2)
    S_LH = coefficent * (FP_S11 + (complex(0, 1.0) * FP_S12))
    S_LV = coefficent * ((+ (complex(0, 1.0) * FP_S22) + FP_S12))
    return S_LH, S_LV

def pi4_simulator(FP_S11, FP_S12, FP_S22): # pi4 mode 
    coefficent = 1 / np.sqrt(2)
    S1_pi4 = coefficent * (FP_S11 + FP_S12)
    S2_pi4 = coefficent * (FP_S22 + FP_S12)
    return S1_pi4, S2_pi4

def covariance_matrix_function(S11, S21):
    C11 = (S11 * np.conj(S11)).real
    C12 = S11 * np.conj(S21)
    C22 = (S21 * np.conj(S21)).real
    return C11, C12, C22

def save_single_band_tif(output_path, data, reference_image_path):
    with rasterio.open(reference_image_path) as ref_image:
        meta = ref_image.meta.copy()
        meta.update({
            'count': 1,  
            'dtype': 'float32',
            'driver': 'GTiff'
        })
        with rasterio.open(output_path, 'w', **meta) as dst:
            dst.write(data, 1) 