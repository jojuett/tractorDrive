from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ui_settings import Ui_Settings
import Image
import ImageQt
import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import ConfigParser
import os,shutil
from math import pi
from string import split
from subprocess import call
from os.path import dirname,realpath

class Simulation(QThread):
    def run(self):
        proj_home = dirname(realpath(__file__))
        proj_home = proj_home[0:proj_home.rfind('/')]
        conf = ConfigParser.ConfigParser
        conf.read(proj_home + '/global.cfg')
        call([conf.get('system','blenderplayer'),proj_home + '/chars/sim.blend'])

class SettingsWidget(QWidget,Ui_Settings):
        
    def __init__(self,parent = None):
        QWidget.__init__(self,parent)
        self.setupUi(self)
        self.statusBar = None
        
        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        proj_home = dirname(realpath(__file__))
        proj_home = proj_home[0:proj_home.rfind('/')]
        img = Image.open(proj_home + "/frontend/img/tractor.png")
        self.img = img
        self.scene.clear()
        self.imgQ = ImageQt.ImageQt(img)
        pixMap = QPixmap.fromImage(self.imgQ)
        self.pitem = self.scene.addPixmap(pixMap)
        self.scene.update()
        
        self.fig = Figure((5.0,4.0))
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)
        self.axes = self.fig.add_subplot(111)
        self.cruiseControlBox.layout().addWidget(self.canvas)
        
        self.updatePlot()
        self.readSettings(proj_home + '/global.cfg')
        self.setConnections()
        
    def setConnections(self):
        self.dial.valueChanged.connect(self.updateImage)
        self.saveButton.clicked.connect(self.saveSettings)
        self.resetButton.clicked.connect(self.factoryReset)
        self.simulateButton.clicked.connect(self.runSim)
        
    def factoryReset(self):
        proj_home = dirname(realpath(__file__))
        proj_home = proj_home[0:proj_home.rfind('/')]
        self.readSettings(proj_home + '/global.factory.cfg')
        
    def updatePlot(self):
        self.axes.clear()
        xs = []
        ys = []
        proj_home = dirname(realpath(__file__))
        proj_home = proj_home[0:proj_home.rfind('/')]
        fp = open(proj_home + '/sim.data','r')
        for line in fp:
            x,y = split(line,' ')
            xs.append(x)
            ys.append(y)
        self.axes.plot(xs,ys)
        self.canvas.draw()
        
    def runSim(self):
        proj_home = dirname(realpath(__file__))
        proj_home = proj_home[0:proj_home.rfind('/')]
        shutil.copy(proj_home + '/global.cfg',proj_home + '/global.cfg.bak')
        self.statusBar.showMessage('Running Simulation...')
        self.saveSettings()
        sim = Simulation()
        sim.finished.connect(self.simFinished)
        sim.start()
        self.sim = sim
        
    def simFinished(self):
        self.statusBar.showMessage("Ready")
        proj_home = dirname(realpath(__file__))
        proj_home = proj_home[0:proj_home.rfind('/')]
        os.rename(proj_home + '/global.cfg.bak',proj_home + '/global.cfg')
        self.updatePlot()
        
    def updateImage(self):
        angle = self.dial.value() * (180/100.0)
        c = self.pitem.boundingRect().center()
        t = QTransform()
        t.translate(c.x(),c.y())
        t.rotate(angle,Qt.ZAxis)
        t.translate(-c.x(),-c.y())
        self.pitem.setTransform(t)
        
        w,h = self.img.size
        self.graphicsView.fitInView(QRectF(0,0,w,h), Qt.KeepAspectRatio)
        self.graphicsView.update()
        
    def saveSettings(self):
        conf = ConfigParser.ConfigParser()
        proj_home = dirname(realpath(__file__))
        proj_home = proj_home[0:proj_home.rfind('/')]
        conf.read(proj_home + '/global.cfg')
        
        conf.set('suspension','compression_FD',self.compression_FD.value())
        conf.set('suspension','compression_FP',self.compression_FP.value())
        conf.set('suspension','compression_RD',self.compression_RD.value())
        conf.set('suspension','compression_RP',self.compression_RP.value())
        
        conf.set('suspension','damping_FD',self.damping_FD.value())
        conf.set('suspension','damping_FP',self.damping_FP.value())
        conf.set('suspension','damping_RD',self.damping_RD.value())
        conf.set('suspension','damping_RP',self.damping_RP.value())
        
        conf.set('suspension','stiffness_FD',self.stiffness_FD.value())
        conf.set('suspension','stiffness_FP',self.stiffness_FP.value())
        conf.set('suspension','stiffness_RD',self.stiffness_RD.value())
        conf.set('suspension','stiffness_RP',self.stiffness_RP.value())
        
        conf.set('tire','grip_FD',self.grip_FD.value())
        conf.set('tire','grip_FP',self.grip_FP.value())
        conf.set('tire','grip_RD',self.grip_RD.value())
        conf.set('tire','grip_RP',self.grip_RP.value())
        
        conf.set('tire','steerable_FD',self.steerable_FD.isChecked())
        conf.set('tire','steerable_FP',self.steerable_FP.isChecked())
        conf.set('tire','steerable_RD',self.steerable_RD.isChecked())
        conf.set('tire','steerable_RP',self.steerable_RP.isChecked())
        
        conf.set('tire','rollInfluence_FD',self.rollInfluence_FD.value())
        conf.set('tire','rollInfluence_FP',self.rollInfluence_FP.value())
        conf.set('tire','rollInfluence_RD',self.rollInfluence_RD.value())
        conf.set('tire','rollInfluence_RP',self.rollInfluence_RP.value())
        
        conf.set('cruise_control','kp',self.kpSlider.value())
        conf.set('cruise_control','ki',self.kiSlider.value())
        conf.set('cruise_control','kd',self.kdSlider.value())
        conf.set('cruise_control','SP',self.SP.value())
        
        conf.set('game','flipThreshold',self.dial.value() * pi /100.0)
        conf.set('game','timeLimit',self.timeEdit.time().second() + self.timeEdit.time().minute()*60)
       
        fp = open(proj_home + '/global.cfg','w')
        conf.write(fp)
        
    def readSettings(self,filename):
        conf = ConfigParser.ConfigParser()
        conf.read(filename)
        self.compression_FD.setValue(conf.getfloat('suspension','compression_FD'))
        self.compression_FP.setValue(conf.getfloat('suspension','compression_FP'))
        self.compression_RD.setValue(conf.getfloat('suspension','compression_RD'))
        self.compression_RP.setValue(conf.getfloat('suspension','compression_RP'))
        
        self.damping_FD.setValue(conf.getfloat('suspension','damping_FD'))
        self.damping_FP.setValue(conf.getfloat('suspension','damping_FP'))
        self.damping_RD.setValue(conf.getfloat('suspension','damping_RD'))
        self.damping_RP.setValue(conf.getfloat('suspension','damping_RP'))
        
        self.stiffness_FD.setValue(conf.getfloat('suspension','stiffness_FD'))
        self.stiffness_FP.setValue(conf.getfloat('suspension','stiffness_FP'))
        self.stiffness_RD.setValue(conf.getfloat('suspension','stiffness_RD'))
        self.stiffness_RP.setValue(conf.getfloat('suspension','stiffness_RP'))
        
        self.grip_FD.setValue(conf.getfloat('tire','grip_FD'))
        self.grip_FP.setValue(conf.getfloat('tire','grip_FP'))
        self.grip_RD.setValue(conf.getfloat('tire','grip_RD'))
        self.grip_RP.setValue(conf.getfloat('tire','grip_RP'))
        
        self.steerable_FD.setChecked(conf.getboolean('tire','steerable_FD'))
        self.steerable_FP.setChecked(conf.getboolean('tire','steerable_FP'))
        self.steerable_RD.setChecked(conf.getboolean('tire','steerable_RD'))
        self.steerable_RP.setChecked(conf.getboolean('tire','steerable_RP'))
        
        self.rollInfluence_FD.setValue(conf.getfloat('tire','rollInfluence_FD'))
        self.rollInfluence_FP.setValue(conf.getfloat('tire','rollInfluence_FP'))
        self.rollInfluence_RD.setValue(conf.getfloat('tire','rollInfluence_RD'))
        self.rollInfluence_RP.setValue(conf.getfloat('tire','rollInfluence_RP'))
        
        self.kpSlider.setValue(conf.getint('cruise_control','kp'))
        self.kiSlider.setValue(conf.getint('cruise_control','ki'))
        self.kdSlider.setValue(conf.getint('cruise_control','kd'))
        self.SP.setValue(conf.getfloat('cruise_control','SP'))
        
        self.dial.setValue(conf.getfloat('game','flipThreshold') * 100/(pi))
        timeLimit = conf.getint('game','timeLimit')
        self.timeEdit.setTime(QTime(0,timeLimit / 60,timeLimit % 60))
        
