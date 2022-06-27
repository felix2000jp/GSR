import socket
from table_school import *

# Listens to requests from managers
class Agent: 

	def __init__(self):
		self.ip_agent   = "127.0.0.1"
		self.port_agent = 6000
		self.socket     = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socket.bind((self.ip_agent, self.port_agent))
		
		# Manager info
		self.addr_manager = ()

		# We make an array of possible requests to track if the request is valid
		# We track the current request and have a flag to tell us if the request
		# is valid
		self.request_list  = ["GET", "PUT", "DEL"]
		self.request_curr  = "" 
		self.request_valid = False


	def receive_request_from_manager(self):
		data, self.addr_manager = self.socket.recvfrom(1024)
		self.request_curr = data.decode()

		if self.request_curr[0:3] in self.request_list:
			self.request_valid = True
			self.socket.sendto("YO".encode(), self.addr_manager)
		else:
			self.request_valid = False
			self.socket.sendto("NOT YO".encode(), self.addr_manager)


	def request_GET_TABLE(self):
		message = ""
		# Table 
		message += (f"TABLE {table_0['index']}\n")
		message += (f" --> ACCESS : {table_0['access']}\n")
		if table_0['access'] == 1:
			message += (f" --> LABEL  : {table_0['label']}\n")
			# Entries
			for entry in table_0["entries"]:
				message += (f" --> ENTRY {entry['index']}\n")
				message += (f"     --> ACCESS : {entry['access']}\n")
				if entry['access'] == 1:
					message += (f"     --> LABEL  : {entry['label']}\n")
					# Values
					for value in entry["values"]:
						message += (f"     --> VALUE {value['index']}\n")
						message += (f"         --> ACCESS : {value['access']}\n")
						if value['access'] == 1:
							message += (f"         --> LABEL  : {value['label']}\n")
							message += (f"         --> VALUE  : {value['value']}\n")
		self.socket.sendto(message.encode(), self.addr_manager)

agent = Agent()
agent.receive_request_from_manager()
agent.request_GET_TABLE()


# Add we need to specify what we are getting (TABLE, ENTRY, VALUE)
# Allow for PUT method
# Allow for DEL method