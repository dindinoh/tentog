Tentog
======

Description
======
irssilike cli client for tent.io written in Python.

Nothing more than a urwid window and a fetcher in the background to get your new posts.
It's almost 100% usable for me right now as my only tent client.

A lot of stuff is not working right now, but this is what _is_ working:
* posting
* follow someone
* read posts
* read reposts

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
* e      : enter edit line

In edit mode
* /follow https://tent.tent.is  : follow specified entity
* esc    : stop editing
* <enter> post what you have written in edit line