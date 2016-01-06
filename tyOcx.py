import sys
import asyncio
import socket
import win32com

#from PyQt5.QtGui import QGuiApplication
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
#from win32com import client 
from quamash import QEventLoop

qt5_url = "C:/cygwin/home/utylee/.virtualenvs/tyTrader-win/Lib/site-packages/PyQt5/plugins" 

# PyQt와 quamash를 이용해서 asyncio eventloop방식을 사용합니다
# PyQt5를 virtualenv 상에서 사용하기 위해서는 정확하게 Platform 폴더를 지정해줘야 한다고 합니다.
QCoreApplication.setLibraryPaths([qt5_url])
app = QApplication(sys.argv)
loop = QEventLoop(app)
asyncio.set_event_loop(loop)

# 인터페이스 윈도우입니다.
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("tyOcx")
        self.setGeometry(1800,300,300,400)

        #test =win32com.client.Dispatch("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        # 키움OpenApi 접속 창을 띄웁니다.
        #self.kiwoom.dynamicCall("CommConnect()")
        self.kiwoom.CommConnect()

        # 접속 버튼을 생성합니다
        self.btn1 = QPushButton("Acc Info", self)
        self.btn1.move(20, 20)
        self.btn1.clicked.connect(self.OnBtn1_clicked)
        #self.connect(self.btn1, SIGNAL("clicked()"), self.OnBtn1_clicked)

        # ocx receive 시그널을 연결해줍니다.
        self.kiwoom.OnReceiveTrData.connect(self.OnReceiveTrData)
        self.kiwoom.OnReceiveRealData.connect(self.OnReceiveRealData)
        self.kiwoom.OnReceiveChejanData.connect(self.OnReceiveChejanData)


        # 주가 정보 요청 버튼을 생성합니다
        self.btn2 = QPushButton("request", self)
        self.btn2.move(20, 70)
        self.btn2.clicked.connect(self.OnBtn2_clicked)
        #self.connect(self.btn2, SIGNAL("clicked()"), self.OnBtn2_clicked)

        # 실시간 시세 추가 버튼을 생성합니다.
        self.btn3 = QPushButton("realtime", self)
        self.btn3.move(20, 100)
        self.btn3.clicked.connect(self.OnBtn3_clicked)

        # 매수 주문 버튼을 생성합니다.
        self.btn4 = QPushButton("order", self)
        self.btn4.move(20, 130)
        self.btn4.clicked.connect(self.OnBtn4_clicked)

    def OnBtn1_clicked(self):
        #ret = self.kiwoom.dynamicCall("CommConnect()")
        #ret = self.kiwoom.CommConnect()

        ret = self.kiwoom.GetLoginInfo("ACCNO")
        print(ret.strip())

    def OnBtn2_clicked(self):
        print('request emitted')
        #ret = self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", "053260") # 금강철강
        ret = self.kiwoom.SetInputValue("종목코드", "016090")  # 대현
        #ret = self.kiwoom.SetInputValue(QString("종목코드"), QString("053260"))
        #ret = self.kiwoom.SetInputValue("종목코드", "016090")
        print(ret)
        #ret = self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "주식기본정보",\
        #                            "OPT10001", 0, "0101")
        ret = self.kiwoom.CommRqData("주식기본정보", "OPT10001", 0, "0101")
        print(ret)

    def OnBtn3_clicked(self):
        #ret = self.kiwoom.dynamicCall("SetRealReg(QString, QString, int, QString)", "9999", "053260", 0, "0")
        #ret = self.kiwoom.dynamicCall("SetRealReg(QString, QString, int, QString)", "9999", "016090", 0, "0")
        ret = self.kiwoom.SetRealReg("0001", "099520;046110", "10", "0")
        print(ret)

    # 주문 버튼이 눌렸을 때의 로직함수입니다.
    def OnBtn4_clicked(self):
        print("주문직전")
        ret = self.kiwoom.SendOrder("주식주문", "0107", "3670956111", 1, "016090", 1, 3700, "0", "")
        #ret = self.kiwoom.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",\
        #                ["주식주문", "0107", "3670956111", 1, "016090", 1, 3700, "0", ""])
        print("주문전송 ret : {}".format(ret))

    # TR가격데이터가 수신되었을 때의 트리거 함수입니다.
    def OnReceiveTrData(self, sScrNo, sRQName, sTRCode, sRecordName, sPreNext,\
            nDataLength, sErrorCode, sMessage, sSPlmMsg):
        if sRQName == "주식기본정보":
            print('come here')
            #cur_price = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", \
                                #sTRCode, "", sRQName, 0, "현재가")
            cur_price = self.kiwoom.CommGetData(sTRCode, "", sRQName, 0, "현재가")
            print("현재가 : {}".format(cur_price.strip()))
        else:
            print('OnReceiveTrData : {}'.format(sRQName.strip()))
            order_vol = self.kiwoom.CommRqData("주문수량", "opt10012", 0, "0101")
            print('주문수량 : {}'.format(order_vol))

    # 실시간 가격데이터가 수신되었을 때의 트리거 함수입니다.
    def OnReceiveRealData(self, sCode, sRealType, sRealData):
        print('실시간 시세 OnReceive!()')
        #real_price = self.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, 0 )
        real_price = self.kiwoom.GetCommRealData("주식시세", 10)
        real_volume = self.kiwoom.GetCommRealData("주식체결", 15)
        print("종목코드 : {}, 현재가 : {}, 거래량 : {}".format(sCode, real_price.strip(), real_volume.strip()))

    # 주문 접수/확인 수신 시 트리거되는 함수입니다.
    def OnReceiveChejanData(self, sGubun, nItemCnt, sFIDList):
        print("OnReceiveChejanData()")

        order_num = self.kiwoom.GetChejanData(302)
        order_vol = self.kiwoom.GetChejanData(900)
        order_price = self.kiwoom.GetChejanData(901)
        
        print("주문번호 : {}, 주문수량 : {}, 주문가격 : {}".format(order_num, order_vol, order_price))

with loop:
    window = MyWindow()
    window.show()
    loop.run_forever()

'''
if __name__ == "__main__":
    QCoreApplication.setLibraryPaths([qt5_url])

    #app = QApplication(sys.argv)
    window = MyWindows()
    window.show()
    #app.exec_()
'''
