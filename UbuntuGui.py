import sys, os, ctypes, psutil
from datetime import datetime

from PyQt5.QtWidgets import QAction, QApplication, QDialog, QFileDialog, QMainWindow, QMenu, QSystemTrayIcon
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import QCoreApplication, QThread, QTimer, pyqtSignal

from HiDT_module import infer

main_form = uic.loadUiType("./GUI/MainGui.ui")[0] # Main Window GUI
save_form = uic.loadUiType("./GUI/SaveGui.ui")[0] # Save Path Select Dialog GUI

# Main Window
class MainWindow(QMainWindow, main_form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Look Out Your Windows")
        self.setWindowIcon(QIcon("icon.ico"))
        
        # Load the image and save path from file
        try:
            f = open(os.path.expanduser("~") + "/" + "LookOutYourWindows_SavePath.txt", "r")
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
        self.image_path = QFileDialog.getOpenFileName(self, "Open File", './', "Images (*.png, *.jpg)")[0]
        if not self.image_path:
            return
    
        self.lineedit_filepath.setText(self.image_path)
        self.loadImageFromFile(self.image_path)
        
        base = os.path.basename(self.image_path)
        self.image_name = os.path.splitext(base)[0] # Save the image name

    # Load select image and show it
    def loadImageFromFile(self, filepath):
        self.qPixmapFile = QPixmap()
        self.qPixmapFile.load(filepath)
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
    def fail(self):
        self.lbl_status.setText("Status: Failed to create")
        self.btn_start.show()
        self.btn_stop.hide()
        self.btn_browse.setEnabled(True)

    # Start setting wallpaper
    def work(self):
        self.lbl_status.setText("Status: Working")
        self.set_wallpaper()
        self.timer.start()
     
    # Stop setting wallpaper
    def stop(self):
        # Terminate thread if images are generating.
        try:
            self.infer_thread.stop()
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
        if 7 <= now.hour < 13:
            os.system("/usr/bin/gsettings set org.gnome.desktop.background picture-uri " + self.save_path + "/" + self.image_name + "_to_morning.jpg")
        elif 13 <= now.hour < 18:
            os.system("/usr/bin/gsettings set org.gnome.desktop.background picture-uri " + self.save_path + "/" + self.image_name + "_to_afternoon.jpg")
        elif 18 <= now.hour < 21:
            os.system("/usr/bin/gsettings set org.gnome.desktop.background picture-uri " + self.save_path + "/" + self.image_name + "_to_evening.jpg")
        else:
            os.system("/usr/bin/gsettings set org.gnome.desktop.background picture-uri " + self.save_path + "/" + self.image_name + "_to_night.jpg")

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
                f = open(os.path.expanduser("~") + "/" + "LookOutYourWindows_SavePath.txt", "w")
                f.write(self.image_path + "\n")
                f.write(self.image_name + "\n")
                f.write(self.save_path)
                f.close()
        else:
            if os.path.exists(os.path.expanduser("~") + "/" + "LookOutYourWindows_SavePath.txt"):
                os.remove(os.path.expanduser("~") + "/" + "LookOutYourWindows_SavePath.txt")

        self.close()

    # Click cancel btn
    def cancel(self):
        self.close()

# Thread to infer images
class InferThread(QThread):
    infer_finished = pyqtSignal()
    infer_failed = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        
        # Reduce CPU priority to avoid stuck
        p = psutil.Process(os.getpid())
        p.nice(5)

        self.image_path = parent.image_path
        self.save_path = parent.save_path
    
    # Run thread
    def run(self):
        try:
            os.environ["OMP_NUM_THREADS"] = "1"
            infer(data_dir=self.image_path, style_dir="./images/styles/", \
                    cfg_path="./configs/daytime.yaml", \
                    weight_path="./trained_models/generator/daytime.pt", \
                    enh_weights_path="./trained_models/enhancer/enhancer.pth", \
                    output_dir=self.save_path)
            self.infer_finished.emit()
        except Exception as e:
            print(e)
            self.infer_failed.emit()

    # Stop thread
    def stop(self):
        self.terminate()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()

    # Set Tray System
    app.setQuitOnLastWindowClosed(False)

    # Adding an icon
    icon = QIcon("icon.ico")
    
    # Adding item on the menu bar
    tray = QSystemTrayIcon()
    tray.setIcon(icon)
    tray.setVisible(True)
    
    # Creating the options
    menu = QMenu()
    
    # To open the window
    _open = QAction("Open")
    _open.triggered.connect(main_window.show)
    menu.addAction(_open)

    # To quit the app
    _quit = QAction("Quit")
    _quit.triggered.connect(app.quit)
    menu.addAction(_quit)
    
    # Adding options to system tray
    tray.setContextMenu(menu)

    sys.exit(app.exec())
    