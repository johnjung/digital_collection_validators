import datetime
import pytz

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

d = datetime.datetime(1998, 8, 12, 12, 32, 41)
timezone = pytz.timezone("America/Chicago")
d_aware = timezone.localize(d)

nonay = [
	("mvol/0004/1905/0130", d_aware),
	("mvol/0004/1905/0404", d_aware),
	("mvol/0004/1920/1111", d_aware),
	("mvol/0004/1930/0812", d_aware),
]

reaay = [
	("mvol/0004/1905/0214", d_aware),
	("mvol/0004/1930/0311", d_aware),
	("mvol/0004/1930/1001", d_aware),
]

queay = [
	("mvol/0004/1905/0917", d_aware),
	("mvol/0004/1930/0712", d_aware),
]

valay = [
	("mvol/0004/1920/1202", d_aware)
]

invay = [
	("mvol/0004/1920/0624", d_aware)
]

yex = 0

for i in range (0, yex):
	nonay.append((("mvol/0004/1921/%s" % '{0:04}'.format(i)), d_aware))
for i in range (0, yex):
	reaay.append((("mvol/0004/1922/%s" % '{0:04}'.format(i)), d_aware))
for i in range (0, yex):
	queay.append((("mvol/0004/1923/%s" % '{0:04}'.format(i)), d_aware))
for i in range (0, yex):
	valay.append((("mvol/0004/1924/%s" % '{0:04}'.format(i)), d_aware))
for i in range (0, yex):
	invay.append((("mvol/0004/1925/%s" % '{0:04}'.format(i)), d_aware))				

exmultilist = multilist(nonay, reaay, queay, valay, invay)