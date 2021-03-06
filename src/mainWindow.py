# -*- coding: utf-8 -*-
#-*-python-2.7-

try:
    from PySide import QtCore, QtGui
except Exception, e:
    from PyQt4 import QtCore, QtGui

from login import Login
import config as config
import pjsua
from speakerManagement import SpeakerManagement
from passwordChange import passwordChange
from configDialog import configDialog
from phone import Phone

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.speakerBtns = list()
        self.selectedSpeaker = list()
        try:
            config.init()
        except Exception, e:
            QtGui.QMessageBox.critical(self,"Configuration Error"," \nRun \"aria-client --setup\"")
            self.close()
            exit()
            pass
        login = Login(self)
        QtCore.QObject.connect(login, QtCore.SIGNAL("accepted()"),self.loginSucess)
        QtCore.QObject.connect(login, QtCore.SIGNAL("reject()"),self.loginFailed)

    def loginSucess(self):
        self.setupUi()
        self.setEnabled(False)
        self.show()
        self.phone_setup()
               

    def loginFailed(self):
        print "Bye...."
        self.close()       

    def setupUi(self):
        self.setWindowTitle("ARIA")
        self.resize(678, 341)
        self.centralwidget = QtGui.QWidget(self)
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)

        self.mainVerticalLayout = QtGui.QVBoxLayout()

        self.label = QtGui.QLabel("Select speaker : \n",self.centralwidget)
        self.mainVerticalLayout.addWidget(self.label)
        
        self.horizontalLayout = QtGui.QHBoxLayout()

        self.scrollArea = QtGui.QScrollArea(self.centralwidget)
        self.scrollArea.setWidgetResizable(False)
        
        try: #PySide
            self.scrollArea.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        except Exception, e: #PyQt
            self.scrollArea.setAlignment(QtCore.Qt.AlignCenter)
        
        self.scrollArea.setLayout(QtGui.QGridLayout())
        
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.adjustSize()

        #self.speakerBtnLayout = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.speakerBtnLayout = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        #set spaker buttons
        try:
            self.setSpeakerBtns(self.speakerBtnLayout)
        except Exception, e:
            QtGui.QMessageBox.critical(self,"Configuration Error"," \n Run ariasetup")
            self.close()
            exit()

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.horizontalLayout.addWidget(self.scrollArea)

        self.btnLayout = QtGui.QVBoxLayout()
        self.okBtn = QtGui.QPushButton("Ok")

        self.okBtn.clicked.connect(self.okAct)
        
        self.okBtn.setEnabled(False)
        self.btnLayout.addWidget(self.okBtn)
        self.cancelBtn = QtGui.QPushButton("Cancel")
        self.cancelBtn.setEnabled(False)
        self.cancelBtn.clicked.connect(self.cancelAct)
        self.btnLayout.addWidget(self.cancelBtn)
        self.horizontalLayout.addLayout(self.btnLayout)

        self.mainVerticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.mainVerticalLayout, 0, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)

        self.menubar = QtGui.QMenuBar()
        #self.menubar.setGeometry(QtCore.QRect(0, 0, 678, 30))
        self.menuFile = QtGui.QMenu("File",self.menubar)
        self.menuSettings = QtGui.QMenu("Settings",self.menubar)
        self.menuHelp = QtGui.QMenu("Help",self.menubar)
        self.setMenuBar(self.menubar)
        self.actionQuit = QtGui.QAction("E&xit", self, shortcut="Ctrl+Q",triggered=self.close)
        self.actionAbout = QtGui.QAction("&About", self, triggered=self.about)

        self.actionSpeaker = QtGui.QAction("Speaker Management", self, triggered=self.speakerSettings)
        self.actionPass = QtGui.QAction("Change Password", self, triggered=self.passSettings)
        self.actionReg = QtGui.QAction("Registation Settings", self, triggered=self.regSettings)

        self.menuFile.addAction(self.actionQuit)
        self.menuHelp.addAction(self.actionAbout)

        self.menuSettings.addAction(self.actionReg)
        self.menuSettings.addAction(self.actionPass)
        self.menuSettings.addAction(self.actionSpeaker)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())


        self.statusbar = QtGui.QStatusBar(self)
        self.setStatusBar(self.statusbar)

        QtCore.QMetaObject.connectSlotsByName(self)

    def setSpeakerBtns(self,layout):
        #size = QtCore.QSize(30,20)
        i = 0
        for speaker in config.getSpeakers():
            pushButton = Speaker(speaker['Name'],speaker['Number'],self.layout)
            #QtGui.QPushButton("\nName"+str(i)+"\n",self.scrollAreaWidgetContents)
            pushButton.setAutoFillBackground(False)
            pushButton.setCheckable(True)
            #pushButton.setAutoExclusive(True)
            #pushButton.resize(size)
            pushButton.clicked.connect(self.speakerSelect)
            layout.addWidget(pushButton, i / 3, i % 3)
            i = i + 1
            self.speakerBtns.append(pushButton)

    def speakerSelect(self,clear=True):
        btn = self.sender()
        #if len(self.selectedSpeaker) != 0:
        #    self.selectedSpeaker.setChecked(False)
        if btn.isChecked():
            self.selectedSpeaker.append(btn)
            self.okBtn.setEnabled(True)
            self.cancelBtn.setEnabled(True)
            
            try: #PySide
                self.statusbar.message("Selected Speaker :"
                +str(btn) ,0)
            except Exception:
                self.statusbar.showMessage("Selected Speaker :"
                    +str(btn) ,0)
        else:
            self.selectedSpeaker.remove(btn)
            if len(self.selectedSpeaker) == 0:
                self.okBtn.setEnabled(False)
                self.cancelBtn.setEnabled(False)
                self.statusbar.clear()

    def cancelAct(self):
        if self.cancelBtn.text() == "Cancel":
            self.clearSelection()
            self.okBtn.setEnabled(False)
            self.cancelBtn.setEnabled(False)
            self.statusbar.clear()
        if self.cancelBtn.text() == "End":
            self.endcalls()
            #self.okBtn.setEnabled(True)
            #self.cancelBtn.setText("Cancel")
            #self.scrollArea.setEnabled(True)

    def clearSelection(self):
        self.selectedSpeaker =list()
        for btn in self.speakerBtns:
            btn.setChecked(False)

    def okAct(self):
        self.scrollArea.setEnabled(False)
        self.okBtn.setEnabled(False)
        self.cancelBtn.setText("End")
        for speaker in self.selectedSpeaker:
            number = speaker.getNumber()
            #print number
            #TODO Call
            current_call = self.ph.call(number)
            self.calllist.append(current_call)

    def about(self):
        from about import About
        About(self)

    def callended(self,t):
        if t==0:
            try:
                current_call=self.calllist.pop()
                print(current_call.is_valid())
                current_call = None
            except IndexError:
                pass
        if len(self.calllist) == 0:
            self.okBtn.setEnabled(True)
            self.cancelBtn.setText("Cancel")
            self.scrollArea.setEnabled(True)
    
    def endcalls(self):
        while True:
            try:
                current_call=self.calllist.pop()
                print(current_call.is_valid())
                current_call.hangup()
                #self.statusbar.showMessage(str(current_call.info().state_text),1000)
            except pjsua.Error, e:
                print ("e"+str(e))
            except IndexError :
                break
        self.okBtn.setEnabled(True)
        self.cancelBtn.setText("Cancel")
        self.scrollArea.setEnabled(True)
        #self.selectedSpeaker.click()
        #self.statusbar.message("Disconnected",0)

    def phone_setup(self):
        self.ph = Phone(int(config.bindport))
        
        QtCore.QObject.connect(self.ph, QtCore.SIGNAL('phoneMessage(const QString& )'), self.setmsg)
        QtCore.QObject.connect(self.ph, QtCore.SIGNAL('statechanged(int )'), self.callended)
        QtCore.QObject.connect(self.ph, QtCore.SIGNAL('regStatus(int )') ,self.registationStatus)
        self.ph.register(domain=config.domain,
            username=config.username, password=config.password)

    def registationStatus(self,status):
        if status == 200:
            self.calllist = list()
            self.setEnabled(True)
        else:
            QtGui.QMessageBox.critical(self,"","Registation Failed")
            self.close()
        

    def setmsg(self,message,time = 5000):
        self.statusbar.clear()
        try:
            self.statusbar.message(message,time)
        except Exception, e:
            self.statusbar.showMessage(message,time)

    def passSettings(self):
        passwordDialog = passwordChange(self)
        QtCore.QObject.connect(passwordDialog, QtCore.SIGNAL("accepted()"),self.settingsSaved) 


    def speakerSettings(self):
        speakerDialog = SpeakerManagement(self)
        QtCore.QObject.connect(speakerDialog, QtCore.SIGNAL("accepted()"),self.settingsSaved) 

    def regSettings(self):
        configUi = configDialog(self)
        QtCore.QObject.connect(configUi, QtCore.SIGNAL("accepted()"), self.settingsSaved)
    
    def settingsSaved(self):
        QtGui.QMessageBox.information(self, "ARIA ","Registation Settings Saved \nRestart For Apply Changes")


    def __del__(self):
        self.ph.deregister()

class Speaker(QtGui.QPushButton):
    """ Speaker"""
    def __init__(self, name,number,parent=None):
        super(Speaker,self).__init__()
        self.setText("\n"+name+"\n")
        self.__name__ = name
        self.__number__ = number
    
    def __str__(self):
        return (str(self.__name__) + 
            " ["+str(self.__number__)+"]")

    def getNumber(self):
        return self.__number__

    def getName(self):
        return self.__name__