import sys
sys.path.append('./python-tent-client')
import tentapp
import lib.libconfig as config

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
