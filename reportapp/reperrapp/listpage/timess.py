import pytz
import datetime

class timess():
 	#Reflects update statuses for the two servers
 	def __init__(self, uplay, servertype):
 		self.lists = {
 			"uploaded" : uplay,
 		}
 		self.servername = servertype
timezone = pytz.timezone("America/Chicago")

#below sets up two sample timess objects
# with upload times for each server

d1 = datetime.datetime(1999, 8, 12, 12, 32, 41)
d2 = datetime.datetime(1996, 8, 12, 12, 32, 41)
d3 = datetime.datetime(2004, 8, 12, 12, 32, 41)

d1a = timezone.localize(d1)
d2a = timezone.localize(d2)
d3a = timezone.localize(d3)

p1 = datetime.datetime(1997, 8, 12, 12, 32, 41)
p2 = datetime.datetime(2002, 8, 12, 12, 32, 41)
p3 = datetime.datetime(2006, 8, 12, 12, 32, 41)
p4 = datetime.datetime(1992, 8, 12, 12, 32, 41)

p1a = timezone.localize(p1)
p2a = timezone.localize(p2)
p3a = timezone.localize(p3)
p4a = timezone.localize(p4)

duplay = [
	("mvol/0004/1905/0130", d1a),
	("mvol/0004/1920/0624", d2a),
	("mvol/0004/1930/0311", d3a),
]

dtimess = timess(duplay, "development")

puplay = [
	("mvol/0004/1905/0404", p1a),
	("mvol/0004/1920/1202", p2a),
	("mvol/0004/1930/0812", p3a),
	("mvol/0004/1930/1001", p4a),
]

ptimess = timess(puplay, "production")