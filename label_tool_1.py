import sys
import PyQt5
#from PyQt6.uic import loadUi
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
#from PyQt6.QtMultimedia import QMediaPlayer, QMediaContent
#from PyQt6.QtMultimediaWidgets import *
from PyQt5.QtCore import *
import os
import cv2
import pandas as pd
import numpy as np
       
NaverApp = QApplication(sys.argv)

class LabelsTool(QDialog):
    
    def __init__(self):
        super(LabelsTool, self).__init__()

        self.setFixedSize(1000, 800)
        
        self.dataset = None 
        self.excel_path = None
        self.csv_file = None
        self.resized_mode = False
        self.convert_mode = False
        self.index = -1
        
        self.initDialog()
        self.initKeyBoard()
        
        self.setupButton()
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        
    def choose_excel_folder(self):
        if self.dataset is None:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setText("You should click to \"Select Dir\" button to choose image dir")
            msg.setWindowTitle("Warn")
            msg.exec()
        else:
            self.csv_folder = QFileDialog.getExistingDirectory(self, 'Open Folder', "C:\\")
            self.csv_path = os.path.join(self.csv_folder, "label_image.csv")
            
            if not(os.path.exists(self.csv_path)):
                self.csv_file = pd.DataFrame()
                self.csv_file["Name"] = pd.Series(self.dataset)
                self.csv_file["Rating"] = pd.Series([])
                self.csv_file.to_csv(self.csv_path, index=False)
            else:
                self.csv_file = pd.read_csv(self.csv_path)
                
                self.show_image(self.index, self.resized_mode, self.convert_mode)
        
    def change_view_mode(self):
        if self.index == -1:
            self.show_notification_pop_up("Need image", "Warn")
            return
        
        _translate = QtCore.QCoreApplication.translate
        self.resized_mode = not(self.resized_mode)
        self.view_mode.setText(_translate("Dialog", "Fit Size" if not(self.resized_mode) else "Real Size")) 
        self.show_image(self.index, self.resized_mode, self.convert_mode)
        
    def change_convert_mode(self):
        if self.index == -1:
            self.show_notification_pop_up("Need image", "Warn")
            return
        
        _translate = QtCore.QCoreApplication.translate
        self.convert_mode = not(self.convert_mode)
        self.convert_btn.setText(_translate("Dialog", "No Convert" if not(self.convert_mode) else "Convert")) 
        self.show_image(self.index, self.resized_mode, self.convert_mode)

    def load_image_dir_func(self):
        # Load image
        self.fname = QFileDialog.getExistingDirectory(self, 'Open Folder', "C:\\")
        
        if os.path.exists(self.fname):
            self.dataset = os.listdir(self.fname)
            self.index = 0
            self.show_image(self.index, self.resized_mode, self.convert_mode)
            
            self.total_image_label.setText("/" + str(len(self.dataset)))
        
    def show_image(self, index, resized_mode, convert_mode):
        name = self.dataset[index]
        print(name, self.fname)
        # current_image = cv2.imread(os.path.join(self.fname, name))

        # Resolve unicode path problem
        stream = open(u"{}".format(os.path.join(self.fname, name)), "rb")
        bytes = bytearray(stream.read())
        np_array = np.asarray(bytes, dtype=np.uint8)
        current_image = cv2.imdecode(np_array, cv2.IMREAD_UNCHANGED)
        
        if not(convert_mode):
            current_image = cv2.cvtColor(current_image, cv2.COLOR_BGR2RGB)
        
        image = QtGui.QImage(current_image, current_image.shape[1], current_image.shape[0], current_image.shape[1] * 3, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap(image)
        
        #if (resized_mode):
         #   self.showscreen.setPixmap(pixmap)
        #else:
        width, height = self.showscreen.width(), self.showscreen.height()
        pixmap = pixmap.scaled(width, height, Qt.KeepAspectRatio)
         
        self.showscreen.setPixmap(pixmap)
        
        
        # Hiển thị rating đã label (nếu có)
        rating_label = self.get_image_rating(name)
        
        if rating_label != -1:
            self.result.setText(str(rating_label))
            self.label = rating_label
        else:
            self.result.setText("")
            self.label = -1
            
        # Update the index in image_index
        self.update_index_label(self.index)
        
    def get_image_rating(self, name):
        if self.csv_file is None:
            return -1
        
        record = self.csv_file[self.csv_file.Name == name].to_numpy()
        
        if len(record) == 0:
            return -1 
        else:
            record = record[0]
            
            try:
                int(record[1]) 
            except:
                return -1
            else:
                return int(record[1]) 
        
    def listen_key(self, event):
        key_press = event.key()
        
        if key_press == Qt.Key_1:
            return 1 #xe_so
        elif key_press == Qt.Key_2:
            return 2 #xe_ga
        elif key_press == Qt.Key_3:
            return 3 #xe_dien 
        elif key_press == Qt.Key_4:
            return 4 #phan_khoi_lon
        elif key_press == Qt.Key_5:
            return 5 #ko_phai_xe_may
    def keyPressEvent(self, event):
        label = self.listen_key(event)
        
        if label is not None or label == -1:
            self.label = label 
            self.display_result(self.label)
            
    def display_result(self, rating):
        if rating is not None or rating == -1:
            self.result.setText(str(rating))
    
    # Cần đoạn code này do event ở key press không nhận các dấu mũi tên
    def initKeyBoard(self):
        # Next or previous image
        self.right = QShortcut(QKeySequence("Right"), self)
        self.right.activated.connect(self.go_next_image)
        
        self.left = QShortcut(QKeySequence("Left"), self)
        self.left.activated.connect(self.go_prev_image)
        
    def show_notification_pop_up(self, content, title):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setText(content)
        msg.setWindowTitle(title)
        msg.exec()
    
    def auto_save_label(self, name, rating):
        index = self.csv_file[self.csv_file.Name == name].index
        index = list(index)

        if len(index) <= 0:
            new_record = pd.DataFrame.from_dict({
                "Name": [name],
                "Rating": [rating]
            })

            self.csv_file = pd.concat([self.csv_file, new_record], axis=0)
        else:
        
            index = list(index)[0]
            
            self.csv_file.iat[index, 1] = int(rating)
        
    def save_csv(self):
        
        if self.csv_file is not None and self.csv_path is not None:
            self.csv_file.to_csv(self.csv_path, index=False)
            
            self.show_notification_pop_up("Save successfully", "Sucess")
        
    # Save file when closing app 
    def closeEvent(self, event):
        if self.csv_file is not None and self.csv_path is not None:
            self.csv_file.to_csv(self.csv_path, index=False)
            print("Auto save when closing")
    
    def go_next_image(self):
        print("Next image")
        
        if self.index == -1:
            self.show_notification_pop_up("You must select image dir by clicking to \"Select Dir\" button ", "Warn")
            return
        
        if self.csv_file is None:
            self.show_notification_pop_up("You must select image dir by clicking to \"Select Save Dir\" button ", "Warn")
            return 
        
        if self.label is None or self.label == -1:
            self.show_notification_pop_up("You must label image", "Warn")
            return 
        
        if self.index >= len(self.dataset) - 1:
            self.show_notification_pop_up("You have labeled all images", "Success")
            
            name = self.dataset[self.index]
            self.auto_save_label(name, self.label)
            
            if self.csv_file is not None and self.csv_path is not None:
                self.csv_file.to_csv(self.csv_path, index=False)
            return 
            
        name = self.dataset[self.index]
        self.auto_save_label(name, self.label)
            
        self.index += 1
        self.show_image(self.index, self.resized_mode, self.convert_mode)      
        
    def go_prev_image(self):
        print("Previous image")
        
        if self.index == -1:
            self.show_notification_pop_up("You must select image dir by clicking to \"Select Dir\" button ", "Warn")
            return 
        
        if self.csv_file is None:
            self.show_notification_pop_up("You must select image dir by clicking to \"Select Save Dir\" button ", "Warn")
            return 
        
        if self.label is None or self.label == -1:
            self.show_notification_pop_up("You must label image", "Warn")
            return 
        
        if self.index <= 0:
            self.show_notification_pop_up("There are no previous image", "Warn")
            return 
            
        name = self.dataset[self.index]
        self.auto_save_label(name, self.label)
            
        self.index -= 1
        self.show_image(self.index, self.resized_mode, self.convert_mode)
    
    def update_index_label(self, index):
        self.image_index.setText("{}".format(index + 1))
        
    def go_to_image(self):
        image_index = int(self.image_index.text())
        
        if image_index >= len(self.dataset) or image_index <= 0:
            self.show_notification_pop_up("Invalid index", "Warning")
        else:
            name = self.dataset[self.index]
            self.auto_save_label(name, self.label)
            
            self.index = image_index - 1
            self.show_image(self.index, self.resized_mode, self.convert_mode)
            
        
    def initDialog(self):
        # Icon
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icon.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)

        # Screen Static
        self.screenStatic = QtWidgets.QWidget(self)
        self.screenStatic.setGeometry(QtCore.QRect(-1, -1, 1001, 801))
        self.screenStatic.setStyleSheet("QWidget#screenStatic{background-image: url(\"new2.jpg\");}")
        self.screenStatic.setObjectName("screenStatic")

        # Show image for labeling 
        self.showscreen = QtWidgets.QLabel(self.screenStatic)
        self.showscreen.setGeometry(QtCore.QRect(360, 120, 621, 651))
        self.showscreen.setStyleSheet("border-radius: 20px;\n""border-width: 10px;\n"
                                      "border-color: white;\n""background-color: rgba(255, 255, 255, 70);") # 170, 255, 255
        self.showscreen.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.showscreen.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.showscreen.setText("")
        self.showscreen.setTextFormat(QtCore.Qt.PlainText)
        self.showscreen.setPixmap(QtGui.QPixmap("../../../../../../"))
        self.showscreen.setScaledContents(False)
        self.showscreen.setAlignment(QtCore.Qt.AlignCenter)
        self.showscreen.setObjectName("showscreen")

        # Welcome to LabelsTool label
        self.welcome2 = QtWidgets.QLabel(self.screenStatic)
        self.welcome2.setGeometry(QtCore.QRect(430, 60, 511, 51))
        self.welcome2.setStyleSheet("font: 75 18pt \"MS Shell Dlg 2\";\n""color: rgb(255, 255, 255);")
        self.welcome2.setObjectName("welcome2")

        # Directory selection button
        self.dir_selection_btn = QtWidgets.QPushButton(self.screenStatic)
        self.dir_selection_btn.setGeometry(QtCore.QRect(60, 120, 211, 51))
        self.dir_selection_btn.setStyleSheet("border-radius: 20px;\n""font: 75 16pt \"MS Shell Dlg 2\";\n"
                                      "background-color: rgb(85, 255, 255);\n""color: #000000;")
        self.dir_selection_btn.setObjectName("dir_selection")

        # Save xlsx dir selection
        self.save_dir_btn = QtWidgets.QPushButton(self.screenStatic)
        self.save_dir_btn.setGeometry(QtCore.QRect(60, 190, 211, 51))
        self.save_dir_btn.setStyleSheet("border-radius: 20px;\n""font: 75 16pt \"MS Shell Dlg 2\";\n"
                                      "background-color: rgb(85, 255, 255);\n""color: #000000;")
        self.save_dir_btn.setObjectName("save_dir_btn")
        
        # Manual save button 
        self.manual_save_btn = QtWidgets.QPushButton(self.screenStatic)
        self.manual_save_btn.setGeometry(QtCore.QRect(60, 330, 211, 51))
        self.manual_save_btn.setStyleSheet("border-radius: 20px;\n""font: 75 16pt \"MS Shell Dlg 2\";\n"
                                      "background-color: rgb(85, 255, 255);\n""color: #000000;")
        self.manual_save_btn.setObjectName("manual_save_btn")
        
        # Change view image mode
        self.view_mode = QtWidgets.QPushButton(self.screenStatic)
        self.view_mode.setGeometry(QtCore.QRect(60, 260, 211, 51))
        self.view_mode.setStyleSheet("border-radius: 20px;\n""font: 75 16pt \"MS Shell Dlg 2\";\n"
                                      "background-color: rgb(85, 255, 255);\n""color: #000000;")
        self.view_mode.setObjectName("view")
        
        # Convert btn
        self.convert_btn = QtWidgets.QPushButton(self.screenStatic)
        self.convert_btn.setGeometry(QtCore.QRect(60, 400, 211, 51))
        self.convert_btn.setStyleSheet("border-radius: 20px;\n""font: 75 16pt \"MS Shell Dlg 2\";\n"
                                      "background-color: rgb(85, 255, 255);\n""color: #000000;")
        self.convert_btn.setObjectName("view")
        
        # Image number label
        self.image_number_label = QtWidgets.QLabel(self.screenStatic)
        self.image_number_label.setGeometry(QtCore.QRect(70, 450, 191, 50))
        self.image_number_label.setStyleSheet("font: 75 18pt \"MS Shell Dlg 2\";\n""color: rgb(255, 255, 255);")
        self.image_number_label.setObjectName("welcome2")
        
        # Show the image number 
        self.image_index = QtWidgets.QLineEdit(self.screenStatic)
        self.image_index.setGeometry(QtCore.QRect(540, 60, 150, 50))
        self.image_index.setStyleSheet("border-radius: 20px;\n"
                                  "border-width:8px;\n"
                                  "border-color: black;\n"
                                  "background-color: rgb(255, 255, 255);\n"
                                  "font: 75 14pt 'MS Shell Dlg 2';\n"
                                  "color: rgb(0, 0, 0);")
        self.image_index.setText("")
        self.image_index.setAlignment(QtCore.Qt.AlignCenter)
        self.image_index.setObjectName("image_index")
        
        # Show the total number image 
        self.total_image_label = QtWidgets.QLabel(self.screenStatic)
        self.total_image_label.setGeometry(QtCore.QRect(700, 60, 200, 50)) 
        self.total_image_label.setStyleSheet("font: 75 18pt \"MS Shell Dlg 2\";\n""color: rgb(0, 0, 0);")
        self.total_image_label.setObjectName("welcome2")
        
        # Go to button 
        self.change_image_btn = QtWidgets.QPushButton(self.screenStatic)
        self.change_image_btn.setGeometry(QtCore.QRect(910, 60, 50, 50))
        self.change_image_btn.setStyleSheet("border-radius: 20px;\n""font: 75 16pt \"MS Shell Dlg 2\";\n"
                                      "background-color: rgb(255, 255, 255);\n""color: #000000;")
        self.change_image_btn.setObjectName("save_dir_btn")
        
        # Result 
        self.result_label = QtWidgets.QLabel(self.screenStatic)
        self.result_label.setGeometry(QtCore.QRect(70, 550, 191, 50))
        self.result_label.setStyleSheet("font: 75 18pt \"MS Shell Dlg 2\";\n""color: rgb(255, 255, 255);")
        self.result_label.setObjectName("welcome2")
        
        # Show click
        self.result = QtWidgets.QLabel(self.screenStatic)
        self.result.setGeometry(QtCore.QRect(70, 600, 191, 161))
        self.result.setStyleSheet("border-radius: 20px;\n"
                                  "border-width:5px;\n"
                                  "border-color: white;\n"
                                  "background-color: rgb(170, 255, 255);\n"
                                  "font: 75 18pt 'MS Shell Dlg 2';\n"
                                  "color: rgb(0, 0, 0);")
        self.result.setText("")
        self.result.setTextFormat(QtCore.Qt.PlainText)
        self.result.setAlignment(QtCore.Qt.AlignCenter)
        self.result.setObjectName("result")
        
    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "LabelNow"))
        # Welcome to LabelsTool image
        self.welcome2.setText(_translate("Dialog", "Image:"))
        # Chọn đường dẫn đến folder chứa ảnh cần gán nhãn
        self.dir_selection_btn.setText(_translate("Dialog", "Select Dir"))
        # Chọn đường dẫn chứa file csv gán nhãn
        self.save_dir_btn.setText(_translate("Dialog", "Select Save Dir"))
        # Thay đổi cách view hình ảnh
        self.view_mode.setText(_translate("Dialog", "Fit Size" if not(self.resized_mode) else "Real Size"))
        # Label result 
        self.result_label.setText(_translate("Dialog", "Result:"))
        # Manual save 
        self.manual_save_btn.setText(_translate("Dialog", "Save All Label"))
        # Go direct to image 
        self.change_image_btn.setText(_translate("Dialog", "Go"))
        # Convert btn
        self.convert_btn.setText(_translate("Dialog", "No Convert" if not(self.convert_mode) else "Convert"))
        
    def setupButton(self):
        self.dir_selection_btn.clicked.connect(self.load_image_dir_func)
        self.save_dir_btn.clicked.connect(self.choose_excel_folder)
        self.view_mode.clicked.connect(self.change_view_mode)
        self.manual_save_btn.clicked.connect(self.save_csv)
        self.change_image_btn.clicked.connect(self.go_to_image)
        self.convert_btn.clicked.connect(self.change_convert_mode)
    

staticWin = LabelsTool()
list_win = staticWin
list_win.show()
sys.exit(NaverApp.exec_())
     
        
        
