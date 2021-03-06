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

import lib.libconfig as libconfig
import lib.libitemwidget as libitemwidget
import lib.liblogin as liblogin
import lib.libpost as libpost
import lib.libfunc as libfunc
import lib.libfollow as libfollow

sys.path.append('./python-tent-client')
import tentapp

def quit(quitmsg,exitvalue):
    """general quit message"""
    print quitmsg
    fetcher()._stop = threading.Event()
    sys.exit(exitvalue)

class fetcher(threading.Thread):
    """fetches new updates in feed and stores them in datastore"""

    def run(self):
        super(fetcher, self).__init__()
        self._stop = threading.Event()

        knowntypes = [
            'https://tent.io/types/post/status/v0.1.0',
            'https://tent.io/types/post/following/v0.1.0',
            'https://tent.io/types/post/follower/v0.1.0',
            'http://www.beberlei.de/tent/bookmark/v0.0.1',
            'https://tent.io/types/post/essay/v0.1.0',
            'https://tent.io/types/post/photo/v0.1.0',
            'https://tent.io/types/post/repost/v0.1.0',
            'http://www.beberlei.de/tent/favorite/v0.0.1'
            #'https://tent.io/types/post/profile/v0.1.0',
            ]

        conf=libconfig.config()
        app = liblogin.login()
        if app:
            try:
                f = open(conf.datastore+'status', 'r').readlines()[-1]
                latest = int(simplejson.loads(f)['published_at'])
                oldpostid = simplejson.loads(f)['id']
                posts = app.getPosts(since_time=latest)
            except Exception, e:
                posts = app.getPosts()
                oldpostid=""
            posts.sort(key = lambda p: p['published_at'])
            for post in posts:
                if post['type'] in knowntypes:
                    if post['id'] <> oldpostid:
                        if post['type']=='https://tent.io/types/post/repost/v0.1.0':
                            orgposter = post['content']['entity']
                            orgid = post['content']['id']
                            rep = libpost.getrepost()
                            rep.orgid=orgid
                            rep.orgposter=orgposter
                            repost=rep.getrepost()
                            post['content']['text']=repost
                        gettime = timestamp = time.strftime("%H:%M", time.localtime(post['published_at']))
                        postid = post['id']
                        libfunc.debug("wrote new posts with timestamp: %s and id: %s"%(gettime,postid))
                        dumpit = simplejson.dumps(post)
                        file = open(conf.datastore+'status', 'a')
                        file.write(dumpit + "\n")
                        file.close()
                else:
                    libfunc.debug ("Found strange post type: %s"  % ( post['type'] ))
            while not self.stopped():
                time.sleep(20)
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
            try:
                if self.reply:
                    self.reply.message=self.get_edit_text()
                    self.reply.sendreply()
                    gtentog()
            except AttributeError, e:
                pass
            if "/f " in self.get_edit_text() or "/follow " in self.get_edit_text():
                whotofollow = str(self.get_edit_text()).split(' ')[1]
                if whotofollow:
                    f = libfollow.follow(whotofollow)
                    if not f == True:
                        sysmsg(f)
                    gtentog()
            
            if "/u " in self.get_edit_text() or "/unfollow " in self.get_edit_text():
                whotounfollow = str(self.get_edit_text()).split(' ')[1]
                if whotounfollow:
                    libfollow.unfollow(whotounfollow)
            
            if not self.get_edit_text() or "/" not in str(self.get_edit_text())[0]:
                libpost.sendpost(self.get_edit_text())
                gtentog()

            else:
                gtentog()

        elif key == 'tab':
            urwid.emit_signal(self, 'done', None)
            gtentog()
            return

        urwid.Edit.keypress(self, size, key)

def sysmsg(msg):
    towrite='{"attachments": [],"app": {"url": "tentog", "name": "Tentog sysmsg"},"updated_at": 0,"entity": "http://Tentog.","content": {"text": "%s"},"received_at": 0,"published_at": 0,"version": 1,"licenses": [],"mentions": [],"type": "https://tent.io/types/post/status/v0.1.0","id":"","permissions": {"entities": {}, "public": true, "groups": []}}' % msg
    conf=libconfig.config()
    file = open(conf.datastore+'status', 'a')
    file.write(towrite + "\n")
    file.close()
    gtentog()

class gtentog(object):
    """start the gui and fetch posts from datastore, refactor"""
    function = ""
    def __init__(self):
        palette = [
            ('head','light cyan', 'black'),
            ('body','', '', 'standout'),
            ('entity','light cyan', '', 'standout'),
            ('foot','', 'black'),
            ('focus','light cyan', '', 'standout'),
            ]
        conf=libconfig.config()
        if self.function=="mentions":
            posts = libpost.mentions()
        else:
            posts = libfunc.getstatusfromfile()
        items = []
        for line in posts:
            postid = line['id']
            timestamp = time.strftime("%H:%M", time.localtime(line['published_at']))
            realtime = time.strftime("%Y-%m-%d %H:%M", time.localtime(line['published_at']))
            entity = str(line['entity']).split('//')[1].split('.')[0]
            entity = entity[0:9]
            if conf.entity in entity:
                entity = "<@"+entity+">"
            else:
                entity = "<"+entity+">"
            if line['type'] == 'https://tent.io/types/post/status/v0.1.0' or line['type']=='https://tent.io/types/post/repost/v0.1.0':
                msg = '%s' % (line['content']['text'])
                entityUrl = line['entity']
                try:
                    if line['content']['location']:
                        l=str(line['content']['location']['coordinates'][0])
                        ll=str(line['content']['location']['coordinates'][1])
                        s = 'http://maps.google.com/maps?q='+l+','+ll+'+%28'+entity[1:-1]+'%29&z=14&ll='+l+','+ll
                        msg = msg + "\nLocation => %s" % (s)
                except Exception, e:
                    pass
                try:
                    if line['mentions'][0]['post']:
                        mentions = ""
                        inreplyto=line['mentions'][0]['post']
                    for m in line['mentions']:
                        mentions = mentions + m['entity'] + " "
                    items.append(libitemwidget.ItemWidget(timestamp,msg,entity,postid,entityUrl,realtime,inreplyto,mentions))
                except:
                    items.append(libitemwidget.ItemWidget(timestamp,msg,entity,postid,entityUrl,realtime))
            elif line['type'] == 'https://tent.io/types/post/following/v0.1.0' and line['entity'] == conf.entityUrl:
                entity = "<@Tentog>"
                msg = "You are now following %s" % (line['content']['entity'])
                items.append(libitemwidget.ItemWidget(timestamp,msg,entity))
            elif line['type'] == 'https://tent.io/types/post/follower/v0.1.0' and line['entity'] == conf.entityUrl:
                entity = "<@Tentog>"
                msg = "You are now followed by %s" % (line['content']['entity'])
                items.append(libitemwidget.ItemWidget(timestamp,msg,entity))
            elif line['type'] == 'https://tent.io/types/post/essay/v0.1.0':
                msg = 'Essay => %s[...]' % (line['content']['body'][0:300])
                entityUrl = line['entity']
                items.append(libitemwidget.ItemWidget(timestamp,msg,entity,postid,entityUrl))
            elif line['type'] == 'http://www.beberlei.de/tent/bookmark/v0.0.1':
                try:
                    msg = 'Bookmark => %s \n %s \n %s' % (line['content']['url'],line['content']['title'],line['content']['description'])
                except:
                    msg = 'Bookmark => %s \n %s' % (line['content']['url'],line['content']['title'])
                items.append(libitemwidget.ItemWidget(timestamp,msg,entity,postid))

        walker = urwid.SimpleListWalker(items)
        self.listbox = urwid.ListBox(walker)
        focus = self.listbox.set_focus(+100)
        self.view = urwid.Frame(urwid.AttrWrap(self.listbox, 'body'))
        self.foot = CustomEdit(' > ')
        self.view.set_footer(self.foot)
        self.view.set_header(urwid.AttrWrap(urwid.Text('%s' % (conf.entityUrl) ),'head'))
        loop = urwid.MainLoop(self.view, palette, unhandled_input=self.keystroke)
        urwid.connect_signal(walker, 'modified', self.update)
        loop.run()
    
    def update(self):
        """repaint status window"""
        #focus = self.listbox.get_focus()[0].postid
        #self.view.set_header(urwid.AttrWrap(urwid.Text('selected: %s' % str(focus)), 'head'))

    def keystroke (self, input):
        conf=libconfig.config()
        """read keystroke in when in status window"""
        try:
            if input in ('q'):
                quit("Tentog quit.",0)
            if input is 'right':
                entityUrl = self.listbox.get_focus()[0].entityUrl
                realtime = self.listbox.get_focus()[0].realtime
                mentions = self.listbox.get_focus()[0].mentions
                inreplyto = self.listbox.get_focus()[0].inreplyto
                self.view.set_header(urwid.AttrWrap(urwid.Text('%s | by %s at %s in reply to %s mentioning %s' % (conf.entityUrl,str(entityUrl),str(realtime),str(mentions),str(inreplyto))), 'head'))
            if input is 'left':
                focus = self.listbox.get_focus()[0].entityUrl
                self.view.set_header(urwid.AttrWrap(urwid.Text('%s' % (conf.entityUrl,)), 'head'))
            if input is 'r':
                reply = libpost.postreply()
                reply.postid = self.listbox.get_focus()[0].postid
                reply.postentity = self.listbox.get_focus()[0].entityUrl
                self.foot = CustomEdit(' reply to %s > '%(reply.postentity))
                self.foot.reply = reply
                self.view.set_footer(self.foot)
                self.edit()
            if input is 'u':
                gtentog()
            if input == 'tab':
                self.edit()
            if input == 'm':
                self.function = "mentions"
                gtentog(self)
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
        libfunc.sanitycheck()
        fetcher().start()
        gtentog()
    except (KeyboardInterrupt, SystemExit):
        quit("Tentog killed.",1)
