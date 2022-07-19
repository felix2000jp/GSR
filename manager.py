import socket

# Sends requests to the agent
class Manager: 
		
	def __init__(self):
		self.ip_agent   = "127.0.0.1"
		self.port_agent = 6000
		self.socket     = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		self.group_valid   = False
		self.request_valid = False

		# Session info
		self.option = ""


		print("MANAGER IS ON")

	def init_group(self):
		group = input("Please tell us what group should we use: ")
		self.socket.sendto(group.encode(), (self.ip_agent, self.port_agent))

	def main_menu(self):
		print()
		print("Welcome to the manager menu")
		print("1 - Make GET request")
		print("2 - Make GET NEXT request")
		print("3 - Make SET request")
		print("4 - Reset group")
		print("5 - OID current value info")
		print("6 - OID previous and current value info")
		print("0 - Exit")
		self.option = input("Please select an option: ")
		print()
		self.socket.sendto(self.option.encode(), (self.ip_agent, self.port_agent))

	def option_solve(self):
		if self.option == "1":
			self.send_OID()
			self.receive_message()
			return 1
		elif self.option == "2":
			self.send_OID()
			self.receive_message()
			return 1
		elif self.option == "3":
			self.send_OID()
			self.send_value()
			self.receive_message()
			return 1
		elif self.option == "4":
			self.init_group()
			return 1
		elif self.option == "5":
			self.send_OID()
			self.receive_message()
			return 1
		elif self.option == "6":
			self.send_OID()
			self.receive_message()
			return 1
		elif self.option == "0":
			return 0
		else:
			print("Invalid Option")
			return 1 
		

	def send_OID(self):
		oid_to_send = input("Please write an OID: ") 
		print()
		self.socket.sendto(oid_to_send.encode(), (self.ip_agent, self.port_agent))
	
	def send_value(self):
		oid_to_send = input("Please write the new value: ") 
		print()
		self.socket.sendto(oid_to_send.encode(), (self.ip_agent, self.port_agent))

	def receive_message(self):
		data, _ = self.socket.recvfrom(1024)
		print(data.decode())



# What Should Happen?
# The user inputs some kind of "keyword"
# This key word is encoded and sent to the agent
# The agent seraches the MIBS files and then concludes something
# This conclusion is sent to the manager.
# The conclusion is displayed on screen for the user to see.

is_running = 1
manager = Manager()
manager.init_group()
while is_running == 1:
	manager.main_menu()
	is_running = manager.option_solve()
