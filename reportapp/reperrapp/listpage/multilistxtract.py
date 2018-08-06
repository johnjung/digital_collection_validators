import datetime
import argparse
import sys

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("req", help = "all, none, ready, queue, valid, invalid")
  parser.add_argument("target", help = "object to extract from")
  args = parser.parse_args()

  if not args.req in ('all', 'none', 'ready', 'queue', 'valid', 'invalid'):
  	sys.stderr.write("Request is invalid\n")

  dictio = eval(args.target).lists

  print("\n")

  if args.req == "all":
  	for dictent in dictio:
  		print("***" + dictent + "***")
  		if len(dictio[dictent]) > 0:
  			for i in dictio[dictent]:
  				print(i)
  			print("\n")
  		else:
  			print("Nothing here.\n")
  else:
  	print("***" + args.req + "***\n")
  	if len(dictio[args.req]) > 0:
  			for i in dictio[args.req]:
  				print(i)
  	else:
  		print("Nothing here.\n")


