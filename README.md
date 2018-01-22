# LARENE
Game for the Network project

![LARENE](https://raw.githubusercontent.com/Romain-B/LARENE/master/img/Larene.png)

## For the local version
Just go to the folder in terminal and execute `python LARENE.py`

## For UDP / TCP Network Multiplayer backup project (screen & sound only on server)
Choose a machine to host the server on which you launch `python save_LARENE.py` and select the number of players with arrow keys and <ENTER>.
The server IP (localhost of the machine by default) and port (12345 by default) will be announced on screen.

<img src="https://raw.githubusercontent.com/Romain-B/LARENE/master/img/server_wait.png" width="400">

Each player on their own machine then launches `python save_game_client.py` (one can be on the server but the small window made by the client will need to be on foreground).
When everyone is connected, player selection occurs (by player number order) and game starts !

**Note :** For those in the BIMcave (you know who you are). You must set the `IN_BIMCAVE` variable to `True` in `save_LARENE.py`(The command used in the script to get the local ip for the server is different from typical machines).

**Note 2 :** If you get an error like the following :`pygame.error: No available audio device`, set the `SOUND` variable to `False` in `save_LARENE.py`. It's regrettable but you'll play with no sound. You can also use this variable to mute the game even if you do have an audio output.


## Practical info
* The **keybinds** for all players (in local mode) are in keybinds.config. For network mode, keybinds are taken from p1 keybinds.
* The levels are defined by giving a list of  `[platform_width, platform_height, topleft_x, topleft_y]` in the levels.config file, followed by a list of 4 `[x, y]` for the spawns. (feel free to make your own !)

## Misc.
Music was royalty free and taken from (https://freesound.org/people/FoolBoyMedia/sounds/237089/)
Most sound effects came from the same source.


## Old/obsolete stuff
### --OBSOLETE-- For the network TCP only test
Choose a machine to host the server.
note its ip address (you can get it by typing `ifconfig` in a terminal of a linux distribution.
launch the server : `python server_test.py`
On another terminal (or machine) modify the ip address in code (around line LARENE_networktest2.py) of the connection to match the server's address.
launch the 2 clients (on either 2 terminals or 2 machines) with `python LARENE_networktest2.py`
