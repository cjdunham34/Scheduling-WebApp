# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.title = request.application
response.subtitle = T('coordinate with friends!')

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Your Name <you@example.com>'
response.meta.description = ''
response.meta.keywords = ''
response.meta.generator = ''
response.meta.copyright = ''

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

response.menu = [
    (T('Home'), False, URL('default', 'index')),
    (T('Edit Schedule'), False, URL('default', 'edit_schedule')),
    (T('Inbox'), False, URL('default', 'wall')),
    (T('Friends'), False, URL('default', 'friends')),
    (T('Search'), False, URL('default', 'search')),
    ]
