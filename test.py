#!/usr/bin/env python

import tentog as to
import lib.libconfig
import lib.liblogin as login
import sys
import pprint

def test_getconfig(config):
    print "\ntest001"
    print "======="
    print "description: find config dir"
    print "testobject:  class config def getconfigpath"
    print "input:       none"
    print "output:      path to tentog config directory"
    print "result:"
    try:
        print config.configpath
        print "PASS"
    except AttributeError, e:
        sys.stderr.write(str(e)+"\n")
        print "FAIL"
        sys.exit(1)

def test_openconfig(config):
    print "\ntest002"
    print "======="
    print "description: try to open config file"
    print "testobject:  class config def openconfig"
    print "input:       getconfigpath+/config"
    print "output:      filehandle"
    print "result:"
    try:
        print config.fhandle
        print "PASS"
    except Exception, e:
        sys.stderr.write(str(e)+"\n")
        print "FAIL"
        sys.exit(1)

def test_readconfig(config):
    print "\ntest003"
    print "======="
    print "description: try to read required values from config file"
    print "testobject:  class config def readconfig"
    print "input:       openconfig"
    print "output:      string required values: entity, keystore"
    print "result:"
    try:
        print config.keystore
        print config.entityUrl
        print config.datastore
        print "PASS"
    except Exception, e:
        print e
        print "FAIL"
        sys.exit(1)

def test_getvalue(config):
    print "\ntest004"
    print "======="
    print "description: get one optional value from config file"
    print "testobject:  class config def readconfig"
    print "input:       string"
    print "output:      value"
    print "result:"
    try:
        print config.editor
        print "PASS"
    except Exception, e:
        print e

def test_login():
    print "\ntest005"
    print "======="
    print "description: login to server"
    print "testobject:  def login"
    print "input:       "
    print "output:      profile"
    print "result:"
    print pprint.pformat(login.login(test=1))

def starttests():
    #config test scope : config
    config=lib.libconfig.config()
    #test001
    test_getconfig(config)
    #test002
    test_openconfig(config)
    #test003
    test_readconfig(config)
    #test004
    test_getvalue(config)

    #config test scope : login
    #test005
    test_login()
    

if __name__=="__main__":
    starttests()
