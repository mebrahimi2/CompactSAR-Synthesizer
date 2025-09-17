from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(980, 750)
        
        font = QtGui.QFont("Segoe UI", 10)
        MainWindow.setFont(font)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.main_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(10)

        self.header_label = QtWidgets.QLabel(self.centralwidget)
        self.header_label.setObjectName("header_label")
        self.header_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.header_label)

        self.top_h_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.top_h_layout)

        # --- Input and Satellite Selection Group ---
        self.input_group = QtWidgets.QGroupBox("1. Select Satellite Data")
        self.input_group_layout = QtWidgets.QGridLayout(self.input_group)
        self.top_h_layout.addWidget(self.input_group, stretch=2)

        self.alosPalsar = QtWidgets.QRadioButton("ALOS-PALSAR")
        self.FP_image_reader = QtWidgets.QPushButton("Import Images")
        self.radarsat2 = QtWidgets.QRadioButton("RADARSAT-2")
        self.lut_file = QtWidgets.QPushButton("Calibration File")

        self.input_group_layout.addWidget(self.alosPalsar, 0, 0)
        self.input_group_layout.addWidget(self.FP_image_reader, 0, 1)
        self.input_group_layout.addWidget(self.radarsat2, 1, 0)
        self.input_group_layout.addWidget(self.lut_file, 1, 1)

        # --- Simulation Mode Group ---
        self.sim_mode_group = QtWidgets.QGroupBox("2. Select Simulation Mode")
        self.sim_mode_layout = QtWidgets.QVBoxLayout(self.sim_mode_group)
        self.top_h_layout.addWidget(self.sim_mode_group, stretch=2)

        self.RHV = QtWidgets.QRadioButton("Right Circular Hybrid mode")
        self.LHV = QtWidgets.QRadioButton("Left Circular Hybrid mode")
        self.PI4 = QtWidgets.QRadioButton("Pi/4 Mode")

        self.sim_mode_layout.addWidget(self.RHV)
        self.sim_mode_layout.addWidget(self.LHV)
        self.sim_mode_layout.addWidget(self.PI4)
        self.sim_mode_layout.addStretch()

        # --- Start Button ---
        self.start_layout = QtWidgets.QVBoxLayout()
        self.top_h_layout.addLayout(self.start_layout, stretch=1)
        
        self.Convert_to_CP = QtWidgets.QPushButton("Start")
        self.Convert_to_CP.setObjectName("Convert_to_CP")
        self.Convert_to_CP.setMinimumHeight(60)
        self.start_layout.addWidget(self.Convert_to_CP)
        self.start_layout.addStretch()


        # --- Bottom Layout (Features and Log) ---
        self.bottom_h_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.bottom_h_layout)

        # --- Features Group ---
        self.features_group = QtWidgets.QGroupBox("3. Select Features to Generate")
        self.features_layout = QtWidgets.QVBoxLayout(self.features_group)
        self.bottom_h_layout.addWidget(self.features_group, stretch=1)

        self.Scattering = QtWidgets.QCheckBox("Scattering vector")
        self.Covariance = QtWidgets.QCheckBox("Covariance matrix")

        self.features_layout.addWidget(self.Scattering)
        self.features_layout.addWidget(self.Covariance)
        self.features_layout.addStretch()

        # --- Log Text Browser ---
        self.log_text = QtWidgets.QTextBrowser(self.centralwidget)
        self.log_text.setObjectName("log_text")
        self.bottom_h_layout.addWidget(self.log_text, stretch=2)
        
        # --- Footer (Email) ---
        self.email_label = QtWidgets.QLabel(self.centralwidget)
        self.email_label.setObjectName("email_label")
        self.email_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.email_label.setOpenExternalLinks(True)
        self.main_layout.addWidget(self.email_label)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)

        self.apply_stylesheet(MainWindow)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def apply_stylesheet(self, MainWindow):
        stylesheet = """
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10pt;
            }
            QMainWindow, #centralwidget {
                background-color: #f7f7f7;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px 5px 10px;
                color: #333;
            }
            QPushButton {
                background-color: #e9e9e9;
                border: 1px solid #c5c5c5;
                padding: 8px 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #dcdcdc;
                border-color: #b5b5b5;
            }
            QPushButton:pressed {
                background-color: #c8c8c8;
            }
            #Convert_to_CP {
                font-weight: bold;
                background-color: #0078d7;
                color: white;
                border: none;
            }
            #Convert_to_CP:hover {
                background-color: #005a9e;
            }
            QTextBrowser#log_text {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                border-radius: 5px;
            }
            QRadioButton, QCheckBox {
                spacing: 8px;
            }
            QLabel#header_label {
                font-size: 16pt;
                font-weight: bold;
                color: #2c3e50;
                padding: 5px;
            }
            QLabel#email_label a {
                color: #0078d7;
                text-decoration: none;
            }
             QLabel#email_label a:hover {
                text-decoration: underline;
            }
        """
        MainWindow.setStyleSheet(stylesheet)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "CompactSAR Synthesizer"))
        self.header_label.setText(_translate("MainWindow", "CompactSAR Synthesizer"))
        self.email_label.setText(_translate("MainWindow", "<a href='mailto:mebrahimi.uni@gmail.com'>mebrahimi.uni@gmail.com</a>"))



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
