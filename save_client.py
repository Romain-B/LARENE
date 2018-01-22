#! /usr/bin/env python
# -*- coding:utf-8 -*-


import threading
from socket import *
import time
import sys
import cPickle as pickle
import json
import pygame
import re

BUFFER = 100
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


#Event codes
RESET_KEY = pygame.K_r
EXIT_KEY = pygame.K_ESCAPE

LEFT = 'l'
RIGHT = 'r'
LEFT_KUP = 'm'
RIGHT_KUP = 'n'

JUMP = 'j'
SHOOT = 's'
RESET = 'x'
QUIT = 'q'


class Client(object):
  """Network managing object for LARENE"""
  def __init__(self, host, port):
    
    self.address = (host, port)

    self.stop = False

    self.TCPsock = socket(AF_INET, SOCK_STREAM)
    self.UDPsock = socket(AF_INET, SOCK_DGRAM)
    
    self.TCPsock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    self.UDPsock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    self.level_end = True       
    self.last_time = 0          # Last time indicated on packet (to ensure we only keep latest data)

    self.keys = []

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
    #take 1st keybinds
    self.kb = load_keybinds('keybinds.config')[0]

    #Wait for the other players
    Go = self.recv_TCP()

    print "Connected as"
    print self.player_id

    self.gameloop()

    #UDP data receiving thread
    #self.t = threading.Thread(target=self.worldinfo_handler_naive, args=())
    #self.t.start()

    #Level end check thread
    #self.u = threading.Thread(target=self.level_end_check_naive, args=())
    #self.u.start()


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

  def gameloop(self):


    #Get display size of monitor
    #infoObject = pygame.display.Info()
    i = 0
    size = (200,200)#(int(infoObject.current_w/2), int(infoObject.current_h/2))
    final_screen = pygame.display.set_mode(size)
    pygame.display.set_caption("PLAYER "+str(self.player_id+1))
    font = pygame.font.SysFont('liberationsans', 20)
    final_screen.fill(BLACK)

    while not self.stop:

      evts = self.get_events()

      final_screen.fill(BLACK)
      textplay = font.render("P"+str(self.player_id+1), False, WHITE)
      final_screen.blit(pygame.transform.scale(textplay, (150, 150)), (25,25))
      pygame.display.flip()
      self.send_playerinfo_naive(evts)

    self.close()




  def get_events(self):
    events = ''
    ev = pygame.event.get()
    for event in ev:
      if event.type == pygame.QUIT:
        self.stop = True
      if event.type == pygame.KEYDOWN :
        if event.key == self.kb[1]:
          events += LEFT
            
        if event.key == self.kb[2]:
          events += RIGHT

        if event.key == self.kb[0]:
          events += JUMP
           
        if event.key == self.kb[3]:
          events += SHOOT
        
        if event.key == EXIT_KEY:
          events += QUIT 
        if event.key == RESET_KEY:
          events += RESET

      if event.type == pygame.KEYUP:
        if event.key == self.kb[1]:
          events += LEFT_KUP
        if event.key == self.kb[2]:
          events += RIGHT_KUP

    return events




  def send_playerinfo_naive(self, events):

    data = str(time.time())+';'+str(self.player_id)+';'+events
    self.send_UDP(data)


  def close(self):
    self.stop = True
    #self.t.join()
    #self.u.join()
    self.UDPsock.close()
    self.TCPsock.close()


def load_keybinds(filename):
    keybinds = []

    with open(filename, 'r') as f:
      lines = f.read().splitlines()

    i=0
    pat = re.compile("^P\d$")
    for i in range(len(lines)) :  
      if pat.match(lines[i]) :
        kb = []
        for j in range(1,5):
          kb.append(getattr(pygame, 'K_'+ lines[i+j].split(':')[1]))
        keybinds.append(kb)
    return keybinds
    


if __name__ == '__main__':
  pygame.init()

  ip = raw_input('IP du Server : ')
  port = int(raw_input('Port du Server : '))
  c = Client(ip, port)
  pygame.quit()
