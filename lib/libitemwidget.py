import urwid

class ItemWidget (urwid.WidgetWrap):
    """imports and overrides urwid.widgetwrap so that we can set columns as we please"""
    def __init__ (self, time, postdata, entity, postid="", entityUrl="" ):
        self.postdata = '%s' % (postdata)
        self.postid = '%s' % (postid)
        self.entity = '%s' % (entity)
        self.entityUrl = '%s' % (entityUrl)
        self.item = [
            
            
            ('fixed', 6, urwid.Padding ( urwid.AttrWrap ( urwid.Text ('%s' % time) , 'body', 'focus'), right=1)),
            ('fixed', 16,urwid.Padding ( urwid.AttrWrap ( urwid.Text ('%s' % entity) , 'entity', 'focus'), right=1)),
            (urwid.Padding(urwid.AttrWrap(urwid.Text('%s' % postdata), 'body', 'focus'),align='left')),

        ]
        w = urwid.Columns(self.item)
        self.__super.__init__(w)

    def selectable(self):
        return True

    def keypress(self, size, key):
        return key
