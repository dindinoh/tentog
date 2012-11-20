import sys
import simplejson
sys.path.append('./python-tent-client')
import tentapp
import lib.libconfig as libconfig
import lib.liblogin as liblogin
from datetime import datetime

def getstatusfromfile():
    """get posts from datastorage returns list of posts"""
    statuslist = []
    conf=libconfig.config()
    try:
        filelines = open(conf.datastore+'status', 'r').readlines()
    except Exception, e:
        return statuslist
    lines = filelines[-100:]
    for line in lines:
        unser = simplejson.loads(line)
        statuslist.append(unser)
    return statuslist

def debug(message):
    """prints debug message to logfile"""
    conf=libconfig.config()
    try:
        logfile = open(conf.debuglog, 'a')
    except Exception, e:
        quit('no debuglog path specified, that is required for now.',1)
    try:
        logfile.write(str(datetime.now()) + " - " + message + "\n")
    except Exception, e:
        logfile.write(str(datetime.now()) + " - " + str(e) + "\n")
    logfile.close()    

def sanitycheck():
    """pre-flight sanity check"""
    try:
        conf=libconfig.config()
    except Exception, e:
        print e
