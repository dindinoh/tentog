import sys
sys.path.append('./python-tent-client')
import tentapp
import lib.libconfig as config

def login(test=""):
    """login to your server"""
    """TODO: error handling failed login does not work in tentapp.py"""
    """      and login is not really used until fetching post"""
    """      so maybe change sanitycheck to include fetching one post"""

    
    conf=config.config()
    entityUrl=conf.entityUrl
    keystore=conf.keystore
    app = tentapp.TentApp(entityUrl)

    app.appDetails = {
        'name': 'Tentog',
        'description': 'trying to be a pale shadow of mutt, and irssi, but done in python, err, well a practical curses to tent',
        'url': 'http://zzzzexample.com',
        'icon': 'http://zzzzexample.com/icon.png',
        'oauthCallbackURL': 'http://zzzzexample.com/oauthcallback',
        'postNotificationUrl': None,
        }

    keyStore = tentapp.KeyStore(keystore)
    app.keys = keyStore.get(entityUrl, {})

    if not app.hasRegistrationKeys():
        app.register()
        keyStore.save(entityUrl, app.keys)

    if not app.hasPermanentKeys():
        approvalURL = app.getUserApprovalURL()
        a=raw_input("Tentog can't find your keystore as specified in your config file.\nDo you wish to create it now? (Y/n) ")
        if a in ['Y','y','']:
            print "\nPlease go to this url to register Tentog:\n"
            print approvalURL
            print 
            print 'After registration find this code in your url:'
            print 'http://zzzzexample.com/oauthcallback?code=15673b7718651a4dd53dc7defc88759e&state=ahyKV...'
            print '                                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'
            print 'Enter that code here:'
            code = raw_input('> ')
            print '-----------'
            app.getPermanentKeys(code)
            keyStore.save(entityUrl, app.keys)

    if test:
        return app.getProfile()

    if app.hasPermanentKeys():
        return app



