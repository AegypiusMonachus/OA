import json,time,random

'''
tenantid ：租户号
uid		 ：会员id
type	 ：生成的类型 1：入款，2出款，3：优惠，4：游戏投注
playedid ：游戏类型id，只有type等于4的时候使用
'''
def createOrderId(tenantid,uid,type,playedid):
# 	if playedid is None:
# 		playedid = 0;
	currentTime= int(time.time());
	orderid= str(uid) + str(currentTime) + "{0:04d}".format(random.randint(0,9999))
	return orderid

def createOrderIdNew(uid):
# 	if playedid is None:
# 		playedid = 0;
	currentTime= int(time.time());
	orderid= str(uid) + str(currentTime) +  "{0:04d}".format(random.randint(0,9999))
	return orderid

def createECOrderId(uid):
# 	if playedid is None:
# 		playedid = 0;
	currentTime= int(time.time());
	orderid= str(uid) + str(currentTime) +  "{0:04d}".format(random.randint(0,9999))
	return orderid
