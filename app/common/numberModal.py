import time, datetime, math

def getModalSQL(type, m_date,diff):
	m_timeStruct = time.strptime(m_date, "%Y-%m-%d") 
	m_date2 = time.strftime("%Y%m%d", m_timeStruct)
	lastDate =datetime.datetime.strptime(m_date, "%Y-%m-%d") + datetime.timedelta(-1)
	m_lastDate = lastDate.strftime("%Y%m%d")
	m_sql = ''
	#重庆时时彩
	if(type == 1):
		m_sql = "select case when actionNo =120 then CONCAT('%s',substring((1000+actionNo),2))  when actionNo <> 120 then  CONCAT('%s',substring((1000+actionNo),2))  end actionNo " %(m_lastDate,m_date2)
	elif(type == 12):#老后台显示是错误的
		m_sql = "select case when actionNo >=42 then CONCAT('%s',substring((1000+actionNo),2))  when actionNo < 42 then  CONCAT('%s',substring((1000+actionNo),2))  end actionNo " %(m_lastDate,m_date2)
	elif(type == 60):#老后台显示是错误的
		#m_date2 = m_date2.substr(2)
		m_sql = "select CONCAT('%s',substring((1000+actionNo),2)) actionNo" %(m_date2)
	elif(type == 61 or type == 62 or type == 75 or type == 76):
		m_sql = "select CONCAT('%s-',substring((10000+actionNo),2)) actionNo" %(m_date2)
	elif(type == 5):
		m_sql = "select CONCAT('%s-',substring((10000+actionNo),2)) actionNo" %(m_date2)	
	elif(type == 14 or type == 26):
		m_sql = "select CONCAT('%s-',substring((10000+actionNo),2)) actionNo" %(m_date2)	
	elif(type == 6 or type == 7 or type == 15):
		#m_date2 = m_date2[2:]
		m_sql = "select CONCAT('%s',substring((100+actionNo),2)) actionNo" %(m_date2)
	elif(type == 16):
		m_sql = "select CONCAT('%s',substring((100+actionNo),2)) actionNo" %(m_date2)
	elif(type == 67 or type == 68):
		m_sql = "select CONCAT('%s-',substring((10000+actionNo),2)) actionNo" %(m_date2)
	elif(type == 9 or type == 10):#需要确认期号生成规则
		timeStruct = time.strptime(m_date, "%Y-%m-%d")
		strTime = time.strftime("%Y-%j", timeStruct).split("-")
		if diff > 0:
			m_sql = "select CONCAT('%s',substring((1000+%s),2)-7) actionNo" %(strTime[0],int(strTime[1]))
		else:
			m_sql = "select CONCAT('%s',substring((1000+%s),2)) actionNo" %(strTime[0],int(strTime[1]))
	#江苏快3
	elif(type == 79):
		m_sql = "select CONCAT('%s',substring((1000+actionNo),2)) actionNo" %(m_date2)
	#系统快3
	elif(type == 63 or type == 64):
		m_sql = "select CONCAT('%s-',substring((10000+actionNo),2)) actionNo" %(m_date2)
	elif(type == 20):
		timeStruct = time.strptime(m_date, "%Y-%m-%d") 
		timeStamp = int(time.mktime(timeStruct))
		timeStruct = time.strptime("2007-11-11", "%Y-%m-%d")
		timeStamp2 = int(time.mktime(timeStruct))
		m_actionNo = 44*(timeStamp - timeStamp2)/3600/24
		m_sql = "select (%s + actionNo +548551) actionNo" %(m_actionNo)
	elif(type == 65):
		m_sql = "select CONCAT('%s-',substring((10000+actionNo),2)) actionNo" % (m_date2)
		# timeStruct = time.strptime(m_date, "%Y-%m-%d")
		# timeStamp = int(time.mktime(timeStruct))
		# timeStruct = time.strptime("2007-11-11", "%Y-%m-%d")
		# timeStamp2 = int(time.mktime(timeStruct))
		# m_actionNo = 288*(timeStamp - timeStamp2)/3600/24
		# m_sql = "select (%s + actionNo - 6789) actionNo" %(m_actionNo)
	elif(type == 66):
		m_sql = "select CONCAT('%s-',substring((10000+actionNo),2)) actionNo" % (m_date2)
		# timeStruct = time.strptime(m_date, "%Y-%m-%d")
		# timeStamp = int(time.mktime(timeStruct))
		# timeStruct = time.strptime("2007-11-11", "%Y-%m-%d")
		# timeStamp2 = int(time.mktime(timeStruct))
		# m_actionNo = 288*(timeStamp - timeStamp2)/3600/24
		# m_sql = "select (%s + actionNo - 4321) actionNo" %(m_actionNo)
	elif(type == 78):
		timeStruct = time.strptime(m_date, "%Y-%m-%d") 
		timeStamp = int(time.mktime(timeStruct))
		timeStruct = time.strptime("2004-09-19", "%Y-%m-%d")
		timeStamp2 = int(time.mktime(timeStruct))
		m_actionNo = 179*(timeStamp - timeStamp2)/3600/24
		m_sql = "select (%s + actionNo - 3837-724-1300+47) actionNo" %(m_actionNo)
	elif(type == 73):
		m_sql = "select CONCAT('%s-',substring((10000+actionNo),2)) actionNo" % (m_date2)
		# timeStruct = time.strptime(m_date, "%Y-%m-%d")
		# timeStamp = int(time.mktime(timeStruct))
		# timeStruct = time.strptime("2004-09-19", "%Y-%m-%d")
		# timeStamp2 = int(time.mktime(timeStruct))
		# m_actionNo = 288*(timeStamp - timeStamp2)/3600/24
		# m_sql = "select (%s + actionNo - 1234) actionNo" %(m_actionNo)
	elif(type == 74):
		m_sql = "select CONCAT('%s-',substring((10000+actionNo),2)) actionNo" % (m_date2)
		# timeStruct = time.strptime(m_date, "%Y-%m-%d")
		# timeStamp = int(time.mktime(timeStruct))
		# timeStruct = time.strptime("2004-09-19", "%Y-%m-%d")
		# timeStamp2 = int(time.mktime(timeStruct))
		# m_actionNo = 288*(timeStamp - timeStamp2)/3600/24
		# m_sql = "select (%s + actionNo - 4567) actionNo" %(m_actionNo)
	elif(type == 71 or type == 72):
		m_sql = "select CONCAT('%s-',substring((10000+actionNo),2)) actionNo" %(m_date2)	
	elif(type == 77 or type == 70 or type == 69 ):#69,70管理后台没有
		m_sql = "select CONCAT('%s-',substring((10000+actionNo),2)) actionNo" %(m_date2)	
	elif(type == 34 ):
		m_date2 = time.strftime("%Y%m%d", m_timeStruct)
		m_sql = "select CONCAT('%s-',substring((10000+actionNo),2)) actionNo" %(m_date2)
	elif (type == 80):
		m_sql = "select CONCAT('%s-',substring((10000+actionNo),2)) actionNo" % (m_date2)
	elif (type == 81):
		m_sql = "select CONCAT('%s-',substring((10000+actionNo),2)) actionNo" % (m_date2)
	return m_sql
