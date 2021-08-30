import sys, os, ctypes, psutil, traceback
from datetime import datetime

from PyQt5.QtCore import QCoreApplication, QThread, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import QAction, QApplication, QDialog, QFileDialog, \
                            QMainWindow, QMenu, QSystemTrayIcon, QErrorMessage

from HiDT_module import infer

main_form = loadUiType("./GUI/MainGui.ui")[0] # Main Window GUI
save_form = loadUiType("./GUI/SaveGui.ui")[0] # Save Path Select Dialog GUI

# Main Window
class MainWindow(QMainWindow, main_form):
    def __init__(self):
        super().__init__()
        
        # Set Main GUI
        self.setupUi(self)
        self.setWindowTitle("Look Out Your Windows")
        self.setWindowIcon(QIcon("icon.ico"))

        # Load the image and save path from file
        try:
            f = open("./LookOutYourWindows_SavePath.txt", "r")
            self.image_path = (f.readline()).rstrip('\n')
            self.image_name = (f.readline()).rstrip('\n')
            self.save_path = (f.readline()).rstrip('\n')
            f.close()

            self.lineedit_filepath.setText(self.image_path)
            self.loadImageFromFile(self.image_path)
        except:
            pass
        
        self.btn_browse.clicked.connect(self.browse_files)
        self.btn_start.clicked.connect(self.start)
        self.btn_stop.clicked.connect(self.stop)
        self.btn_exit.clicked.connect(QCoreApplication.instance().quit)
        self.timer = QTimer(self, interval=90000, timeout=self.set_wallpaper)

    # Open file explorer to browse image and set file path
    def browse_files(self):
        self.image_path = QFileDialog.getOpenFileName(self, "Open File", './', "Images (*.png *.jpg)")[0]
        if not self.image_path:
            return
    
        self.lineedit_filepath.setText(self.image_path)
        self.loadImageFromFile(self.image_path)
        
        base = os.path.basename(self.image_path)
        self.image_name = os.path.splitext(base)[0] # Save the image name

    # Load select image and show it
    def loadImageFromFile(self, filepath):
        self.qPixmapFile = QPixmap()
        self.qPixmapFile.load(filepath) # Raise "qt.gui.icc: fromIccProfile: failed minimal tag size sanity" but no problem occurs
        self.inference_size = min(self.qPixmapFile.height(), self.qPixmapFile.width()) // 4 # To retain the original size of the image
        self.qPixmapFile = self.qPixmapFile.scaledToHeight(261)
        self.qPixmapFile = self.qPixmapFile.scaledToWidth(441)
        self.lbl_image.setPixmap(self.qPixmapFile)
        self.lbl_status.setText("Status: Waiting")

    # Start generating images and setting wallpaper
    def start(self):
        # Get save folder path
        if hasattr(self, "save_path"):
            # Use the loaded path
            save_dialog = SaveDialog(self.image_path, self.image_name, self.save_path)
        else:
            save_dialog = SaveDialog(self.image_path, self.image_name)
        save_dialog.exec_()
        
        # Return if save path is not selected
        if hasattr(save_dialog, "save_path") and save_dialog.save_path:
            self.save_path = save_dialog.save_path
        else:
            return

        # Check if there exist generated images before 
        total_files = os.listdir(self.save_path)
        image_names = [self.image_name + "_to_morning.jpg", self.image_name + "_to_afternoon.jpg",
                        self.image_name + "_to_evening.jpg", self.image_name + "_to_night.jpg"]

        for file_name in total_files: 
            for index in range(len(image_names) - 1, -1, -1):
                if file_name == image_names[index]:
                    image_names.pop(index)

        # set UI for working
        self.btn_start.hide()
        self.btn_stop.show()
        self.btn_browse.setEnabled(False)

        # All images don't exist, so create new images
        if image_names:
            self.lbl_status.setText("Status: Creating Images")
            self.infer_thread = InferThread(self)
            self.infer_thread.start()
            self.infer_thread.infer_failed.connect(self.fail)
            self.infer_thread.infer_finished.connect(self.work)
        else:
            self.work()

    # Handling if creating images fail
    @pyqtSlot(str)
    def fail(self, error):
        self.lbl_status.setText("Status: Failed to create")
        self.btn_start.show()
        self.btn_stop.hide()
        self.btn_browse.setEnabled(True)

        # Pop-up a new dialog to show an error message
        error_dialog = QErrorMessage()
        error_dialog.setWindowTitle("Error Message")
        error_dialog.setWindowIcon(QIcon("icon.ico"))
        error_dialog.showMessage(error)
        error_dialog.exec()


    # Start setting wallpaper
    def work(self):
        self.lbl_status.setText("Status: Working")
        self.set_wallpaper()
        self.timer.start()
     
    # Stop setting wallpaper
    def stop(self):
        # Terminate thread if images are generating.
        try:
            self.infer_thread.terminate()
        except:
            pass
        
        self.lbl_status.setText("Status: Waiting")
        self.btn_start.show()
        self.btn_stop.hide()
        self.btn_browse.setEnabled(True)
        self.timer.stop()

    # Set desktop wallpaper according to time
    def set_wallpaper(self):
        now = datetime.now()
        SPI_SETDESKWALLPAPER = 20
        if 7 <= now.hour < 13:
            ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, self.save_path + "/" + self.image_name + "_to_morning.jpg", 0)
        elif 13 <= now.hour < 18:
            ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, self.save_path + "/" + self.image_name + "_to_afternoon.jpg", 0)
        elif 18 <= now.hour < 21:
            ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, self.save_path + "/" + self.image_name + "_to_evening.jpg", 0)
        else:
            ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, self.save_path + "/" + self.image_name + "_to_night.jpg", 0)
            

# Dialog for save path
class SaveDialog(QDialog, save_form):
    def __init__(self, image_path, image_name, save_path=None):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Look Out Your Windows')
        
        self.image_path = image_path
        self.image_name = image_name
        # Set loaded path
        if save_path: 
            self.lineedit_savepath.setText(save_path)
            self.chkbox_save.toggle() # Set check box on

        self.btn_browse.clicked.connect(self.browse_files)
        self.btn_ok.clicked.connect(self.ok)
        self.btn_cancel.clicked.connect(self.cancel)

    # Browse save folder
    def browse_files(self):
        save_path = QFileDialog.getExistingDirectory(self, 'Open a Folder', './')   # Must be not self.save path
        self.lineedit_savepath.setText(save_path)                                   # to press 'cancel' returns None

    # Click OK btn
    def ok(self):
        self.save_path = self.lineedit_savepath.text()

        # Save the save path as text file
        if self.chkbox_save.isChecked():
            if self.save_path:
                f = open("./LookOutYourWindows_SavePath.txt", "w")
                f.write(self.image_path + "\n")
                f.write(self.image_name + "\n")
                f.write(self.save_path)
                f.close()
        else:
            if os.path.exists("./LookOutYourWindows_SavePath.txt"):
                os.remove("./LookOutYourWindows_SavePath.txt")

        self.close()

    # Click cancel btn
    def cancel(self):
        self.close()

# Thread to infer images
class InferThread(QThread):
    infer_finished = pyqtSignal()
    infer_failed = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)
        
        self.image_path = parent.image_path
        self.save_path = parent.save_path
        
        # Set inference size 
        self.inference_size = parent.inference_size
    
    # Run thread
    def run(self):
        # Reduce the process priority to avoid stuck
        p = psutil.Process(os.getpid())
        p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        
        try:
            infer(data_dir=self.image_path, style_dir="./images/styles/", \
                    cfg_path="./configs/daytime.yaml", \
                    weight_path="./trained_models/generator/daytime.pt", \
                    enh_weights_path="./trained_models/enhancer/enhancer.pth", \
                    inference_size= self.inference_size, \
                    output_dir=self.save_path)
            self.infer_finished.emit()

        except Exception as e:
            self.infer_failed.emit(repr(traceback.format_exc()))

class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # Set Tray Icon
        self.setIcon(QIcon("icon.ico"))
        self.setVisible(True)
        self.activated.connect(self.onTrayIconActivated)
    
    # Show main window when user double-clicks the tray icon
    def onTrayIconActivated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.parent.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()

    # Set Tray System
    app.setQuitOnLastWindowClosed(False)
    tray_icon = SystemTrayIcon(main_window)

    # Creating the options
    menu = QMenu()

    # To open the window
    _open = QAction("Open")
    _open.triggered.connect(main_window.show)
    menu.addAction(_open)

    # To quit the app
    _quit = QAction("Quit")
    _quit.triggered.connect(QCoreApplication.instance().quit)
    menu.addAction(_quit)
    
    # Adding options to system tray
    tray_icon.setContextMenu(menu)

    sys.exit(app.exec())