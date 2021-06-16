#!/usr/bin/env python3
import socket
import sys
import re
import ssl

URL = sys.argv[1]

def url(URL):
	temp = ""
	path = ""
	hostname = ""
	ssl_protocol = ""
	zvysok = ""
	temp = re.match("^htt(p|ps)", URL)
	if temp:
		temp = re.split("://",URL)
		ssl_protocol = temp[0]
		zvysok = temp[1]

	temp = zvysok.split("/", maxsplit = 1)
	hostname = temp[0]
	path = temp[1]

	return (ssl_protocol, hostname, path)

while True:
	ssl_protocol, hostname, path = url(URL)
	#print(ssl_protocol+"\n"+hostname+"\n"+path)
	
	s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	
	if (ssl_protocol == "") or (hostname == ""):
		sys.stderr.write("error")
		sys.exit(2)

	if ssl_protocol == "https":
		s.connect((hostname,443))
		s=ssl.wrap_socket(s)
	else:
		s.connect((hostname,80))

	f=s.makefile("rwb")
	f.write(f"GET /{path} HTTP/1.1\r\n".encode("ASCII"))
	f.write(f"Host:{hostname}\r\n".encode("ASCII"))
	f.write(("Accept-charset: UTF-8\r\n\r\n").encode("ASCII"))
	f.flush()

	first_line = f.readline().decode("ASCII")
	first_line = first_line.strip()
	first_line = first_line.split(" ")

	status = first_line[1]
	popis = first_line[2]

	headre = {}
	
	while True:
		header = f.readline().decode("ASCII")
		if not header:
			break
		if not ":" in header:
			break
		if header == "\r\n":
			break
		h = header.split(":",1)
		headre[h[0].lower()] = h[1].lower()
	
	if status == "200":
		break
	elif ("301") or ("302") or ("303") or ("307") or ("308") == status:
		if ("location" in headre.keys()):
			URL = headre["location"]
			f.close()
			s.close()
			sys.exit(1)
		else:
			f.close()
			s.close()
			sys.exit(1)
	else:
		sys.stderr.write(status + " " + popis + "\n")
		f.close()
		s.close()
		sys.exit(1)

for i in headre.keys():
	if i == "content-length":
		length = int(headre["content-length"])
		obsah = f.read(length)
		sys.stdout.buffer.write(obsah)
		break
		
	elif i == "transfer-encoding":
		while True:
			length = f.readline().decode("ASCII").strip()
			length = int(length, base = 16)
			chunk = f.read(length)
			sys.stdout.buffer.write(chunk)
			if not chunk:
				break
			f.readline()

f.close()
s.close()
sys.exit(1)
