#! /usr/bin/env python
# -*- coding:utf-8 -*-


import threading
import socket
import cPickle as pickle

BUFFER = 100


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockUDP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
host = raw_input("Server hostname or ip? ")
port = input("Server port? ")
addr = (host,port)
addrudp = (host,port)

sock.connect(addr)
#sockUDP.bind(addrudp)

print sock.recv(BUFFER)
sock.send('OK')

sockUDP.sendto('b4', addrudp)
m, a_ = sockUDP.recvfrom(BUFFER)
print m

print "UDP rec from : ", a_
print "UDP send to : ", addrudp

sockUDP.sendto('OK', addrudp)


print sock.recv(BUFFER)
sock.send('OK')

print "TCP addr ", addr
print "UDP addr ", addrudp

a = 1
while True:
  if a == 1:
    print "Send (TCP)"
    data = raw_input("message: ")
    sock.send(data)
    s = sock.recv(BUFFER)
    print "response (TCP): ", s
    a = 2
  if a == 2:
    print "Send (UDP)"
    data = raw_input("message: ")
    sockUDP.sendto(data, addrudp)
    msg, ad = sockUDP.recvfrom(BUFFER)
    print "response (UDP): ", msg
    a = 1
