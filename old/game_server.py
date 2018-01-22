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
    self.player_UDPdata = [None]*self.nb_players
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
        client.send(str(i+1)+','+str(self.nb_players)+','+str(self.address[1]+i))


        #UDP CONNECTION
        ping, UDPaddr = s.recvfrom(BUFFER)
        s.sendto('OK', UDPaddr)
        
        #SAVE CLIENT
        self.clients.append((client, s, UDPaddr))
        i+=1

   
      
      for i in range(self.nb_players):
        threading.Thread(target= self.TCP_handler, args = (self.clients[i][0], i+1)).start()
        threading.Thread(target= self.UDP_handler, args = (self.clients[i][1], self.clients[i][2], i+1)).start()

      self.TCP_broadcast("Go")
      self.start_level()
      threading.Thread(target= self.gameloop, args=()).start()
      #self.char_select()
      #self.launch()

    except error as e:
      for c in self.clients:
        c[0].close()
        c[1].close()
      
      self.sock.close()
      raise e
      sys.exit()

  def gameloop(self):
    while True:

      #Data send back to all clients
      data = self.player_UDPdata
      evts = self.events

      #Reset event array since events will be sent now
      self.events = []
      evts_string = [str(evts[i])+',' for i in range(self.nb_players)]
      evts_string = str(evts_string[:-1])


      tosend = str(time.time())+';'+evts_string+';'+str(randint(0, NB_SPAWNS))+';'
      self.UDP_broadcast(tosend)
      


  def start_level(self):
    level_num = randint(0, NB_LEVELS-1)
    spawns = [randint(0, NB_SPAWNS-1) for _ in range(self.nb_players)]

    data = str(level_num)

    for s in spawns:
      data += ','+str(s)

    self.TCP_broadcast(data)
    self.lvl_done = False



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
    while not self.stop:
      data, a = UDPsock.recvfrom(BUFFER)
      data = data.split(';')
      p_id = int(data[0])

      print p_id, data

      self.events[p_id-1] = data[1]
      #self.player_UDPdata[p_id-1] = data[2:]

  
  def close(self):
    for c in self.clients:
        c[0].close()
        c[1].close()
    self.stop = True


if __name__ == '__main__':
  s = Server('', 12345,2)
  s.start_server()
