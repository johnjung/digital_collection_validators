import datetime

class multilist():
 	"""docstring for multilist"""
 	lists = {
 	"none" : [],
 	"ready" : [],
 	"queue" : [],
 	"valid" : [],
 	"invalid" : []
 	}

 	def __init__(self, nonay, reaay, queay, valay, invay):
 		self.lists["none"] =  nonay
 		self.lists["ready"] = reaay
 		self.lists["queue"] = queay
 		self.lists["valid"] = valay
 		self.lists["invalid"] = invay

nonay = [
	("mvol/0004/1905/0130", datetime.datetime(1998, 8, 12, 12, 32, 7)),
	("mvol/0004/1905/0404", datetime.datetime(1998, 8, 12, 12, 32, 7)),
	("mvol/0004/1920/1111", datetime.datetime(1998, 8, 12, 12, 32, 7)),
	("mvol/0004/1930/0812", datetime.datetime(1998, 8, 12, 12, 32, 7)),
]

reaay = [
	("mvol/0004/1905/0214", datetime.datetime(1998, 8, 12, 12, 32, 7)),
	("mvol/0004/1930/0311", datetime.datetime(1998, 8, 12, 12, 32, 7)),
	("mvol/0004/1930/1001", datetime.datetime(1998, 8, 12, 12, 32, 7)),
]

queay = [
	("mvol/0004/1905/0917", datetime.datetime(1998, 8, 12, 12, 32, 7)),
	("mvol/0004/1930/0712", datetime.datetime(1998, 8, 12, 12, 32, 7)),
]

valay = [
	("mvol/0004/1920/1202", datetime.datetime(1998, 8, 12, 12, 32, 7))
]

invay = [
	("mvol/0004/1920/0624", datetime.datetime(1998, 8, 12, 12, 32, 7))
]

exmultilist = multilist(nonay, reaay, queay, valay, invay)