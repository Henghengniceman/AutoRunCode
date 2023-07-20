import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDate,   QDateTime , QTime
from datetime import datetime
from PyQt5.QtCore import Qt
from WorkFlow import WorkFlow
MainPath = 'Z:/henghengzhang/raymetrics/Lidar_Data'
class workflow_GUI(WorkFlow):
    def __init__(self,MainPath,ConfigInfo,loginfo,Date,):
        super(workflow_GUI,self).__init__(MainPath)
        self.MainPath = MainPath
        self.ConfigInfo = ConfigInfo
        self.loginfo = loginfo
        self.Date = Date

class WorkFlowGUI(QWidget):
    def __init__(self):
        super(WorkFlowGUI, self).__init__()
        self.ConfigInfo = {'GlueRange': 2250.0, 'ZenithReferenceHeight': 4000.0,
                           'AzimuthReferenceHeight': 10000.0, 'FixPointReferenceHeight': 10000.0,
                           'ShowDepolHeight': 10000.0, 'Sa': 40.0, 'R_zc': 1.0, 'V_constant': 0.0335,
                           'DepolSNR': 3.0, 'Overlap': 1.0, 'RCSProfiles': 1.0,
                           'RCSPolar': 1.0, 'BetaProfiles': 1.0, 'BetaPolar': 1.0, 'BetaData': 1.0,
                           'DeltaProfiles': 1.0, 'DeltaPolar': 1.0, 'DeltaData': 1.0, 'ZenithContourf': 1.0,
                           'FixBetaContourf': 1.0, 'FixDeltaContourf': 1.0,
                           'StartDate': datetime(2018, 1, 1, 0, 0), 'EndDate': datetime(2018, 1, 1, 0, 0)}
        self.ReadConfigFile()
        self.initUI()


         # self.loginfo = ''
        # self.Date = datetime(2018,1,1,0,0,0)
    def initUI(self):
        self.setWindowTitle('KASCAL Data Analysis Tool')
        self.setWindowIcon(QIcon('./images/LIDAR.ico'))
        wlayout = QVBoxLayout()
        # title
        Title  = QLabel('KASCAL Data Analysis Tool',self)
        Title.setAlignment(Qt.AlignCenter)
        pe = QPalette()
        pe.setColor(QPalette.WindowText,Qt.red)
        Title.setAutoFillBackground(True)
        pe.setColor(QPalette.Window,Qt.black)
        Title.setPalette(pe)
        Title.setFont(QFont("Roman times",20,QFont.Bold))
        # time
        fromlayout = QFormLayout()
        LabelStartime = QLabel('Start Time：')
        LabelEnd = QLabel('End Time：')
        self.StartDate = QDateTimeEdit(QDate(self.ConfigInfo['StartDate'].year,self.ConfigInfo['StartDate'].month,self.ConfigInfo['StartDate'].day),self)
        self.EndDate = QDateTimeEdit(QDate(self.ConfigInfo['EndDate'].year,self.ConfigInfo['EndDate'].month,self.ConfigInfo['EndDate'].day),self)
        self.StartDate.setDisplayFormat("yyyy.MM.dd")
        self.EndDate.setDisplayFormat("yyyy.MM.dd")
        self.StartDate.setCalendarPopup(True)
        self.EndDate.setCalendarPopup(True)
        self.StartDate.dateChanged.connect(self.onStartDateChanged)
        self.EndDate.dateChanged.connect(self.OnEndDateChange)
        fromlayout.addRow(LabelStartime, self.StartDate)
        fromlayout.addRow(LabelEnd, self.EndDate)
        fwg = QWidget()
        fwg.setLayout(fromlayout)
        # parameter title
        ParaTitlelayout = QFormLayout()
        Paratitle  = QLabel('Parameters：',self)
        Paratitle.setAlignment(Qt.AlignLeft)
        Paratitle.setFont(QFont("Arial",12,QFont.Bold))
        Inibtn = QPushButton('Load Config. File')
        Inibtn.clicked.connect(self.LoadConfigFile)
        ParaTitlelayout.addRow(Paratitle,Inibtn)
        fwgparatitle = QWidget()
        fwgparatitle.setLayout(ParaTitlelayout)
        # parameter
        paraHlayout  = QHBoxLayout()
        ParaformlatoutLeft = QFormLayout()
        ParaformlatoutRight = QFormLayout()
        GlueRangeLabel = QLabel('Glue Range:')
        self.GlueRangesp = QDoubleSpinBox()
        self.GlueRangesp.setDecimals(2)
        self.GlueRangesp.setMinimum(1875)
        self.GlueRangesp.setMaximum(3750)
        self.GlueRangesp.setSingleStep(37.5)
        self.GlueRangesp.setValue(int(self.ConfigInfo['GlueRange']))
        self.GlueRangesp.valueChanged.connect(lambda:self.valuechange('GlueRange'))

        AzimuthRefereceHeightLabel = QLabel('Azimuth Reference Height:')
        self.AzimuthReferenceHeightsp = QDoubleSpinBox()
        self.AzimuthReferenceHeightsp.setDecimals(1)
        self.AzimuthReferenceHeightsp.setMinimum(8000)
        self.AzimuthReferenceHeightsp.setMaximum(12000)
        self.AzimuthReferenceHeightsp.setSingleStep(500)
        self.AzimuthReferenceHeightsp.setValue(self.ConfigInfo['AzimuthReferenceHeight'])
        self.AzimuthReferenceHeightsp.valueChanged.connect(lambda:self.valuechange('AzimuthReferenceHeight'))

        ShowDepolHeightLabel = QLabel('Show Depol Height:')
        self.ShowDepolHeightsp = QDoubleSpinBox()
        self.ShowDepolHeightsp.setDecimals(1)
        self.ShowDepolHeightsp.setMinimum(7500)
        self.ShowDepolHeightsp.setMaximum(15000)
        self.ShowDepolHeightsp.setSingleStep(150)
        self.ShowDepolHeightsp.setValue(int(self.ConfigInfo['ShowDepolHeight']))
        self.ShowDepolHeightsp.valueChanged.connect(lambda:self.valuechange('ShowDepolHeight'))

        R_zcLabel = QLabel('Scatter Ratio:')
        self.R_zcsp = QDoubleSpinBox()
        self.R_zcsp.setDecimals(2)
        self.R_zcsp.setMinimum(0.0)
        self.R_zcsp.setMaximum(0.2)
        self.R_zcsp.setSingleStep(0.01)
        self.R_zcsp.setValue(self.ConfigInfo['R_zc'])
        self.R_zcsp.valueChanged.connect(lambda:self.valuechange('R_zc'))

        DepolSNRLabel = QLabel('Depol SNR:')
        self.DepolSNRsp = QDoubleSpinBox()
        self.DepolSNRsp.setDecimals(1)
        self.DepolSNRsp.setMinimum(0)
        self.DepolSNRsp.setMaximum(4)
        self.DepolSNRsp.setSingleStep(0.5)
        self.DepolSNRsp.setValue(self.ConfigInfo['DepolSNR'])
        self.DepolSNRsp.valueChanged.connect(lambda:self.valuechange('DepolSNR'))

        ParaformlatoutLeft.addRow(GlueRangeLabel,self.GlueRangesp)
        ParaformlatoutLeft.addRow(AzimuthRefereceHeightLabel,self.AzimuthReferenceHeightsp)
        ParaformlatoutLeft.addRow(ShowDepolHeightLabel,self.ShowDepolHeightsp)
        ParaformlatoutLeft.addRow(R_zcLabel,self.R_zcsp)
        ParaformlatoutLeft.addRow(DepolSNRLabel,self.DepolSNRsp)
        fwgleft = QWidget()
        fwgleft.setLayout(ParaformlatoutLeft)

        ZenithReferenceHeightLabel = QLabel('Zenith Reference Height:')
        self.ZenithReferenceHeightsp = QDoubleSpinBox()
        self.ZenithReferenceHeightsp.setDecimals(1)
        self.ZenithReferenceHeightsp.setMinimum(3000)
        self.ZenithReferenceHeightsp.setMaximum(10000)
        self.ZenithReferenceHeightsp.setSingleStep(500)
        self.ZenithReferenceHeightsp.setValue(self.ConfigInfo['ZenithReferenceHeight'])
        self.ZenithReferenceHeightsp.valueChanged.connect(lambda:self.valuechange('ZenithReferenceHeight'))

        FixPointReferenceHeightLabel = QLabel('Fixed Reference Height:')
        self.FixPointReferenceHeightsp = QDoubleSpinBox()
        self.FixPointReferenceHeightsp.setDecimals(1)
        self.FixPointReferenceHeightsp.setMinimum(8000)
        self.FixPointReferenceHeightsp.setMaximum(12000)
        self.FixPointReferenceHeightsp.setSingleStep(500)
        self.FixPointReferenceHeightsp.setValue(self.ConfigInfo['FixPointReferenceHeight'])
        self.FixPointReferenceHeightsp.valueChanged.connect(lambda:self.valuechange('FixPointReferenceHeight'))

        SaLabel = QLabel('LIDAR Ratio:')
        self.Sasp = QDoubleSpinBox()
        self.Sasp.setDecimals(1)
        self.Sasp.setMinimum(20)
        self.Sasp.setMaximum(100)
        self.Sasp.setSingleStep(1)
        self.Sasp.setValue(self.ConfigInfo['Sa'])
        self.Sasp.valueChanged.connect(lambda:self.valuechange('Sa'))

        # V_constantLabel = QLabel('Depol. Constant:')
        # self.V_constantsp = QDoubleSpinBox()
        # self.V_constantsp.setDecimals(4)
        # self.V_constantsp.setMinimum(0.0325)
        # self.V_constantsp.setMaximum(0.0345)
        # self.V_constantsp.setSingleStep(0.0001)
        # self.V_constantsp.setValue(self.ConfigInfo['V_constant'])
        # self.V_constantsp.valueChanged.connect(lambda:self.valuechange('V_constant'))

        self.OverlapCB = QCheckBox("&Overlap")
        self.OverlapCB.setChecked(bool(self.ConfigInfo['Overlap']))
        self.OverlapCB.stateChanged.connect(lambda:self.btnstate('Overlap'))

    # self.OverlapCB.valueChanged.connect(lambda:self.valuechange('Overlap'))
        ParaformlatoutRight.addRow(ZenithReferenceHeightLabel,self.ZenithReferenceHeightsp)
        ParaformlatoutRight.addRow(FixPointReferenceHeightLabel,self.FixPointReferenceHeightsp)
        ParaformlatoutRight.addRow(SaLabel,self.Sasp)
        # ParaformlatoutRight.addRow(V_constantLabel,self.V_constantsp)
        ParaformlatoutRight.addRow(self.OverlapCB)
        fwgParameter = QWidget()
        fwgParameter.setLayout(paraHlayout)
        fwgParameterl = QWidget()
        fwgParameterl.setLayout(ParaformlatoutLeft)
        paraHlayout.addWidget(fwgParameterl)
        fwgParameterr = QWidget()
        fwgParameterr.setLayout(ParaformlatoutRight)
        paraHlayout.addWidget(fwgParameterr)
        # Product
        Producttitle  = QLabel('  Product：',self)
        Producttitle.setAlignment(Qt.AlignLeft)
        Producttitle.setFont(QFont("Arial",12,QFont.Bold))

        ProGlayout  = QGridLayout()
        ProGlayout.setColumnStretch(1, 2)
        ProGlayout.setColumnStretch(2, 6)

        self.RCSProfilesCB = QCheckBox("&RCSProfiles")
        self.RCSProfilesCB.setChecked(bool(self.ConfigInfo['RCSProfiles']))
        self.RCSProfilesCB.stateChanged.connect(lambda:self.btnstate('RCSProfiles'))
        ProGlayout.addWidget(self.RCSProfilesCB,0,0)

        self.RCSPolarCB = QCheckBox("&RCSPolar")
        self.RCSPolarCB.setChecked(bool(self.ConfigInfo['RCSPolar']))
        self.RCSPolarCB.stateChanged.connect(lambda:self.btnstate('RCSPolar'))
        ProGlayout.addWidget(self.RCSPolarCB,0,1)

        self.BetaProfilesCB = QCheckBox("&BetaProfiles")
        self.BetaProfilesCB.setChecked(bool(self.ConfigInfo['BetaProfiles']))
        self.BetaProfilesCB.stateChanged.connect(lambda:self.btnstate('BetaProfiles'))
        ProGlayout.addWidget(self.BetaProfilesCB,0,2)

        self.BetaPolarCB = QCheckBox("&BetaPolar")
        self.BetaPolarCB.setChecked(bool(self.ConfigInfo['BetaPolar']))
        self.BetaPolarCB.stateChanged.connect(lambda:self.btnstate('BetaPolar'))
        ProGlayout.addWidget(self.BetaPolarCB,0,3)

        self.BetaDataCB = QCheckBox("&BetaData")
        self.BetaDataCB.setChecked(bool(self.ConfigInfo['BetaData']))
        self.BetaDataCB.stateChanged.connect(lambda:self.btnstate('BetaData'))
        ProGlayout.addWidget(self.BetaDataCB,0,4)

        self.ZenithContourfCB = QCheckBox("&ZenithContourf")
        self.ZenithContourfCB.setChecked(bool(self.ConfigInfo['ZenithContourf']))
        self.ZenithContourfCB.stateChanged.connect(lambda:self.btnstate('ZenithContourf'))
        ProGlayout.addWidget(self.ZenithContourfCB,0,5)

        self.DeltaProfilesCB = QCheckBox("&DeltaProfiles")
        self.DeltaProfilesCB.setChecked(bool(self.ConfigInfo['DeltaProfiles']))
        self.DeltaProfilesCB.stateChanged.connect(lambda:self.btnstate('DeltaProfiles'))
        ProGlayout.addWidget(self.DeltaProfilesCB,1,0)

        self.DeltaPolarCB = QCheckBox("&DeltaPolar")
        self.DeltaPolarCB.setChecked(bool(self.ConfigInfo['DeltaPolar']))
        self.DeltaPolarCB.stateChanged.connect(lambda:self.btnstate('DeltaPolar'))
        ProGlayout.addWidget(self.DeltaPolarCB,1,1)

        self.DeltaDataCB = QCheckBox("&DeltaData")
        self.DeltaDataCB.setChecked(bool(self.ConfigInfo['DeltaData']))
        self.DeltaDataCB.stateChanged.connect(lambda:self.btnstate('DeltaData'))
        ProGlayout.addWidget(self.DeltaDataCB,1,2)

        self.FixBetaContourfCB = QCheckBox("&FixBetaContourf")
        self.FixBetaContourfCB.setChecked(bool(self.ConfigInfo['FixBetaContourf']))
        self.FixBetaContourfCB.stateChanged.connect(lambda:self.btnstate('FixBetaContourf'))
        ProGlayout.addWidget(self.FixBetaContourfCB,1,3)

        self.FixDeltaContourfCB = QCheckBox("&FixDeltaContourf")
        self.FixDeltaContourfCB.setChecked(bool(self.ConfigInfo['FixDeltaContourf']))
        self.FixDeltaContourfCB.stateChanged.connect(lambda:self.btnstate('FixDeltaContourf'))
        ProGlayout.addWidget(self.FixDeltaContourfCB,1,4)
        fwgPro = QWidget()
        fwgPro.setLayout(ProGlayout)

        self.StartButtion = QPushButton('Start Analysis')
        self.StartButtion.setStyleSheet("QPushButton{font-size:32px;color:rgb(0,0,0,255);} \
                QPushButton{background-color:rgb(170,200,50)}\ QPushButton:hover{background-color:rgb(50, 170, 200)}")
        self.StartButtion.setShortcut("Ctrl+Return")
        self.StartButtion.clicked.connect(self.StartAnalysis)

        wlayout.addWidget(Title)
        wlayout.addWidget(fwg)
        wlayout.addWidget(fwgparatitle)
        wlayout.addWidget(fwgParameter)
        wlayout.addWidget(Producttitle)
        wlayout.addWidget(fwgPro)
        wlayout.addWidget(self.StartButtion)
        self.setLayout(wlayout)
    def ReadConfigFile(self):
        fname, _  = QFileDialog.getOpenFileName(self, 'Open file', './',"Config. files (*.init *.txt)")
        # print(fname)
        with open(fname) as f:
            self.lines = f.readlines()
            for line in self.lines [3:]:
                if len(line.split(':')) == 2:
                    try:
                        self.ConfigInfo.update({line.split(':')[0].replace(' ',''):float(line.split(':')[1])})
                    except:
                        self.ConfigInfo.update({line.split(':')[0].replace(' ',''):line.split(':')[1].replace(' ','')})
            for line in self.lines[:3]:
                if len(line.split(':')) == 2:
                    self.ConfigInfo.update({line.split(':')[0].replace(' ',''):datetime.strptime(line.split(':')[1].replace(' ','').replace('\n',' '), '%Y-%m-%d ')})
        self.loginfo = ''
        for line in self.lines:
            self.loginfo = self.loginfo+line
        # date
        self.Date = self.ConfigInfo['StartDate'].strftime('%Y%m%d')
        # print(self.lines)
    def LoadConfigFile(self):
        self.ReadConfigFile()
        self.UIParaUpdate()
    def UIParaUpdate(self):
        self.StartDate.setDate(QDate(self.ConfigInfo['StartDate'].year,self.ConfigInfo['StartDate'].month,self.ConfigInfo['StartDate'].day))
        self.EndDate.setDate(QDate(self.ConfigInfo['EndDate'].year,self.ConfigInfo['EndDate'].month,self.ConfigInfo['EndDate'].day))
        self.GlueRangesp.setValue(int(self.ConfigInfo['GlueRange']))
        self.ZenithReferenceHeightsp.setValue(self.ConfigInfo['ZenithReferenceHeight'])
        self.AzimuthReferenceHeightsp.setValue(self.ConfigInfo['AzimuthReferenceHeight'])
        self.FixPointReferenceHeightsp.setValue(self.ConfigInfo['FixPointReferenceHeight'])
        self.ShowDepolHeightsp.setValue(int(self.ConfigInfo['ShowDepolHeight']))
        self.Sasp.setValue(self.ConfigInfo['Sa'])
        self.R_zcsp.setValue(self.ConfigInfo['R_zc'])
        self.V_constantsp.setValue(self.ConfigInfo['V_constant'])
        self.DepolSNRsp.setValue(self.ConfigInfo['DepolSNR'])
        self.OverlapCB.setChecked(bool(self.ConfigInfo['Overlap']))
        self.RCSProfilesCB.setChecked(bool(self.ConfigInfo['RCSProfiles']))
        self.BetaProfilesCB.setChecked(bool(self.ConfigInfo['BetaProfiles']))
        self.BetaPolarCB.setChecked(bool(self.ConfigInfo['BetaPolar']))
        self.BetaDataCB.setChecked(bool(self.ConfigInfo['BetaData']))
        self.ZenithContourfCB.setChecked(bool(self.ConfigInfo['ZenithContourf']))
        self.DeltaProfilesCB.setChecked(bool(self.ConfigInfo['DeltaProfiles']))
        self.DeltaPolarCB.setChecked(bool(self.ConfigInfo['DeltaPolar']))
        self.DeltaDataCB.setChecked(bool(self.ConfigInfo['DeltaData']))
        self.FixBetaContourfCB.setChecked(bool(self.ConfigInfo['FixBetaContourf']))
        self.FixDeltaContourfCB.setChecked(bool(self.ConfigInfo['FixDeltaContourf']))



    def onStartDateChanged(self,date):
        # print(date.toString("yyyy-MM-dd"))
        StartDates = datetime.strptime(date.toString("yyyy-MM-dd"),"%Y-%m-%d")
        self.ConfigInfo['StartDate'] = StartDates
        self.lines[1] = 'Start Date : '+ date.toString("yyyy-MM-dd")+'\n'
        # print(self.ConfigInfo['StartDate'])
    def OnEndDateChange(self,date):
        EndDates = datetime.strptime(date.toString("yyyy-MM-dd"),"%Y-%m-%d")
        self.ConfigInfo['EndDate'] = EndDates
        self.lines[2] = 'End Date : '+ date.toString("yyyy-MM-dd")+'\n'
        # print(self.ConfigInfo['EndDate'])
    def valuechange(self,index):
        # print(index)
        # print('self.ConfigInfo["{}"] =self.{}sp.value()'.format(index,index))
        exec('self.ConfigInfo["{}"] =self.{}sp.value()'.format(index,index))
        if index == 'GlueRange':
            self.lines[3] = 'GlueRange : '+ str(self.ConfigInfo['GlueRange'])+'\n'
        if index == 'ZenithReferenceHeight':
            self.lines[4] = 'ZenithReferenceHeight : '+ str(self.ConfigInfo['ZenithReferenceHeight'])+'\n'
        if index == 'AzimuthReferenceHeight':
            self.lines[5] = 'AzimuthReferenceHeight : '+ str(self.ConfigInfo['AzimuthReferenceHeight'])+'\n'
        if index == 'FixPointReferenceHeight':
            self.lines[6] = 'FixPointReferenceHeight : '+ str(self.ConfigInfo['FixPointReferenceHeight'])+'\n'
        if index == 'ShowDepolHeight':
            self.lines[7] = 'ShowDepolHeight : '+ str(self.ConfigInfo['ShowDepolHeight'])+'\n'
        if index == 'Sa':
            self.lines[8] = 'Sa : '+ str(self.ConfigInfo['Sa'])+'\n'
        if index == 'R_zc':
            self.lines[9] = 'R_zc : '+ str(self.ConfigInfo['R_zc'])+'\n'
        if index == 'V_constant':
            self.lines[10] = 'V_constant : '+ str(self.ConfigInfo['V_constant'])+'\n'
        if index == 'DepolSNR':
            self.lines[11] = 'DepolSNR : '+ str(self.ConfigInfo['DepolSNR'])+'\n'
        if index == 'DepoShowIndex':
            self.lines[12] = 'DepoShowIndex : '+ str(self.ConfigInfo['DepoShowIndex'])+'\n'

    def btnstate(self,index):
        # print(index)
        if eval('self.'+index+'CB.checkState()'):
            self.ConfigInfo[index] = 1
        else:
            self.ConfigInfo[index] = 0
        if index == 'Overlap':
            self.lines[13] = 'Overlap : '+ str(self.ConfigInfo['Overlap'])+'\n'
        # print(self.lines)
        if index == 'RCSProfiles':
            self.lines[15] = 'RCSProfiles : '+ str(self.ConfigInfo['RCSProfiles'])+'\n'
        # print(self.lines)
        if index == 'RCSPolar':
            self.lines[16] = 'RCSPolar : '+ str(self.ConfigInfo['RCSPolar'])+'\n'
        if index == 'BetaProfiles':
            self.lines[17] = 'BetaProfiles : '+ str(self.ConfigInfo['BetaProfiles'])+'\n'
        if index == 'BetaPolar':
            self.lines[18] = 'BetaPolar : '+ str(self.ConfigInfo['BetaPolar'])+'\n'
        if index == 'BetaData':
            self.lines[19] = 'BetaData : '+ str(self.ConfigInfo['BetaData'])+'\n'
        if index == 'DeltaProfiles':
            self.lines[20] = 'DeltaProfiles : '+ str(self.ConfigInfo['DeltaProfiles'])+'\n'
        if index == 'DeltaPolar':
            self.lines[21] = 'DeltaPolar : '+ str(self.ConfigInfo['DeltaPolar'])+'\n'
        if index == 'DeltaData':
            self.lines[22] = 'DeltaData : '+ str(self.ConfigInfo['DeltaData'])+'\n'
        if index == 'ZenithContourf':
            self.lines[23] = 'ZenithContourf : '+ str(self.ConfigInfo['ZenithContourf'])+'\n'
        if index == 'FixBetaContourf':
            self.lines[24] = 'FixBetaContourf : '+ str(self.ConfigInfo['FixBetaContourf'])+'\n'
        if index == 'FixDeltaContourf':
            self.lines[25] = 'FixDeltaContourf : '+ str(self.ConfigInfo['FixDeltaContourf'])+'\n'

    # print(self.OverlapCB.checkState())
        # exec('self.ConfigInfo["{}"] =self.{}CB.checkState()'.format(index,index))
        # print(self.ConfigInfo[index])
    def StartAnalysis(self):
        print('Start Analysis')
        # print(self.ConfigInfo)
        # self.isEnsable(False)
        loginfo = ''
        for line in self.lines:
            loginfo = loginfo+line
        # date
        Date = self.ConfigInfo['StartDate'].strftime('%Y%m%d')
     
        workflowI = workflow_GUI(self.ConfigInfo['DataPath'],self.ConfigInfo,loginfo,Date)
        workflowI.ZenithScanning()
        workflowI.AzimuthScanning()
        workflowI.FixedPoint()
        self.isEnsable(True)
    def isEnsable(self,isenbale):
        self.StartDate.setEnabled(isenbale)
        self.EndDate.setEnabled(isenbale)
        self.GlueRangeIndexsp.setEnabled(isenbale)
        self.ZenithReferenceHeightsp.setEnabled(isenbale)
        self.AzimuthReferenceHeightsp.setEnabled(isenbale)
        self.FixPointReferenceHeightsp.setEnabled(isenbale)
        self.ShowDepolIndexsp.setEnabled(isenbale)
        self.Sasp.setEnabled(isenbale)
        self.R_zcsp.setEnabled(isenbale)
        self.V_constantsp.setEnabled(isenbale)
        self.DepolSNRsp.setEnabled(isenbale)
        self.OverlapCB.setEnabled(isenbale)
        self.RCSProfilesCB.setEnabled(isenbale)
        self.BetaProfilesCB.setEnabled(isenbale)
        self.BetaPolarCB.setEnabled(isenbale)
        self.BetaDataCB.setEnabled(isenbale)
        self.ZenithContourfCB.setEnabled(isenbale)
        self.DeltaProfilesCB.setEnabled(isenbale)
        self.DeltaPolarCB.setEnabled(isenbale)
        self.DeltaDataCB.setEnabled(isenbale)
        self.FixBetaContourfCB.setEnabled(isenbale)
        self.FixDeltaContourfCB.setEnabled(isenbale)

def auto_analysis_GUI():
    app = QApplication(sys.argv)
    demo = WorkFlowGUI()
    # print(demo.lines)
    demo.show()
    sys.exit(app.exec_())

# auto_analysis_GUI()