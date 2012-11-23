import sys
import time
sys.path.append('./python-tent-client')
import tentapp
import lib.libconfig as libconfig
import lib.liblogin as liblogin
import lib.libfunc as libfunc

class getrepost(object):
    def __init__(self):
        orgid = ""
        orgposter = ""
    def getrepost(self):
        try:
            app = tentapp.TentApp(self.orgposter)
            post = app.getPosts(id=self.orgid)
        except:
            post={'content':{'text':'could not fetch %s'%(self.orgid)}}

        repost = "Repost => " + self.orgposter + ": " + post['content']['text']
        return repost

def sendpost(message):
    """send post to server"""
    conf = libconfig.config()
    app = liblogin.login()
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
    except Exception, e:
        libfunc.debug("something went wrong posting: \n%s" % (message))
        libfunc.debug(e)

