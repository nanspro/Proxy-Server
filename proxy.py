import thread,socket,sys,os,time


def proxy(c, client):
	data = c.recv(1024)
	fl = data.split('\n')[0]
	url = fl.split(' ')[1]

	pos = url.find("://")
	if (pos == -1):
		tmp = url
	else:
		tmp = url[(pos+3):]

	web_pos = tmp.find("/")
	if (web_pos == -1):
		web_pos = len(tmp)

	content = tmp[(web_pos+1):]
	port_pos = tmp.find(':')

	server = ""
	port = 0
	if (port_pos==-1 or web_pos<port_pos):
		port = 80
		server = tmp[:web_pos]
	else:
		port = int((tmp[(port_pos+1):])[:web_pos-port_pos-1])
		server = tmp[:port_pos]
		# print(port)
		# print(server)

	req = "GET " + tmp[web_pos:] + " HTTP/1.1\r\n"
	data = req+"\r\n"

	if not os.path.exists('CACHE'):
		os.makedirs('CACHE')
	file_list = os.listdir('CACHE')
	number = len(file_list)
	# print(number)
	file = tmp[(web_pos+1):]
	filepath = "./CACHE/"+file
	sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	sock.connect((server,port))

	if file in file_list:
		t = time.ctime(os.path.getmtime(filepath))
		fd = req + "If-Modified-Since: " + t + "\r\n\r\n"
		sock.send(fd)
		cnt = 0
		while 1:
			x = sock.recv(1024)
			if cnt==0:
				status = x.split(' ')[1]
				# print(status)
			if not x:
				break
			cnt = cnt+1

		if status==304:
			with open(filepath) as f:
				# print("hi")
				while 1:
					text = f.read(1024)
					if not text:
						break
					c.send(text)
				f.close()
			c.close()
		
		else:
			fw = open(filepath,"w")
			with open(file) as f:
				while 1:
					text = f.read(1024)
					if not text:
						break
					fw.write(text)
					c.send(text)
				f.close()
			fw.close()
			c.close()


	else:
		# print(number)
		if number==3:
			all_files = sorted(os.listdir('CACHE'), key=os.path.getctime)
			oldest = all_files[-1]
			os.remove('./CACHE/'+oldest)

		try:
			# print("1")
			sock.send(data) 				
			# while 1:
			fo = open(filepath,"a")

			while 1:
				buf = sock.recv(1024)
				if buf:
					fo.write(buf)
					c.send(buf)
				else:
					break

			sock.close()
			# conn.close()
			c.close()
		except socket.error, (value, message):
			if sock:
				sock.close()
			# if conn:
				# conn.close()
			if c:
				c.close()
			print("Error: ",message)
			sys.exit(1)


def main():

	if (len(sys.argv) < 2):
		print ("Error: Enter port number")
		return sys.stdout

	host = ''
	port = int(sys.argv[1])

	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.bind((host,port))
		sock.listen(10)
	except socket.error, (value, message):
		if sock:
			sock.close()
		print("Unable to open socket: ", message)
		sys.exit(1)

	while 1:
		c, client = sock.accept()
		thread.start_new_thread(proxy, (c,client))

	sock.close()

if __name__ == '__main__':
	main()



