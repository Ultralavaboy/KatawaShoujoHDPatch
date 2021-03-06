import os
import urllib
import subprocess
import platform
import sys
import logging as lg
from distutils.dir_util import copy_tree
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


inst_dir = "C:\Program Files (x86)\Katawa Shoujo"
patch_dir = "KatawaShoujoHD"
languages_dir = "Languages"
out_dir = "KSHD"


class Patch(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Background image
        self.bg = QLabel(self)
        self.bg.setPixmap(QPixmap('buildres\Bg.jpg'))

        # Textbox with info
        self.txtbox = QLabel(self)
        self.txtbox.move(110, 15)
        self.txtbox.setFont(QFont('Playtime With Hot Toddies', 11))
        self.txtbox.setText("Hello.\n"
                            "This setup will install the HD Patch \non your Katawa Shoujo.\n"
                            "The installer is going to use your game's\n"
                            "copied files, so the original game will not be\n"
                            "harmed. You can come back to the original\ngame whenever you want. Enjoy!")
        self.txtbox.adjustSize()

        # Rin image
        self.pic = QLabel(self)
        self.pic.setPixmap(QPixmap('buildres\Rin.png'))
        self.pic.setGeometry(25, 25, 79, 121)
        self.pic.setScaledContents(True)

        # Progress Bar
        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(30, 140, 360, 18)
        self.pbar.move(41, 235)

        # Status label under progress bar
        self.statuslbl = QLabel(self)
        self.statuslbl.setFont(QFont('Playtime With Hot Toddies', 9))
        self.statuslbl.move(42, 255)

        # Line above path QLineEdit
        self.pathlbl = QLabel(self)
        self.pathlbl.setFont(QFont('Playtime With Hot Toddies', 10))
        self.pathlbl.setText('Choose the folder with your Katawa Shoujo:')
        self.pathlbl.adjustSize()
        self.pathlbl.move(42, 156)

        # "It may take a few minutes" label
        self.lbl2 = QLabel(self)
        self.lbl2.setFont(QFont('Playtime With Hot Toddies', 10))
        self.lbl2.move(140, 199)

        # Path QLineEdit
        self.pth = QLineEdit(self)
        self.pth.setReadOnly(True)
        self.pth.setText(inst_dir)
        self.pth.setGeometry(41, 174, 240, 21)

        # checkbox RUS
        self.cb_rus = QCheckBox('Install Russian', self)
        self.cb_rus.toggle()
        self.cb_rus.move(140, 206)

        # checkbox GER
        self.cb_ger = QCheckBox('Install German', self)
        self.cb_ger.toggle()
        self.cb_ger.move(240, 206)

        # "Browse" button
        self.cbtn = QPushButton('Browse', self)
        self.cbtn.move(290, 173)
        self.cbtn.clicked.connect(self.select_folder)

        # "Install" button
        self.btn = QPushButton('Install', self)
        self.btn.setGeometry(40, 200, 90, 30)
        self.btn.clicked.connect(self.bongiorno)
        self.btn.setEnabled(False)
        self.check_exe()

        # Other window settings
        self.move(700, 400)
        self.setFixedSize(410, 300)
        self.setWindowIcon(QIcon('buildres\icon.ico'))
        self.setWindowTitle("Katawa Shoujo HD Patch")
        self.show()


    # Selecting folder function
    def select_folder(self):
        global inst_dir
        inst_dir = QFileDialog.getExistingDirectory(self, 'Select Katawa Shoujo folder')
        print(inst_dir)
        self.pth.setText(inst_dir)
        self.check_exe()


    # Check for existence of "Katawa Shoujo.exe" in current directory
    def check_exe(self):
        global inst_dir
        if not os.path.isfile(os.path.join(inst_dir,"Katawa Shoujo.exe")):
            self.btn.setEnabled(False)
            QMessageBox.about(self, 'Warning', 'Could not find "Katawa Shoujo.exe".'
                                               '\nMake sure you have chosen the correct folder.')
        else:
            self.btn.setEnabled(True)


    # Main patching method
    def bongiorno(self):
        global inst_dir
        path = inst_dir
        try:
            # "It may take a few minutes" label appear
            self.lbl2.setText('Do not close the installer until the installation \nis complete. It may take a few minutes.')
            self.lbl2.adjustSize()
            self.cb_rus.hide()
            self.cb_ger.hide()
            self.btn.setEnabled(False)

            self.statuslbl.setText("Found the base game files...")
            lg.debug("Found the base game files")
            self.statuslbl.adjustSize()
            self.pbar.setValue(10)

            # Copy the base game files to the output directory
            self.statuslbl.setText("Copying the base game files...")
            self.statuslbl.adjustSize()
            self.pbar.setValue(42)
            copy_tree(path, out_dir)
            lg.debug("Copied the base game files")

            # Hand the call to rpatool to wine if not on windows
            self.statuslbl.setText("Extracting RPA...")
            self.statuslbl.adjustSize()
            self.pbar.setValue(69)

            user_os = platform.system()
            lg.debug("User's platform is %s" % user_os)
            rpa_path = os.path.join(path, 'game/data.rpa')
            extract_path = os.path.join(out_dir, 'game')
            lg.debug("Extracting RPA from %s to %s" % (rpa_path, extract_path))

            if user_os == "Windows":
                subprocess.call(['rpatool.exe', '-x', rpa_path, '-o', extract_path])
            else:
                subprocess.call(['wine', 'rpatool.exe', '-x', rpa_path, '-o', extract_path])
            lg.debug("RPA extracted")

            # Remove the rpa
            self.statuslbl.setText("Removing redundant files...")
            self.statuslbl.adjustSize()
            self.pbar.setValue(87)
            os.remove(os.path.join(out_dir, "game/data.rpa"))
            lg.debug("Redundant files were removed")

            # Patching
            self.statuslbl.setText("Patching the game files...")
            self.statuslbl.adjustSize()
            copy_tree(patch_dir, out_dir)
            lg.debug("Patched")

            # Installing Russian
            if self.cb_rus.isChecked():
                self.statuslbl.setText("Installing Russian language...")
                self.statuslbl.adjustSize()
                self.pbar.setValue(92)
                copy_tree(os.path.join(languages_dir, "Russian"), out_dir)
                lg.debug("Russian language was installed")

            # Installing German
            if self.cb_ger.isChecked():
                self.statuslbl.setText("Installing German language...")
                self.statuslbl.adjustSize()
                self.pbar.setValue(96)
                copy_tree(os.path.join(languages_dir, "German"), out_dir)
                lg.debug("German language was installed")

            # Done
            self.statuslbl.setText("Done! The game is now playable in the folder '%s' in this directory"
                                    "\nby running 'Katawa Shoujo.exe'" % out_dir)
            lg.debug("Installation complete")
            self.statuslbl.adjustSize()
            self.pbar.setValue(100)
            self.lbl2.setText("")
            self.lbl2.adjustSize()
            self.cb_rus.show()
            self.cb_ger.show()
            self.btn.setEnabled(True)
        except:
            lg.exception('An error occured!')
            raise


if __name__ == '__main__':
    App = QApplication(sys.argv)
    QFontDatabase.addApplicationFont('buildres/playtime.ttf')
    App.setStyleSheet('QLabel{font-family: Playtime With Hot Toddies; line-height: 100%}')
    lg.basicConfig(filename='logKSHD.txt', level=lg.DEBUG, format='%(asctime)s %(message)s')
    window = Patch()
    lg.debug('The installer started successfully.')
    sys.exit(App.exec())
