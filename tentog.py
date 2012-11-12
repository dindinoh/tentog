#!/usr/bin/env python

"""
Small cli client, irssi lookalike, for tent.io servers.
"""

import urwid
import time
import simplejson
import sys
import threading
import os

from datetime import datetime

import lib.libconfig as config
import lib.libitemwidget as itemwidget
import lib.liblogin as login

sys.path.append('./python-tent-client')
import tentapp

def search(tosearch):
    """search in datastore, will not be used if move to not saving more than 50 posts at a time"""
    debug("looking for: %s" % (tosearch))
    conf=config.config()
    filelines = open(conf.datastore+"status", 'r').readlines()
    found=0
    for line in filelines:
        unser = simplejson.loads(line)
        try:
            if tosearch in unser['content']['text']:
                debug('SEARCH: found %s'%(unser))
                try:
                    gtentog().sysmsg(unser['content']['text'])
                except Exception, e:
                    debug(e)
                found=1
        except:
            pass

    if found==0:
        debug("Sorry no matches found")

def getstatusfromfile():
    """get posts from datastorage returns list of posts"""
    statuslist = []
    conf=config.config()
    filelines = open(conf.datastore+'status', 'r').readlines()
    lines = filelines[-100:]
    for line in lines:
        unser = simplejson.loads(line)
        statuslist.append(unser)
    return statuslist

def unfollow(entity,lastid=""):
    """unfollow entity
    get ent['id'] first from followers and unfollow that id
    NOT WORKING
    """
    conf=config.config()
    app = login.login()
    if lastid:
        debug('unfollow: Have lastid: %s'%(lastid))
        getf = app.getFollowers(since_id=lastid)
    else:
        debug('unfollow: Have NO lastid')
        getf = app.getFollowers()
    for ent in getf:
        lastid=ent['id']
        debug('lastid in loop = %s'%(lastid))
        if ent['entity']==entity:
            debug('found entity match: %s and %s'%(ent['entity'],entity))
            try:
                app.unfollow(ent['id'])
                debug('unfollowed: %s'%(entity))
                return True
            except Exception, e:
                debug('error unfollowing: %s' % (entity))
                debug(e)
                return False
        else:
            debug('%s is not the same as %s'%(ent['entity'],entity))
    unfollow(entity,lastid)

def follow(entity):
    """follow entity"""
    conf=config.config()
    app = login.login()
    try:
        app.follow(str(entity))
        return True
    except Exception, e:
        debug('error following: %s' % (entity))
        debug(e)
        return False

def sendpost(message):
    """send post to server"""
    conf=config.config()
    app = login.login()
    post = {
        # add essay if > 256char
        'type': 'https://tent.io/types/post/status/v0.1.0',
        'published_at': int(time.time()),
        'permissions': {
            # add private as option
            'public': True,
            },
        # this should be read from config file
        'licenses': [''],
        'app': { 'name' : 'Tentog' },
        'content': {
            'text': message,
            }
        }
    try:
        app.putPost(post)
        gtentog()
    except Exception, e:
        debug("something went wrong posting: \n%s" % (message))
        debug(e)

def reply(marked):
    """reply to marked post"""
    debug('REPLY marked: %s'%(marked))
    gtentog()

def newpost():
    """new post"""
    import time
    os.system(config().getvalue('editor')+"/tmp/tentpost.txt")
    f = open('/tmp/tentpost.txt', 'r').readlines()
    message = ""
    for line in f:
        message = message + line
    sendpost(message[0:-1])
    os.system('rm -rf /tmp/tentpost.txt')
    os.system('clear')
    gtentog()

def debug(message):
    """prints debug message to logfile"""
    conf=config.config()
    try:
        logfile = open(conf.debuglog, 'a')
    except Exception, e:
        quit('no debuglog path specified, that is required for now.',1)
    try:
        logfile.write(str(datetime.now()) + " - " + message + "\n")
    except Exception, e:
        logfile.write(str(datetime.now()) + " - " + str(e) + "\n")
    logfile.close()    

def quit(quitmsg,exitvalue):
    """general quit message"""
    print quitmsg
    fetcher()._stop = threading.Event()
    sys.exit(exitvalue)

def sanitycheck():
    """pre-flight sanity check"""
    """TODO: include config file tests, make optional according to option parsing"""
    #login.login()
    try:
        conf = config.config()
    except Exception, e:
        print e
    

class fetcher(threading.Thread):
    """fetches new updates in feed and stores them in datastore"""


    # post types not yet added:
    # https://tent.io/types/post/delete/v0.1.0

    def run(self):
        super(fetcher, self).__init__()
        self._stop = threading.Event()
        knowntypes = [
            'https://tent.io/types/post/status/v0.1.0',
            'https://tent.io/types/post/following/v0.1.0',
            'https://tent.io/types/post/follower/v0.1.0',
            'https://tent.io/types/post/profile/v0.1.0',
            'http://www.beberlei.de/tent/bookmark/v0.0.1',
            'https://tent.io/types/post/essay/v0.1.0',
            'https://tent.io/types/post/photo/v0.1.0'
            ]

        conf=config.config()
        app = login.login()
        if app:
            f = open(conf.datastore+'status', 'r').readlines()[-1]
            latest = int(simplejson.loads(f)['published_at'])
            oldpostid = simplejson.loads(f)['id']
            posts = app.getPosts(since_time=latest)
            posts.sort(key = lambda p: p['published_at'])
            for post in posts:
                debug('looking for new posts')
                if post['type'] in knowntypes:
                    if post['id'] <> oldpostid:
                        gettime = timestamp = time.strftime("%H:%M", time.localtime(post['published_at']))
                        postid = post['id']
                        debug("wrote new posts with timestamp: %s and id: %s"%(gettime,postid))
                        dumpit = simplejson.dumps(post)
                        file = open(conf.datastore+'status', 'a')
                        file.write(dumpit + "\n")
                        file.close()
                else:
                    debug ("Found strange post type: %s"  % ( post ))
            while not self.stopped():
                time.sleep(60)
                fetcher().start()
                return 1

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

class CustomEdit(urwid.Edit):
    """edit footer"""
    __metaclass__ = urwid.signals.MetaSignals
    signals = ['done']

    def keypress(self, size, key):
        """take care of keypress and dispatch actions"""
        if key == 'enter':
            urwid.emit_signal(self, 'done', self.get_edit_text())
            if "/f " in self.get_edit_text() or "/follow " in self.get_edit_text():
                whotofollow = str(self.get_edit_text()).split(' ')[1]
                if whotofollow:
                    follow(whotofollow)
                    gtentog()
            if "/s " in self.get_edit_text() or "/search " in self.get_edit_text():
                tosearch = str(self.get_edit_text()).split(' ')[1]
                if tosearch:
                    search(tosearch)
                    gtentog()
            if "/u " in self.get_edit_text() or "/unfollow " in self.get_edit_text():
                whotounfollow = str(self.get_edit_text()).split(' ')[1]
                if whotounfollow:
                    unfollow(whotounfollow)
            if "/u " in self.get_edit_text():
                gtentog()
            if "/r " in str(self.get_edit_text()):
                debug('SENDING TO REPLY')
                reply(self.get_edit_text())
                gtentog()
                return
            if "/" not in str(self.get_edit_text())[0]:
                sendpost(self.get_edit_text())
                debug('ended up in post again did we?')
                gtentog()
                return
        elif key == 'esc':
            urwid.emit_signal(self, 'done', None)
            gtentog()
            return

        urwid.Edit.keypress(self, size, key)

class gtentog(object):
    """start the gui and fetch posts from datastore"""
    def __init__(self):
        palette = [
            ('head','light cyan', 'black'),
            ('body','', '', 'standout'),
            ('entity','light cyan', '', 'standout'),
            ('foot','', 'black'),
            ('focus','', 'light cyan', 'standout'),
            ]

        items = []
        for line in getstatusfromfile():
            if line['type'] == 'https://tent.io/types/post/status/v0.1.0':
                timestamp = time.strftime("%H:%M", time.localtime(line['published_at']))
                entity = str(line['entity']).split('//')[1].split('.')[0] + ">"
                msg = '%s' % (line['content']['text'])
                postid = line['id']
                entityUrl = line['entity']
                items.append(itemwidget.ItemWidget(timestamp,msg,entity,postid,entityUrl))
            elif line['type'] == 'https://tent.io/types/post/repost/v0.1.0':
                timestamp = time.strftime("%H:%M", time.localtime(line['published_at']))
                entity = str(line['entity']).split('//')[1].split('.')[0] + ">"
                msg = '-- repost: %s\n' % (str(line['content']['entity']).split('//')[1].split('.')[0])
                #repost = getrepostfromfile(line['id']) 
                #if not repost:
                debug("repost not in database")
                items.append(itemwidget.ItemWidget(timestamp,msg,entity))
                debug('have repost at time %s from %s'%(timestamp,entity))
            elif line['type'] == 'https://tent.io/types/post/following/v0.1.0':
                timestamp = time.strftime("%H:%M", time.localtime(line['published_at']))
                entity = "Tentog>"
                msg = "You are now following %s" % (line['content']['entity'])
                items.append(itemwidget.ItemWidget(timestamp,msg,entity))
            elif line['type'] == 'https://tent.io/types/post/follower/v0.1.0':
                timestamp = time.strftime("%H:%M", time.localtime(line['published_at']))
                entity = "Tentog>"
                msg = "You are now followed by %s" % (line['content']['entity'])
                items.append(itemwidget.ItemWidget(timestamp,msg,entity))

        walker = urwid.SimpleListWalker(items)
        self.listbox = urwid.ListBox(walker)
        focus = self.listbox.set_focus(+100)
        self.view = urwid.Frame(urwid.AttrWrap(self.listbox, 'body'))
        self.foot = CustomEdit(' > ')
        self.view.set_footer(self.foot)        
        # TODO use watch_file to make automatic repaint of window work?
        #self.main_loop.event_loop.watch_file(
        #    self.pipe_stderr_read,
        #    self.stderr_event)
        loop = urwid.MainLoop(self.view, palette, unhandled_input=self.keystroke)
        urwid.connect_signal(walker, 'modified', self.update)
        loop.run()

    def sysmsg(self,sysmsg):
        """ this function might be used for interacting with the user and if used it should be made into a new function with the above one to avoid duplication"""
        palette = [
            ('head','light cyan', 'black'),
            ('body','', '', 'standout'),
            ('entity','light cyan', '', 'standout'),
            ('foot','', 'black'),
            ('focus','', 'light cyan', 'standout'),
            ]

        items = []
        timestamp="now"
        entity="Tentog>"
        msg=sysmsg
        items.append(itemwidget.ItemWidget(timestamp,msg,entity))
        walker = urwid.SimpleListWalker(items)
        self.listbox = urwid.ListBox(walker)
        focus = self.listbox.set_focus(+100)
        self.view = urwid.Frame(urwid.AttrWrap(self.listbox, 'body'))
        self.foot = CustomEdit(' > ')
        self.view.set_footer(self.foot)        
        loop = urwid.MainLoop(self.view, palette, unhandled_input=self.keystroke)
        urwid.connect_signal(walker, 'modified', self.update)
        loop.run()
    
    def update(self):
        """repaint status window (is this one used?)"""
        focus = self.listbox.get_focus()[0].postid
        #self.view.set_header(urwid.AttrWrap(urwid.Text('selected: %s' % str(focus)), 'head'))

    def keystroke (self, input):
        """read keystroke in when in status window"""
        try:
            if input in ('q'):
                quit("Tentog quit.",0)
            #if input is 'enter':
            #    focus = listbox.get_focus()[0].content
            #    view.set_header(urwid.AttrWrap(urwid.Text('tentog : should show verbose from %s' % str(focus)), 'head'))
            if input is 'r':
                self.foot = CustomEdit(' > /reply %s %s: '%(self.listbox.get_focus()[0].postid,self.listbox.get_focus()[0].entityUrl))
                self.view.set_footer(self.foot)
                self.edit()
            if input is 'u':
                gtentog()
            if input is 'p':
                newpost()    
            if input == 'e':
                self.edit()
            if input == 't':
                self.sysmsg("messy")
            if input == 'm':
                mentions()
        except TypeError:
            pass
    
    def edit(self):
        self.view.set_focus('footer')
        urwid.connect_signal(self.foot, 'done', self.edit_done)

    def edit_done(self, content):
        self.view.set_focus('body')
        urwid.disconnect_signal(self, self.foot, 'done', self.edit_done)
        if content:
            focus = self.listbox.get_focus()[0]
        self.view.set_footer(None)

if __name__ == '__main__':
    try:
        sanitycheck()
        fetcher().start()
        gtentog()
    except (KeyboardInterrupt, SystemExit):
        quit("Tentog killed.",1)
