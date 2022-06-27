import socket

# Sends requests to the agent
class Manager: 
		
	def __init__(self):
		self.ip_agent   = "127.0.0.1"
		self.port_agent = 6000
		self.socket     = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	
	def send_request_to_agent(self):
		# The user inputs a command
		# We then send the request to the agent
		resquest = input() 
		self.socket.sendto(resquest.encode(), (self.ip_agent, self.port_agent))
	
	def receive_reponse_from_agent(self):
		# We receive the response
		data, _ = self.socket.recvfrom(1024)

		if data.decode() == "YO":
			print("Request is valid")
			data, _ = self.socket.recvfrom(1024)
			print(data.decode())
		else:
			print("Request is not valid")



# What Should Happen?
# The user inputs some kind of "keyword"
# This key word is encoded and sent to the agent
# The agent seraches the MIBS files and then concludes something
# This conclusion is sent to the manager.
# The conclusion is displayed on screen for the user to see.

manager = Manager()
manager.send_request_to_agent()
manager.receive_reponse_from_agent()