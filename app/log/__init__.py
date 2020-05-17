import logging
from logging.handlers import TimedRotatingFileHandler
import datetime

eclogger = logging.getLogger("eclog")
fmter = logging.Formatter('%(asctime)s | %(levelname)s | %(filename)s | %(module)s | %(lineno)d | %(funcName)s | %(message)s')
#hdlr = logging.FileHandler("log/eclog")
hdlr = TimedRotatingFileHandler(filename='log/eclog', when='MIDNIGHT', backupCount=7, atTime=datetime.time(0, 0, 0, 0))
hdlr.setFormatter(fmt=fmter)
eclogger.addHandler(hdlr=hdlr)
eclogger.setLevel('INFO')

paylogger = logging.getLogger("paylog")
payhdlr = TimedRotatingFileHandler(filename='log/paylog', when='MIDNIGHT', backupCount=7, atTime=datetime.time(0, 0, 0, 0))
payhdlr.setFormatter(fmt=fmter)
paylogger.addHandler(hdlr=payhdlr)
paylogger.setLevel('INFO')