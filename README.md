# LARENE
Game for the Network project

![LARENE](https://raw.githubusercontent.com/Romain-B/LARENE/master/img/Larene.png)

## For the local version
Just go to the folder in terminal and execute `python LARENE.py`

## For the network TCP only test
Choose a machine to host the server.
note its ip address (you can get it by typing `ifconfig` in a terminal of a linux distribution.
launch the server : `python server_test.py`

On another terminal (or machine) modify the ip address in code (around line LARENE_networktest2.py) of the connection to match the server's address.
launch the 2 clients (on either 2 terminals or 2 machines) with `python LARENE_networktest2.py`

## Practical info
* The keybinds for all players (in local mode) are in keybinds.config. For network mode, keybinds are taken from p1 keybinds.
* The levels are defined by giving a list of  `[platform_width, platform_height, topleft_x, topleft_y]` in the levels.config file, followed by a list of 4 `[x, y]` for the spawns.

## Misc.
Music was royalty free and taken from (https://freesound.org/people/FoolBoyMedia/sounds/237089/)
Most sound effects came from the same source.
