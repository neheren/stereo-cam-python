import os, platform, time
import shlex  
from latencyTester import averagePing, online
from subprocess import Popen, PIPE, STDOUT
import grequests
import asyncio
import GUI
# from runcoroutine import runCoroutine
_mayCheckConnections = True
def enableConnectionCheck(enable):
	mayCheckConnections = enable
def mayCheckConnection():
	return _mayCheckConnections

class Connection : # place this in another doc please..
	ip = ''
	port = ''
	ping = 0
	status = False
	serverUp = False
	reversedPing = 0
	def __init__ (self, _ip, _port):
		self.ip = _ip
		self.port = _port
	
	def updateConnection(self, accuracy):
		con = online(self.ip)
		print(self.ip)
		if(con != False) : # returning false if connection down, and the ping if up
			self.ping = con
			self.status = True
			print('Connection up for ' + self.ip + ' with ping: ' + str(self.ping))
			return True
		else : 
			self.status = False
			print('Connection could not be established to ' + self.ip)
			return False

def arePisConnected(cons, accuracy, loop = True):
	print('Trying to connect to slaves')
	for connection in cons :
		connection.updateConnection(accuracy)

def checkClientStatus(cons):
	ips = map(lambda con: con.ip + con.port + 'status', cons) # reversed pings instead of pings
	requests = (grequests.get(ip, timeout = 0.5) for ip in ips)
	responses = grequests.map(requests)
	for i in range(0, len(cons)):
		if(responses[i] != None and responses[i].status_code == 200):
			cons[i].serverUp = True
		else:
			cons[i].serverUp = False


def updateConnections(cons, eachSeconds):
	try:
		while 1: # Constantly check
			if(mayCheckConnection()): # if permitted
				arePisConnected(cons, 1, False) # that the pi's can be seen on the network.
				checkClientStatus(cons) # and that the slave servers are up and returning 200
				time.sleep(eachSeconds) # then wait for a while
			else: # if not permitted
				time.sleep(1) # check again in 1 sec.
	except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
		GPIO.cleanup() # cleanup all GPIO
		