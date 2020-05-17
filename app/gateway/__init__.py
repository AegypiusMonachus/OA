from . import xinbaofuGW,boqingfuGW,ryun70GW,bibaoGW,huifengGW,safGW,wyGW

class GatewaytFactory():
    @staticmethod
    def getPaymentGateway(id):
        if id ==1:
            return xinbaofuGW.XinbaofuGW()
        if id ==2:
            return boqingfuGW.BoqingfuGW()        
        if id ==5:
            return ryun70GW.Ryun70GW()
        if id ==6:
            return bibaoGW.BibaoGW()
        if id ==7:
            return huifengGW.HuifengGW()
        if id ==8:
            return safGW.SAFGW()
        if id ==9:
            return wyGW.WyGW()