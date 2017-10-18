#! /usr/bin/env python
# -*- coding:utf-8 -*-


import threading
import socket
import sys
import cPickle as pickle
from random import randint

BUFFER = 100
NLEVELS = 3
NSPAWNS = 4


class Server(object):
  """docstring for Server"""
  def __init__(self, host, port):
    super(Server, self).__init__()
    self.host = host
    self.port = port
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    self.sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #self.sockUDP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.clients = []
    self.addresses = []
    self.kill = False
    # self.pnum = 2
    # self.client_info = [None for i in range(self.pnum)]

    # #ready client list
    # self.go = [0]*self.pnum


  def start_server(self):
    try:
      self.sock.bind((self.host, self.port))
      self.sockUDP.bind((self.host, self.port))
      self.sock.listen(5)

      # start_lvl = randint(0,NLEVELS-1)
      # spawns = [randint(0, NSPAWNS-1) for i in range(self.pnum)]

      i = 0
      while self.kill == False and i < 2:
        client, address = self.sock.accept()

        self.clients.append(client)


        # print "Connected with PLAYER "+str(l)+" at addr "+address[0]+":"+str(address[1])
        client.send("Connected as PLAYER "+str(i+1))
        print client.recv(BUFFER)

        msg, a = self.sockUDP.recvfrom(BUFFER)
        print msg

        addr = a
        self.addresses.append(addr)


        print "TCP addr ", address
        print "UDP addr ", addr

        self.sockUDP.sendto('UDPtest', addr)
        print 'sent'

        print "Waiting for recvfrom client"
        msg, a = self.sockUDP.recvfrom(BUFFER)

        print msg

        client.send("Second connection to test")
        print client.recv(BUFFER)

        i+=1

      #Listen loop
        
      
      for j in range(i):
        threading.Thread(target= self.TCP_handler, args = (self.clients[j], self.addresses[j],)).start()
        threading.Thread(target= self.UDP_handler, args = (self.clients[j], self.addresses[j],)).start()
      # while True:
      #   #If data from all players have been received
      #   if sum(self.go) == self.pnum:
      #     all_data = ''
      #     #Add_stuff if necessary
      #     level = str(randint(0,NLEVELS-1))
      #     for i in range(self.pnum):
      #       level += ','+str(randint(0,NSPAWNS-1))
      #     all_data += level
      #     #Send data
      #     for i in range(self.pnum):
      #       all_data+=';'+self.client_info[i]

      #     self.broadcast(all_data)
      #     #Reset the ready client list
      #     self.go = [0]*self.pnum


    except socket.error as e:
      for c in self.clients:
        c.close()
      self.kill = True
      self.sock.close()
      self.sockUDP.close()
      raise e
      sys.exit()




  def TCP_handler(self, client, addr):
    try :
      while self.kill == False:
        msg = client.recv(BUFFER)
        print "Received (TCP) : "+msg+" from ", addr
        client.send("Received : "+msg)

    except socket.error as e:
      raise e
      client.close()
      self.kill == True





  def UDP_handler(self, client, addr):
    try :
      while self.kill == False:
        msg, ad = self.sockUDP.recvfrom(BUFFER)
        print "Received (UDP) : "+msg+" from ", ad

        if ad == addr:
          self.sockUDP.sendto("Received (UDP) : "+msg, addr)


    except socket.error as e:
      raise e
      client.close()
      self.kill == True










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
