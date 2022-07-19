from asyncio import current_task
import re
import socket

from click import option
from my_mib import *
from pysnmp.hlapi import *

# Listens to requests from managers
class Agent: 

	def __init__(self):
		self.ip_agent   = "127.0.0.1"
		self.port_agent = 6000
		self.socket     = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socket.bind((self.ip_agent, self.port_agent))
		
		# Manager info
		self.addr_manager = ()

		# Session information
		self.group   = ""
		self.idOper  = 0
		self.mib_sec = [{
			"OID"      : "The OID sequence",
			"group"    : "The group where the OID was located",
			"value"    : "The value stored in the table",
			"type"     : "The type of the value stored in the table",
			"size"     : "The size of the value stored in the table",
			"idOper"   : "Then identifier of the operation",
			"typeOper" : "The type of the operation done",
			"idSource" : "The IP from the source",
			"idDest"   : "The IP from the destination",
			# Maybe we will add more things to it later like port, type of operation...
		}]

		print("AGENT IS ON")

	def receive_group(self):
		data, self.addr_manager = self.socket.recvfrom(1024)
		self.group = data.decode()

	def receive_request(self):
		data, self.addr_manager = self.socket.recvfrom(1024)
		option = data.decode()

		if option == "1":
			self.request_GET()
			return 1
		elif option == "2":
			self.request_GET_NEXT()
			return 1
		elif option == "3":
			self.request_SET()
			return 1
		elif option == "4":
			self.receive_group()
			return 1
		elif option == "5":
			self.show_current_info()
			return 1
		elif option == "6":
			self.show_previous_and_current_info()
			return 1
		elif option == "0":
			return 0
		else:
			return 1


	def request_GET(self):
		data, self.addr_manager = self.socket.recvfrom(1024)
		oid_received = data.decode()

		# We first see if the OID is already loaded on the mib_sec
		# is_loaded = False
		# for obj in self.mib_sec:
		# 	if obj["OID"] == oid_received and obj["group"] == self.group:
		# 		is_loaded = True
		# 		break

		# if is_loaded:
		# 	message = f"OID {oid_received} has already been loaded into MIBsec successfully"
		# 	self.socket.sendto(message.encode(), self.addr_manager)
		# 	return

		# There is an error here
		# If we successfully load a certain OID and then we change the group
		# to something that does not exist and then try to load the same OID 
		# the program will not realise that the group is invalid because it never
		# talks to the snmp agent
		# EDIT: I solved this by adding a group key to every mib_sec object
		# I still need to check this out
		try:
			iterator = getCmd(
				SnmpEngine(),
				CommunityData(self.group),
				UdpTransportTarget(("localhost", 161)),
				ContextData(),
				ObjectType(ObjectIdentity(oid_received))
			)

			errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
			# This if else statement is only here to check for errors on the group 
			# This does not catch invalid OID errors (I don't know why)
			if errorIndication:
				message = str(errorIndication) + "\n"
				message += "This most likely happened due to an invalid group name\n"
				message += "Please verify both the group name and OID..."
				self.socket.sendto(message.encode(), self.addr_manager)
			elif errorStatus:
				message = str('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
				self.socket.sendto(message.encode(), self.addr_manager)
			else:
				# We first see if the OID is already loaded on the mib_sec
				for oid, varBind in varBinds:
					for obj in self.mib_sec:
						if obj["OID"] == str(oid) and obj["group"] == self.group:
							message = f"OID {str(oid)} has ALREADY BEEN loaded into MIBsec successfully"
							self.socket.sendto(message.encode(), self.addr_manager)
							return

					current_table = {
						"OID"      : "",
						"group"    : "",
						"value"    : "",
						"type"     : "",
						"size"     : "",
						"idOper"   : 0,
						"typeOper" : "",
						"idSource" : "",
						"idDest"   : "",
					}
					current_table["OID"]      = str(oid)
					current_table["group"]    = self.group
					current_table["value"]    = str(varBind)
					# Sem __name__ output é <class 'DisplayString'
					# Tenho de verificar este tipo, porquê DisplayString?
					current_table["type"]     = type(varBind).__name__
					current_table["size"]     = len(str(varBind))
					current_table["idOper"]   = self.idOper
					current_table["typeOper"] = "GET"
					current_table["idSource"] = self.addr_manager[0]
					current_table["idDest"]   = self.ip_agent

					self.idOper += 1
					self.mib_sec.append(current_table)
					message = f"OID {str(oid)} has been loaded into MIBsec successfully"

				self.socket.sendto(message.encode(), self.addr_manager)
				print(self.mib_sec)
		except Exception as e:
			message = "The following Exception has ocurred:\n"
			message += str(e) + "\n" 
			message += "This most likely happened due to an invalid OID\n"
			message += "Please verify both the group and OID..."
			self.socket.sendto(message.encode(), self.addr_manager)

	def request_GET_NEXT(self):
		data, self.addr_manager = self.socket.recvfrom(1024)
		oid_received = data.decode()

		# There is an error here
		# If we successfully load a certain OID and then we change the group
		# to something that does not exist and then try to load the same OID 
		# the program will not realise that the group is invalid because it never
		# talks to the snmp agent
		# EDIT: I solved this by adding a group key to every mib_sec object
		# I still need to check this out
		try:
			iterator = nextCmd(
				SnmpEngine(),
				CommunityData(self.group),
				UdpTransportTarget(("localhost", 161)),
				ContextData(),
				# 1.3.6.1.2.1.1.1.0
				# 1.3.6.1.2.1.1.6.0
				# 1.3.6.1.2.1.4.1.0
				ObjectType(ObjectIdentity(oid_received))
			)

			errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
			# This if else statement is only here to check for errors on the group 
			# This does not catch invalid OID errors (I don't know why)
			if errorIndication:
				message = str(errorIndication) + "\n"
				message += "This most likely happened due to an invalid group name\n"
				message += "Please verify both the group name and OID..."
				self.socket.sendto(message.encode(), self.addr_manager)
			elif errorStatus:
				message = str('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
				self.socket.sendto(message.encode(), self.addr_manager)
			else:
				for oid, varBind in varBinds:
					# We first see if the OID is already loaded on the mib_sec
					for obj in self.mib_sec:
						if obj["OID"] == str(oid) and obj["group"] == self.group:
							message = f"OID {str(oid)} has already been loaded into MIBsec successfully"
							self.socket.sendto(message.encode(), self.addr_manager)
							return

					current_table = {
						"OID"      : "",
						"group"    : "",
						"value"    : "",
						"type"     : "",
						"size"     : "",
						"idOper"   : 0,
						"typeOper" : "",
						"idSource" : "",
						"idDest"   : "",
					}
					current_table["OID"]      = str(oid)
					current_table["group"]    = self.group
					current_table["value"]    = str(varBind)
					# Sem __name__ output é <class 'DisplayString'
					# Tenho de verificar este tipo, porquê DisplayString?
					current_table["type"]     = type(varBind).__name__
					current_table["size"]     = len(str(varBind))
					current_table["idOper"]   = self.idOper
					current_table["typeOper"] = "GET_NEXT"
					current_table["idSource"] = self.addr_manager[0]
					current_table["idDest"]   = self.ip_agent

					self.idOper += 1
					self.mib_sec.append(current_table)
					message = f"OID {str(oid)} has been loaded into MIBsec successfully"

				self.socket.sendto(message.encode(), self.addr_manager)
				print(self.mib_sec)
		except Exception as e:
			message = "The following Exception has ocurred:\n"
			message += str(e) + "\n" 
			message += "This most likely happened due to an invalid OID\n"
			message += "Please verify both the group and OID..."
			self.socket.sendto(message.encode(), self.addr_manager)
	
	def request_SET(self):
		data, self.addr_manager = self.socket.recvfrom(1024)
		oid_received = data.decode()

		data, self.addr_manager = self.socket.recvfrom(1024)
		new_value = data.decode()

		try:
			iterator = setCmd(
				SnmpEngine(),
				CommunityData(self.group),
				UdpTransportTarget(("localhost", 161)),
				ContextData(),
				# 1.3.6.1.2.1.1.1.0
				# 1.3.6.1.2.1.1.6.0
				# 1.3.6.1.2.1.4.1.0
				ObjectType(ObjectIdentity(oid_received), new_value)
			)

			errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
			# This if else statement is only here to check for errors on the group 
			# This does not catch invalid OID errors (I don't know why)
			if errorIndication:
				message = str(errorIndication) + "\n"
				message += "This most likely happened due to an invalid group name\n"
				message += "Please verify both the group name and OID..."
				self.socket.sendto(message.encode(), self.addr_manager)
			elif errorStatus:
				message = str('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
				self.socket.sendto(message.encode(), self.addr_manager)
			else:
				for oid, varBind in varBinds:
					# We first see if the new value is the same as the current value
					reversed_mib_sec = self.mib_sec.copy()
					reversed_mib_sec.reverse()
					current_value = None
					for obj in reversed_mib_sec:
						if obj["OID"] == str(oid_received) and obj["group"] == self.group:
							current_value = obj['value']
							if new_value == current_value:
								message = f"OID {str(oid)} value is already set to {new_value}"
								self.socket.sendto(message.encode(), self.addr_manager)
								return
							break
					

					current_table = {
						"OID"      : "",
						"group"    : "",
						"value"    : "",
						"type"     : "",
						"size"     : "",
						"idOper"   : 0,
						"typeOper" : "",
						"idSource" : "",
						"idDest"   : "",
					}
					current_table["OID"]      = str(oid)
					current_table["group"]    = self.group
					current_table["value"]    = str(varBind)
					# Sem __name__ output é <class 'DisplayString'
					# Tenho de verificar este tipo, porquê DisplayString?
					current_table["type"]     = type(varBind).__name__
					current_table["size"]     = len(str(varBind))
					current_table["idOper"]   = self.idOper
					current_table["typeOper"] = "SET"
					current_table["idSource"] = self.addr_manager[0]
					current_table["idDest"]   = self.ip_agent

					self.idOper += 1
					self.mib_sec.append(current_table)
					message = f"OID {str(oid)} value has been changed successfully"

				self.socket.sendto(message.encode(), self.addr_manager)
				print(self.mib_sec)
		except Exception as e:
			message = "The following Exception has ocurred:\n"
			message += str(e) + "\n" 
			message += "This most likely happened due to an invalid OID\n"
			message += "Please verify both the group and OID..."
			self.socket.sendto(message.encode(), self.addr_manager)

	def show_current_info(self):
		data, self.addr_manager = self.socket.recvfrom(1024)
		oid_received = data.decode()

		reversed_mib_sec = self.mib_sec.copy()
		reversed_mib_sec.reverse()
		message = ""
		for obj in reversed_mib_sec:
			if obj["OID"] == str(oid_received) and obj["group"] == self.group:
				message += f"The value set to the OID {oid_received} is:\n{obj['value']}\n"
				break
		if message == "":
			message = f"Could not find OID {oid_received}"
		self.socket.sendto(message.encode(), self.addr_manager)
	
	def show_previous_and_current_info(self):
		data, self.addr_manager = self.socket.recvfrom(1024)
		oid_received = data.decode()

		message = f"This are the values that have been set to the OID {oid_received} ordered from oldest to newest\n"
		for obj in self.mib_sec:
			if obj["OID"] == str(oid_received) and obj["group"] == self.group:
				message += f"{obj['value']}\n"
		if message == f"This are the values that have been set to the OID {oid_received} ordered from oldest to newest\n":
			message = f"Could not find OID {oid_received}"
		self.socket.sendto(message.encode(), self.addr_manager)


is_running = 1
agent = Agent()
agent.receive_group()
while is_running == 1:
	is_running = agent.receive_request()



# Add we need to specify what we are getting (TABLE, ENTRY, VALUE)
# Allow for PUT method
# Allow for DEL method
