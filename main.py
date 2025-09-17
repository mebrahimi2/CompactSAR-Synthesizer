import os
import sys
from PyQt6 import QtWidgets, QtCore
from FP_to_CP_GUI import Ui_MainWindow
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QSplashScreen, QApplication
from functions import *
from osgeo import gdal

class FP_to_CP(QtWidgets.QMainWindow):
    def __init__(self):
        super(FP_to_CP, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.FP_image_reader.clicked.connect(self.image_reader)
        self.ui.lut_file.clicked.connect(self.calibration)
        self.ui.Convert_to_CP.clicked.connect(self.simualtion_to_cp)
        self.ui.log_text.append("Welcome! Ready to start processing.")
        
        self.images_loaded = False
        self.calibration_done = False
    
    def image_reader(self):
        RADARSAT2 = self.ui.radarsat2.isChecked()
        alos_palsar = self.ui.alosPalsar.isChecked()
        
        self.images_loaded = False
        self.calibration_done = False
        
        if RADARSAT2:
            files, _ = QFileDialog.getOpenFileNames(
                self,
                "Select 4 Images",
                "",
                "TIF Files (*.tif *.tiff)"
            )
            
            if len(files) != 4:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.setWindowTitle("Warning")
                msg_box.setText("You must select exactly 4 .tif images!")
                msg_box.setStyleSheet("QLabel{color: red; font-weight: bold;}")
                msg_box.exec()
            else:
                self.paths = {}
                keys = ["HH", "HV", "VH", "VV"]
                
                for i, file_path in enumerate(files):
                    self.paths[keys[i]] = file_path
                    
                self.image_paths = self.paths
                
                self.ui.log_text.append("Selected Images:")
                for key, full_path in self.paths.items():
                    self.ui.log_text.append(f"{key}: {full_path}")
                
                self.image_array = radarsat2_reader(self.paths)
                
                if all(self.image_array[key] is not None for key in self.image_array):
                    self.ui.log_text.append("Images read successfully")
                    self.images_loaded = True
                    row, column = self.image_array["HH"].shape[1:3]
                    self.ui.log_text.append(f"Image rows = {row} and image columns = {column}")
                else:
                    self.ui.log_text.append("Error: One or more images could not be read!")
        
        elif alos_palsar:
            filepath, _ = QFileDialog.getOpenFileName(
                self,
                "Select ALOS-PALSAR Image",
                "",
                "ALOS-PALSAR Files (VOL-ALPSRP*.1__A)"
            )
            
            if filepath:
                self.ui.log_text.append(f"Selected ALOS-PALSAR file: {filepath}")
                
                palsar = gdal.Open(filepath)
                if palsar is not None:
                    self.paths = {'HH': filepath}
                    self.ui.log_text.append("ALOS-PALSAR image loaded successfully")
                    
                    number_of_cols = palsar.RasterXSize
                    number_of_rows = palsar.RasterYSize
                    number_of_bands = palsar.RasterCount
                    
                    self.ui.log_text.append(f"Image dimensions: {number_of_rows} rows, {number_of_cols} columns")
                    self.ui.log_text.append(f"Number of bands: {number_of_bands}")
                    
                    if number_of_bands >= 4:
                        HH = palsar.GetRasterBand(1)
                        HV = palsar.GetRasterBand(2)
                        VH = palsar.GetRasterBand(3)
                        VV = palsar.GetRasterBand(4)
                        
                        self.image_array = {
                            "HH": HH.ReadAsArray(),
                            "HV": HV.ReadAsArray(),
                            "VH": VH.ReadAsArray(),
                            "VV": VV.ReadAsArray()
                        }
                        
                        self.ui.log_text.append("ALOS-PALSAR images read successfully")
                        self.images_loaded = True
                        
                        row, column = self.image_array["HH"].shape
                        self.ui.log_text.append(f"Band dimensions: {row} rows, {column} columns")
                    else:
                        self.ui.log_text.append("Error: The selected file does not contain the required 4 bands (HH, HV, VH, VV).")
                else:
                    self.ui.log_text.append("Error: Unable to open the selected ALOS-PALSAR file.")
        
    def calibration(self):
        if not self.images_loaded:
            QMessageBox.warning(self, "Warning", "Please import images before calibration!")
            return

        RADARSAT2 = self.ui.radarsat2.isChecked()
        alos_palsar = self.ui.alosPalsar.isChecked()
        
        if RADARSAT2:
            xml_file, _ = QFileDialog.getOpenFileName(
                self, "Select Calibration XML File", "", "XML Files (*.xml)"
            )
            
            if not xml_file:
                QMessageBox.warning(self, "Warning", "No XML file selected!")
                return
            
            self.ui.log_text.append(f"Selected Calibration XML: {xml_file}")
            offset, gains = gains_offset_reader_xml(xml_file)
            if offset is None or gains is None:
                self.ui.log_text.append("Failed to load LUT. Calibration aborted.")
                return

            self.ui.log_text.append("Look-Up Table (LUT) for RADARSAT-2 calibration loaded successfully.")
            
            HH_array, HV_array, VH_array, VV_array = self.image_array.values()
            rows, _ = HH_array.shape[1:3]
            
            self.I_HH_cal, self.Q_HH_cal = Radarsat2_calibration(HH_array, gains, offset, rows)
            self.I_HV_cal, self.Q_HV_cal = Radarsat2_calibration(HV_array, gains, offset, rows)
            self.I_VH_cal, self.Q_VH_cal = Radarsat2_calibration(VH_array, gains, offset, rows)
            self.I_VV_cal, self.Q_VV_cal = Radarsat2_calibration(VV_array, gains, offset, rows)
            
            self.ui.log_text.append("RADARSAT-2 Calibration successfully applied on bands")
            self.calibration_done = True

        elif alos_palsar:
            CF, CF_offset = -83, 32
            const = db_to_linear_scale(CF - CF_offset)
            
            HH_array, HV_array, VH_array, VV_array = self.image_array.values()
            
            self.I_HH_cal, self.Q_HH_cal, _, _ = ALOS_calibration(HH_array, const)
            self.I_HV_cal, self.Q_HV_cal, _, _ = ALOS_calibration(HV_array, const)
            self.I_VH_cal, self.Q_VH_cal, _, _ = ALOS_calibration(VH_array, const)
            self.I_VV_cal, self.Q_VV_cal, _, _ = ALOS_calibration(VV_array, const)
            
            self.ui.log_text.append("ALOS PALSAR Calibration successfully applied on bands")
            self.calibration_done = True

        
    def simualtion_to_cp(self):
        if not self.images_loaded:
            QMessageBox.warning(self, "Error", "Please import images first!")
            return

        if not self.calibration_done:
            QMessageBox.warning(self, "Error", "Please perform calibration before simulation!")
            return

        S11, S12, S22 = FP_scattering_matrix(self.I_HH_cal, self.Q_HH_cal, self.I_HV_cal, self.Q_HV_cal,
                                            self.I_VH_cal, self.Q_VH_cal, self.I_VV_cal, self.Q_VV_cal)
        RHV_mode = self.ui.RHV.isChecked()
        LHV_mode = self.ui.LHV.isChecked()
        pi4_mode = self.ui.PI4.isChecked()
        
        scattering_selected = self.ui.Scattering.isChecked()
        covariance_selected = self.ui.Covariance.isChecked()
        
        if not (RHV_mode or LHV_mode or pi4_mode):
            QMessageBox.warning(self, "Error", "Please select one of the simulation modes (RHV, LHV, or Pi/4).")
            return

        if not (scattering_selected or covariance_selected):
            QMessageBox.warning(self, "Error", "Please select at least one feature (Scattering vector or Covariance matrix).")
            return
        
        S11_C, S21_C = None, None
        C11, C12, C22 = None, None, None
        folder_name = ""

        if RHV_mode:
            folder_name = "_RHV"
            S11_C, S21_C = RHV_simulator(S11, S12, S22)
        elif LHV_mode:
            folder_name = "_LHV"
            S11_C, S21_C = LHV_simulator(S11, S12, S22)
        elif pi4_mode:
            folder_name = "_pi4"
            S11_C, S21_C = pi4_simulator(S11, S12, S22)

        if covariance_selected:
            self.ui.log_text.append("Covariance matrix selected. Processing...")
            C11, C12, C22 = covariance_matrix_function(S11_C, S21_C)
                
        if scattering_selected:
            folder_s = "S2" + folder_name
            os.makedirs(folder_s, exist_ok=True)
            self.ui.log_text.append(f"Saving scattering vector results to '{folder_s}' folder...")
            save_single_band_tif(os.path.join(folder_s, "S11_real.tif"), S11_C.real, self.paths['HH'])
            save_single_band_tif(os.path.join(folder_s, "S11_imag.tif"), S11_C.imag, self.paths['HH'])
            save_single_band_tif(os.path.join(folder_s, "S21_real.tif"), S21_C.real, self.paths['HH'])
            save_single_band_tif(os.path.join(folder_s, "S21_imag.tif"), S21_C.imag, self.paths['HH'])

        if covariance_selected:
            folder_c = "C2" + folder_name
            os.makedirs(folder_c, exist_ok=True)
            self.ui.log_text.append(f"Saving covariance matrix results to '{folder_c}' folder...")
            save_single_band_tif(os.path.join(folder_c, "C11.tif"), C11, self.paths['HH'])
            save_single_band_tif(os.path.join(folder_c, "C12_real.tif"), C12.real, self.paths['HH'])
            save_single_band_tif(os.path.join(folder_c, "C12_imag.tif"), C12.imag, self.paths['HH'])
            save_single_band_tif(os.path.join(folder_c, "C22.tif"), C22, self.paths['HH'])
            
        self.ui.log_text.append("Simulation completed successfully. Results have been saved.")
    
def main():
    app = QApplication(sys.argv)
    
    try:
        original_pixmap = QPixmap('logo.png')
        scaled_pixmap = original_pixmap.scaled(400, 400, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
        splash = QSplashScreen(scaled_pixmap)
        splash.show()
        app.processEvents()
    except Exception as e:
        print(f"Could not load or show splash screen: {e}. 'logo.png' might be missing or invalid.")
        splash = None

    win = FP_to_CP()
    win.setWindowTitle("CompactSAR Synthesizer")
    win.setWindowIcon(QIcon('logo.png'))

    if splash:
        QtCore.QTimer.singleShot(3000, lambda: (splash.close(), win.show()))
    else:
        win.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()