#!/usr/bin/env python3
import socket
import sys
import re
import ssl

def url(URL):
	temp = ""
	path = ""
	hostname = ""
	ssl = ""
	temp = re.match("(\w+)://", URL)
	if temp:
		ssl = temp[0]
	temp = re.match("://([\w\-\.]+)", URL)
	if temp:
		hostname = temp[0]
	temp = re.match("\w(/.*|$)", URL)
	if temp:
		path = temp[0]
	return (ssl, hostname, path)

URL = sys.argv[1]
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

while True:
	ssl, hostname, path = url(URL)
	
	if ssl == "https":
		s.connect((hostname,443))
		s=ssl.wrap_socket(s)
	else:
		s.connect((hostname,80))

	f=s.makefile("rwb")
	f.write(f"GET {path} HTTP/1.1\r\n".encode("ASCII"))
	f.write(f"Host: {hostname} \r\n".encode("ASCII"))
	f.write(("Accept-charset: UTF-8\r\n\r\n").encode("ASCII"))
	f.flush()

	first_line = f.readline().decode("ASCII")
	first_line = first_line.strip()
	first_line = first_line.split(" ")

	status = first_line[1]
	popis = first_line[2]

	headre = {}
	
	while True:
		header = f.readline.decode("ASCII")
		dict = header.split(": ")
		headre[dict[0].lower()] = dict[1].lower()

	if status == "200":
		break

	elif status == ("301" or "302" or "303" or "307" or "308"):
		(ssl, hostname, path) = url(headre["location"])
		f.close()
	else:
		sys.stderr.write(status + popis)
		f.close()
		sys.exit(1)
		break

for i in headre.keys():
	if i == "content-length":
		length = int(headre["content-length"])
		obsah = f.read(length)
		sys.stdout.buffer.write(obsah)
		break

	elif i == "transfer-encoding":
		while True:
			length = f.readline().decode("ASCII")
			length = int(length, 16)
			chunk = f.read(length)
			sys.stdout.buffer.write(chunk)
			if not chunk:
				break
			f.readline()
		break

f.flush()
f.close()
s.close()
sys.exit(0)