#! /usr/bin/env python
# -*- coding:utf-8 -*-


import threading
from socket import *
import time
import sys
import cPickle as pickle
from random import randint

BUFFER = 100
NB_LEVELS = 3
NB_SPAWNS = 4

class Server(object):
  """Network server object for LARENE"""
  def __init__(self, host, port, nb_players):
    
    self.address = (host, port)
    self.nb_players = nb_players

    #Check if ports are available
    try :
      for i in range(self.nb_players):
        s = socket(AF_INET, SOCK_STREAM)
        s.bind((host, port+i))
        s.close()
    except error as e:
      print "ERROR, port "+str(port+i)+" is not available"
      raise e
      sys.exit()


    self.players = [None]*self.nb_players
    #self.player_UDPdata = [None]*self.nb_players
    self.events = ['']*self.nb_players

    self.TCPsock = socket(AF_INET, SOCK_STREAM)
    self.UDPsock = [socket(AF_INET, SOCK_DGRAM) for _ in range(self.nb_players)]
    
    self.TCPsock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    for s in self.UDPsock :
      s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) 


    self.clients = []
    self.lvl_done = False

    self.stop = False



  def start_server(self) :
    try:
      self.TCPsock.bind(self.address)
      self.TCPsock.listen(5)

      i = 0
      #WAIT FOR ALL TO CONNECT
      while i < self.nb_players:

        s = self.UDPsock[i]
        s.bind((self.address[0], self.address[1]+i))

        client, TCPaddr = self.TCPsock.accept()

        #TCP CONNECTION
        client.send('ping')
        ok = client.recv(BUFFER)


        #SEND BASIC_INFO (player_id, nb_players, UDPport)
        client.send(str(i)+','+str(self.nb_players)+','+str(self.address[1]+i))


        #UDP CONNECTION
        ping, UDPaddr = s.recvfrom(BUFFER)
        s.sendto('OK', UDPaddr)
        
        #SAVE CLIENT
        self.clients.append((client, s, UDPaddr))
        i+=1
        print "PLAYER "+str(i)+" CONNECTED !"

        self.TCPthreads = []
        self.UDPthreads = []
      
      for i in range(self.nb_players):
        t = threading.Thread(target= self.TCP_handler, args = (self.clients[i][0], i))
        t.start()
        self.TCPthreads.append(t)
        u = threading.Thread(target= self.UDP_handler, args = (self.clients[i][1], self.clients[i][2], i))
        u.start()
        self.UDPthreads.append(u)

      self.TCP_broadcast("Go")

    except error as e:
      for c in self.clients:
        c[0].close()
        c[1].close()
      
      self.sock.close()
      raise e
      sys.exit()
 


  def TCP_broadcast(self, data):
    for c in self.clients:
      c[0].send(data)

  def UDP_broadcast(self, data):
    i=0
    for c in self.clients:
      self.UDPsock[i].sendto(data, c[2])
      i+=1


  def TCP_handler(self, client, p_id):
    while not self.stop:
      data = client.recv(BUFFER)
      if data == "lvl_done" and self.lvl_done == False:
        self.start_level()
        self.lvl_done = True

      #dostuff

  def UDP_handler(self, UDPsock, UDPaddr, p_id):
    last_time = 0
    while not self.stop:
      data, a = UDPsock.recvfrom(BUFFER)
      data = data.split(';')
      time = float(data[0])
      p_id = int(data[1])

      # print p_id, data
      if time >= last_time:
        self.events[p_id] += data[2]
        last_time = time
      #self.player_UDPdata[p_id] = data[2:]

  
  def close(self):
    for c in self.clients:
        c[0].close()
        c[1].close()
    self.stop = True
    for t in self.TCPthreads:
      t.join()
    for u in self.UDPthreads:
      u.join()


if __name__ == '__main__':
  s = Server('', 12345,2)
  s.start_server()