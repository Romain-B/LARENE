#! /usr/bin/env python
# -*- coding:utf-8 -*-


import threading
import socket
import sys
import cPickle as pickle
from random import randint

BUFFER = 50
NLEVELS = 3
NSPAWNS = 4


class Server(object):
  """docstring for Server"""
  def __init__(self, host, port):
    super(Server, self).__init__()
    self.host = host
    self.port = port
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    self.clients = []
    self.pnum = 2
    self.client_info = [None for i in range(self.pnum)]

    #ready client list
    self.go = [0]*self.pnum


  def start_server(self):
    try:
      self.sock.bind((self.host, self.port))
      self.sock.listen(5)
      start_lvl = randint(0,NLEVELS-1)
      spawns = [randint(0, NSPAWNS-1) for i in range(self.pnum)]
      while len(self.clients) < self.pnum:
        client, address = self.sock.accept()
        self.clients.append(client)
        l = len(self.clients)
        print "Connected with PLAYER "+str(l)+" at addr "+address[0]+":"+str(address[1])
        client.send("Connected as PLAYER "+str(l))
        print client.recv(BUFFER)
        
        start_info = str(start_lvl)
        for i in range(self.pnum):
          start_info+=','+str(spawns[i])

        client.send(start_info)
      #ADD PLAYER CHARACTER SELECTION IN HERE


      #Game loop
        threading.Thread(target= self.player_handler, args = (client, l-1, )).start()

      while True:
        #If data from all players have been received
        if sum(self.go) == self.pnum:
          all_data = ''
          #Add_stuff if necessary
          level = str(randint(0,NLEVELS-1))
          for i in range(self.pnum):
            level += ','+str(randint(0,NSPAWNS-1))
          all_data += level
          #Send data
          for i in range(self.pnum):
            all_data+=';'+self.client_info[i]

          self.broadcast(all_data)
          #Reset the ready client list
          self.go = [0]*self.pnum


    except socket.error as e:
      for c in self.clients:
        c.close()
      self.sock.close()
      raise e
      sys.exit()

  def broadcast(self, data):
    for c in self.clients:
        c.send(data)

  def player_handler(self, client, c_num):
    while True:
      if self.go[c_num] == 0:
        data = client.recv(BUFFER)
        #print "received from "+str(c_num)+" data : "+data
        self.client_info[c_num] = data
        self.go[c_num] = 1
    client.close()



    
        
if __name__ == '__main__':
  port_num = 12345
  s = Server('', port_num)
  s.start_server()
