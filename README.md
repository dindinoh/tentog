Tentog
======

Description
======
irssilike cli client for tent.io written in Python, so if you want a gui-free way of using tent this one works. 

Dependencies
======
* python-tent-client
* python-urwid
* python-simplejson

Installation
======
* First clone this repo
* Then inside tentog folder clone python-tent-client, see http://www.github.com/longears/python-tent-client
  (or do it anyways you might please, but if you do not do this you need to fix this in tentog.py)
* Create a config folder, file and datastore folder.
1. mkdir -p ~/.config/tentog/data/posts/
2. edit ~/.config/tentog/config
3. add something like:
<pre> 
    [tentog]
    editor=yourfavoriteeditor
    entityUrl=https://YOURENTITY.tent.is
    keystore=/home/YOURUSERNAME/.config/tentog/keystore.js
    datastore=/home/YOURUSERNAME/.config/tentog/data/posts/
    debuglog=/home/YOURUSERNAME/tentog.log
</pre>

That _should_ be all!

Usage
======
python tentog.py

It should fix your keys as kestore.js if you haven't set them up using longears python-tent-client before. In that case copy them to the keystore specified in the config file. It will start fetching new posts in the background.

Keys in status window:
* u      : update status window
* TAB    : enter edit line
* right  : see more information in head bar about chosen post
* left	 : clean top bar from what right bar put there
 
In edit mode
* /follow https://tent.tent.is  : follow specified entity
* TAB    : stop editing
* <enter> post what you have written in edit line
