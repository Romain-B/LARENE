#! /usr/bin/env python
# -*- coding:utf-8 -*-


import threading
from socket import *
import time
import sys
import cPickle as pickle

BUFFER = 100

class Client(object):
  """Network managing object for LARENE"""
  def __init__(self, host, port):
    
    self.address = (host, port)

    self.TCPsock = socket(AF_INET, SOCK_STREAM)
    self.UDPsock = socket(AF_INET, SOCK_DGRAM)
    
    self.TCPsock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    self.UDPsock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    self.level_end = True       
    self.last_time = 0         #Last time indicated on packet (to ensure we only keep latest data)
    self.worldinfo = []
    self.server_worldinfo = [] #Player positions and lives
    self.event_info = []       #List of events (for sound cues mainly)

    try :
    #CONNECT TCP
      self.TCPsock.connect(self.address)
      ping = self.TCPsock.recv(BUFFER)
      self.TCPsock.send('OK')

    #GET BASIC INFO FROM SERVER (TCP for safety)
      basic_info = self.TCPsock.recv(BUFFER)
      basic_info = basic_info.split(',')
      self.UDPaddr = (host, int(basic_info[2]))

    #CONNECT UDP
      self.UDPsock.sendto('ping', self.UDPaddr)
      ping, a = self.UDPsock.recvfrom(BUFFER) 

    except error as e :
      raise e
      self.close()
      sys.exit()

    
    self.player_id = int(basic_info[0])
    self.nb_players = int(basic_info[1])

    #Wait for the other players
    Go = self.recv_TCP()


    #UDP data receiving thread
    threading.Thread(target=self.worldinfo_handler, args=()).start()


  #BASIC METHODS

  def send_TCP(self, data):
    self.TCPsock.send(data)

  def send_UDP(self, data):
    self.UDPsock.sendto(data, self.UDPaddr)


  def recv_TCP(self):
    data = self.TCPsock.recv(BUFFER)
    return data

  def recv_UDP(self):
    data, ad = self.UDPsock.recvfrom(BUFFER)
    return data


  # GAME RELATED METHODS

  def level_start(self):
    #TCP for safety
    data = self.recv_TCP()
    
    #data format : level_num, p1_spawn_nb, p2_spawn_nb, ...
    data = data.split(',')

    level_num = int(data[0])
    spawns = []
    for i in range(self.nb_players):
      spawns.append(int(data[i]))

    # To restart the main game loop data listener
    self.level_end = False 

    return [level_num, spawns]

  def worldinfo_handler(self):

    while True:
      if not self.level_end:
        data = self.recv_UDP()
        data = data.split(';')

        time = float(data[0])

        #If the packet is the latest data (UDP can send be received in wrong order)
        if time > self.last_time :
          self.last_time = time

          event_info = data[1].split(',')
          
          self.worldinfo = map(int, data[2].split(','))

          player_info = []

          # for i in range(self.nb_players):
          #   player_info.append(map(int, data[i+3].split(',')))

          self.server_worldinfo = player_info
          self.event_info = event_info
        else :
          self.send_TCP("lvl_done")


  def send_playerinfo(self, p_coord, p_lives, events):

    data = str(self.player_id)+';'+\
            events+';'+\
            str(p_coord[0])+','+str(p_coord[1])+';'+\
            str(p_lives)

    self.send_UDP(data)

  def send_playerinfo_naive(self, events):

    data = str(self.player_id)+';'+events

    self.send_UDP(data)





  def close(self):
    self.UDPsock.close()
    self.TCPsock.close()


if __name__ == '__main__':
  c = Client('', 12345)
