from socket import *
import sys
import time
import os
import os.path
from os import path
from datetime import datetime
import signal


if len(sys.argv) <= 1:
	print('Usage : "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address Of Proxy Server')
	sys.exit(2)

# Create a server socket
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

#if port specified, use it
if len(sys.argv) >= 3:
	tcpSerSock.bind((sys.argv[1], int(sys.argv[2])))

#if no port specified, default to 8888
else:
	tcpSerSock.bind((sys.argv[1], 8888))

# become a server socket
tcpSerSock.listen()

while 1:
	print('Ready to serve...')
	tcpCliSock, addr = tcpSerSock.accept()
	print("Received a connection from:" + str(addr))
	message = tcpCliSock.recv(1024).decode('utf-8')

	#this catch/if statement is to prevent errors when browsers send an empty message, which
	#I've noticed some browsers do periodically
	if message != "":

		#split up the client request
		parts = message.split()

		#GET and POST requests supported
		request_type = parts[0]

		filename = message.split()[1].partition("/")[2]


		#clean up the request a bit
		filename =  filename.replace("http://","",1)
		filename = filename.replace("www.", "", 1)
		if filename[len(filename)-1] == "/":
			filename = filename[:-1]
		if "/" not in filename:		
				filename = filename + "/default"

		# commented out line below would be a pretty big security flaw
		# filename =  filename.replace("https://","",1)

		#check if there is an if-modified parameter in the request
		#and if the file already exists
		if os.path.exists(filename):
			date = ""
			index = message.index("If-Modified-Since")
			for char in message[index+len("If-Modified-Since")+1:]:
				date += char
				if char == "\r" or char == "\n":
					break

			date = date[:-1]			
			date = date.lstrip()
			#the value of the date in the if-modified-since header
			# date = datetime.strptime(date, '%a, %d %b %Y %H:%M:%S GMT')
			# date = date.timestamp()


			hostn = filename.replace("www.","",1)
			hostn = filename.replace("http://","",1)

			slash_index = hostn.find("/")

			c = socket(AF_INET, SOCK_STREAM)

			if slash_index != -1:
				connect_domain = hostn[0:slash_index]
			else:
				connect_domain = hostn

			#connect to server
			c.connect((connect_domain, 80))

			print("the value of the date here is" + str(date))
			if request_type == "GET":
				req_string = "GET "+ "http://"   +  filename + " HTTP/1.0\r\n" + "If-Modified-Since: " + str(date) + "\r\n\r\n"

			#POST request if POST request sent by client
			elif request_type == "POST":
				modified_body = message.split()[1][1:]
				req_string = "POST " + "http://" + modified_body + " HTTP/1.0" + "\r\n\r\n"

			#send request to server
			c.send(req_string.encode('utf-8'))
			time.sleep(0.01)
			

			data = c.recv(1024)
			data_string = data.decode("utf-8")
			data_array = data_string.split("\r\n")
			first_line = data_array[0]


			#this means we can just send over the cached file
			if "304 Not Modified" in first_line:
					filetouse = "/" + filename
					f = open(filetouse[1:], "r")
					fileExist = "true"

					#read in the cached file
					with open(filetouse[1:], mode='rb') as file:
							byte = file.read(1024)
							
							#send cached file to client
							while(byte):
								tcpCliSock.send(byte)
								byte = file.read(1024)

					#close socket
					tcpCliSock.close()

			elif "200 OK" in first_line:
				while len(data) >= 3:
					#send the data over to the client
					tcpCliSock.sendall(data)

					#some formatting
					if "/" in filename:
						index = filename.find("/")
						foldername = filename[0:index]
						foldername = foldername
						if not os.path.isdir(foldername):
								try:
										os.makedirs(foldername, 0o700)
								except OSError as e:
										print(e)

						tmpFile = open(filename,"ab+")
						tmpFile.write(data)
						data = c.recv(1024)

					else:
						if not os.path.isdir(filename):
							try:
								os.makedirs(filename, 0o700)
							except OSError as e:
									print(e)
						print("we are here")
						#i.e. they just entered vockz.org
						#first, check to see if a directory with that name exists
						file_string = filename + "/default"
						tmpFile = open(filename + "/default","ab+")
						tmpFile.write(data)
						data = c.recv(1024)




				
					#finish up writing last chunk of data to file and close socket
					if "/" in filename:
						tmpFile = open(filename,"ab+")
						tmpFile.write(data)
						tcpCliSock.close()
					else:
						tmpFile = open(filename + "/default","ab+")
						tmpFile.write(data)
						# c.sendall(data)
						tcpCliSock.close()



			# #account for cases like example.com without any filename (i.e. index.html)
			# if "/" not in filename:		
			# 	cached_file = filename + "/default"
			# else:
			# 	cached_file = filename
			
			# #now, check the date that the file we have cached
			# #was last modified

			# #lots of parsing here to make sure we're reading from the header, etc. etc.
			# #could probably be done with less code if I were to import an outside library
			# i = 0
			# with open (cached_file, "r") as myfile:
			# 	i += 1
			# 	text = myfile.readlines()
			
			# value = 0
			# for i in range(len(text)):
			# 	if text[i] == "\n":
			# 		value = i
			# 		break

			# for i in range(0, value):
			# 	if "Last-Modified" in text[i]:
			# 		line = text[i]
			# 		index = line.find(":")
			# 		modified_date = line[index+2:].rstrip()

			# last_modified = datetime.strptime(modified_date, "%a, %d %b %Y %H:%M:%S GMT")
			# last_modified = last_modified.timestamp()
				


			#in this case we don't need to even ask the server for a response
			#because we know that the file hasn't been modified since the requested
			#date
			# if date > last_modified:

			# 	last_modified = datetime.fromtimestamp(last_modified)
			# 	last_modified = last_modified.strftime('%a, %d %b %Y %H:%M:%S GMT')


				
			
			# 	print("DONT NEED TO RESEND")
			# 	tcpCliSock.sendall(str.encode("HTTP/1.0 304 NOT MODIFIED \n",'utf-8'))
			# 	tcpCliSock.sendall(str.encode('Content-Type: text/html\n', 'utf-8'))
			# 	tcpCliSock.sendall(str.encode("Last-Modified: " + last_modified + "\n"))
			# 	tcpCliSock.sendall(str.encode('\n'))
			# 	tcpCliSock.close()
			# 	continue

			# #in this case, we need to ask the server
			# #if the file has been modified since the requested  data
			# else:
			# 	hostn = filename.replace("www.","",1)
			# 	hostn = filename.replace("http://","",1)

			# 	slash_index = hostn.find("/")
			# 	if slash_index != -1:
			# 		connect_domain = hostn[0:slash_index]
			# 	else:
			# 		connect_domain = hostn
			# 	#connect to server on port 80
			# 	c.connect((connect_domain, 80))
			# 	print("NEED TO RESEND")


		fileExist = "false"
		filetouse = "/" + filename

		try:
			# Check wether the file exist in the cache
			f = open(filetouse[1:], "r")
			fileExist = "true"

			#if we've made it here, file exists since error not thrown
			#I kept this because of the skeleton code but if I wrote this
			#from scratch I'd probably just check if the file exists already

			#read in the cached file
			with open(filetouse[1:], mode='rb') as file:
					byte = file.read(1024)
					
					#send cached file to client
					while(byte):
						tcpCliSock.send(byte)
						byte = file.read(1024)

			#close socket
			tcpCliSock.close()



		# Error handling for file not found in cache
		except IOError:
			if fileExist == "false":
			# Create a socket on the proxyserver
				c = socket(AF_INET, SOCK_STREAM) 
				
				hostn = filename.replace("www.","",1)
				hostn = filename.replace("http://","",1)
				
				try:
					#do some formatting to account for
					#case when something like "example.com" (without /index.html)
					#is specified in url
					slash_index = hostn.find("/")
					if slash_index != -1:
						connect_domain = hostn[0:slash_index]
					else:
						connect_domain = hostn

					#connect on port 80
					c.connect((connect_domain, 80))


					#GET request if GET request sent by client
					if request_type == "GET":
						req_string = "GET "+ "http://"   +  filename + " HTTP/1.0" + "\r\n\r\n"


					#POST request if POST request sent by client
					elif request_type == "POST":
						modified_body = message.split()[1][1:]
						req_string = "POST " + "http://" + modified_body + " HTTP/1.0" + "\r\n\r\n"


					#send the request string over to the host/server
					c.send(req_string.encode('utf-8'))
					time.sleep(0.01)
					

					data = c.recv(1024)
					data_string = data.decode("utf-8")
					data_array = data_string.split("\r\n")
					first_line = data_array[0]

					#if response is OK
					if "200 OK" in first_line:
					
						while len(data) >= 3:
							#send the data over to the client
							tcpCliSock.sendall(data)

							#some formatting
							if "/" in filename:
								index = filename.find("/")
								foldername = filename[0:index]
								foldername = foldername
								if not os.path.isdir(foldername):
										try:
												os.makedirs(foldername, 0o700)
										except OSError as e:
												print(e)

								tmpFile = open(filename,"ab+")
								tmpFile.write(data)
								data = c.recv(1024)

							else:
								if not os.path.isdir(filename):
									try:
										os.makedirs(filename, 0o700)
									except OSError as e:
											print(e)
								print("we are here")
								#i.e. they just entered vockz.org
								#first, check to see if a directory with that name exists
								file_string = filename + "/default"
								tmpFile = open(filename + "/default","ab+")
								tmpFile.write(data)
								data = c.recv(1024)




					
						#finish up writing last chunk of data to file and close socket
						if "/" in filename:
							tmpFile = open(filename,"ab+")
							tmpFile.write(data)
							tcpCliSock.close()
						else:
							tmpFile = open(filename + "/default","ab+")
							tmpFile.write(data)
							# c.sendall(data)
							tcpCliSock.close()


					#response was not 200 OK so just send it over
					#to the client and don't cache/save response
					else:
						tcpCliSock.sendall(data)
						tcpCliSock.close()




						
				#something bad happened - send this to the client
				except Exception as e:
					print("ERROR" + str(e))
					tcpCliSock.sendall(str.encode("HTTP/1.0 200 OK\n",'utf-8'))
					tcpCliSock.sendall(str.encode('Content-Type: text/html\n', 'utf-8'))
					tcpCliSock.sendall(str.encode('\n'))
					tcpCliSock.sendall(str.encode("<html>Error. <br> There was an error with the request. <br> Please check that you entered the URL correctly and note that this server implementation only supports single-depth html files. It does not support images or https requests.<html>"))
					tcpCliSock.close()
					continue




#https://stackoverflow.com/questions/1112343/how-do-i-capture-sigint-in-python	
#need this code to close out the server socket when the server is terminated			
def signal_handler(sig, frame):
	print('You pressed Ctrl+C!')
	#probably don't need this, since I think OS closes socket
	#automatically but figured I'd leave it here
	if tcpSerSock != None:
		tcpSerSock.close()
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.pause()