import os
import sys
from ConfigParser import SafeConfigParser

class config(object):
    """objects holds config information"""

    def __init__(self):
        self.getconfigpath()
        self.openconfig()
        self.readconfig()

    def getconfigpath(self):
        """returns config path as string if found else sys.exit""" 

        paths=["~/.tentog","~/.config/tentog"]
        for path in paths:
            if os.path.isdir(os.path.expanduser(path)):
                self.configpath=os.path.expanduser(path)
        try:
            c = self.configpath
        except AttributeError:
            print "Please create tentog config and storage dir as %s or %s"%(paths[0],paths[1])
            sys.exit(1)

    def openconfig(self):
        """opens config file in config path from getconfigpath returns file handle"""

        try:
            with open(self.configpath+"/config") as self.fhandle: pass 
            self.configfile=self.configpath+"/config"
        except IOError as e:
            print "Could not open config file %s"%(self.configpath+"/config")
            sys.exit(1)

    def missingreq(self,miss):
        """raise error from config file input is output message"""
        raise AttributeError("Missing required entry %s in config file."%(miss))

    def readconfig(self,value=""):
        """read config file value as optional input will return value"""
        parser = SafeConfigParser()
        parser.read(self.configfile)
        if parser.has_section('tentog'):
            # check required options in config file
            if parser.has_option('tentog','entityUrl'):
                self.entityUrl=parser.get('tentog', 'entityUrl')
            else:
                self.missingreq('entityUrl')
            if parser.has_option('tentog','keystore'):
                self.keystore=parser.get('tentog', 'keystore')
            else:
                self.missingreq('keystore')
            if parser.has_option('tentog','datastore'):
                self.datastore=parser.get('tentog', 'datastore')
            else:
                self.missingreq('datastore')

            #optional options in config file
            if parser.has_option('tentog','editor'):
                self.editor=parser.get('tentog','editor')

            if parser.has_option('tentog','debuglog'):
                self.debuglog=parser.get('tentog', 'debuglog')

        else:
            raise AttributeError("Required section [tentog] missing in config file.")
        #if value is not null return requested value
        if value:
            if value=='entityUrl':
                return self.entityUrl
            elif value=='keystore':
                return self.keystore
            elif value=='datastore':
                return self.datastore
            elif value=='editor':
                return self.editor
            else:
                raise AttributeError("Missing requested value %s in config file."%(value))
