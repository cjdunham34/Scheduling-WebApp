# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - api is an example of Hypermedia API support and access control
#########################################################################

@auth.requires_login()
def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    user_fname = auth.user.first_name if auth.user else "Person"
    requests = db(User.id==Link.target)(Link.source==me)(Link.accepted==True)\
      .select(orderby=alphabetical)
    return locals()

@auth.requires_login()
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@auth.requires_login()
def edit_schedule():
    return dict(post_url=URL('store_schedule'))

# called via ajax
def store_schedule():
    monday = request.vars['monday[]']
    tuesday = request.vars['tuesday[]']
    wednesday = request.vars['wednesday[]']
    thursday = request.vars['thursday[]']
    friday = request.vars['friday[]']
    saturday = request.vars['saturday[]']
    sunday = request.vars['sunday[]']
    db.schedule.update_or_insert(db.schedule.user == auth.user, user=auth.user, monday=monday, tuesday=tuesday, wednesday=wednesday, thursday=thursday, friday=friday, saturday=saturday, sunday=sunday)
    response.flash = T("schedule has been saved!")
    return response.json(dict(monday=monday, tuesday=tuesday, wednesday=wednesday, thursday=thursday, friday=friday, saturday=saturday, sunday=sunday))

@auth.requires_login()
def get_schedule():
    row = db.schedule(user=auth.user)
    if not row:
        db.schedule.insert(user=auth.user)
    time_list = []
    day_num = request.vars.num
    if day_num=='0': time_list = db(db.schedule.user == auth.user.id).select().first().monday
    elif day_num=='1': time_list = db(db.schedule.user == auth.user.id).select().first().tuesday
    elif day_num=='2': time_list = db(db.schedule.user == auth.user.id).select().first().wednesday
    elif day_num=='3': time_list = db(db.schedule.user == auth.user.id).select().first().thursday
    elif day_num=='4': time_list = db(db.schedule.user == auth.user.id).select().first().friday
    elif day_num=='5': time_list = db(db.schedule.user == auth.user.id).select().first().saturday
    elif day_num=='6': time_list = db(db.schedule.user == auth.user.id).select().first().sunday
    return response.json(time_list)

@auth.requires_login()
def get_f_schedule():
    user_friend = request.vars.user_friend
    row = db.schedule(user=user_friend)
    if not row:
        db.schedule.insert(user=user_friend)
    time_list = []
    day_num = request.vars.num
    if day_num=='0': time_list = db(db.schedule.user == user_friend).select().first().monday
    elif day_num=='1': time_list = db(db.schedule.user == user_friend).select().first().tuesday
    elif day_num=='2': time_list = db(db.schedule.user == user_friend).select().first().wednesday
    elif day_num=='3': time_list = db(db.schedule.user == user_friend).select().first().thursday
    elif day_num=='4': time_list = db(db.schedule.user == user_friend).select().first().friday
    elif day_num=='5': time_list = db(db.schedule.user == user_friend).select().first().saturday
    elif day_num=='6': time_list = db(db.schedule.user == user_friend).select().first().sunday
    return response.json(time_list)
    
@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_login() 
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)

@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs bust be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())

def user():
    return dict(form=auth())

def download():
    return response.download(request, db)

def call():
    session.forget()
    return service()

# our home page, will show our posts and posts by friends
@auth.requires_login()
def home():
    Post.posted_by.default = me
    Post.posted_on.default = request.now
    crud.settings.formstyle = 'table2cols'
    form = crud.create(Post)
    friends = [me]+[row.target for row in myfriends.select(Link.target)]
    posts = db(Post.posted_by.belongs(friends))\
        .select(orderby=~Post.posted_on, limitby=(0, 100))
    return locals()

# our wall will show our profile and our own posts
@auth.requires_login()
def wall():
    user = User(a0 or me)
    if not user or not (user.id==me or \
       myfriends(Link.target==user.id).count()):
        redirect(URL('home'))
    posts = db(Post.posted_by==user.id)\
        .select(orderby=~Post.posted_on, limitby=(0, 100))
    myInbox = db(Post.posted_to==me)\
        .select(orderby=~Post.posted_on, limitby=(0, 100))
    friends = db(User.id==Link.source)(Link.target==me)(Link.accepted==True)\
     .select(orderby=alphabetical)
    print (friends)
    #put into a list
    friendIDNum = []
    for friend in friends:
        friendIDNum.append(friend.auth_user.id)
        print (friend.auth_user)
    db.post.posted_by.default = me
    db.post.posted_to.requires = IS_IN_SET(friendIDNum, [(friends[x].auth_user.first_name + ' ' + friends[x].auth_user.last_name) for x in range(0, friendIDNum.__len__())], zero='Choose a Friend')
    db.post.posted_on.default = request.now
    form = SQLFORM(db.post, fields=['posted_to', 'body'])
    if form.process().accepted:
        session.flash = 'form accepted'
        redirect(URL('wall'))
    return locals()

# a page for searching friends and requesting friendship
@auth.requires_login()
def search():
    form = SQLFORM.factory(Field('name', requires=IS_NOT_EMPTY()))
    if form.accepts(request):
        tokens = form.vars.name.split()
        query = reduce(lambda a,b:a&b,
            [User.first_name.contains(k)|User.last_name.contains(k) \
             for k in tokens])
        people = db(query).select(orderby=alphabetical)
    else:
        people = []
    return locals()

# a page for accepting and denying friendship requests
@auth.requires_login()
def friends():
    friends = db(User.id==Link.source)(Link.target==me)\
      .select(orderby=alphabetical)
    requests = db(User.id==Link.target)(Link.source==me)\
      .select(orderby=alphabetical)
    return locals()

# this is the Ajax callback
@auth.requires_login()
def friendship():
    """Ajax callback!"""
    if request.env.request_method != 'POST': raise HTTP(400)

    if a0=='request' and (not Link(source=me, target=a1)) and not (int(a1)==int(me)):
        # insert a new friendship request
        Link.insert(source=me, target=a1)
    elif a0=='accept':
        # accept an existing friendship request
        db(Link.target==me)(Link.source==a1).update(accepted=True)
        if not db(Link.source==me)(Link.target==a1).count() :
            Link.insert(source=me, target=a1)
            db(Link.target==a1)(Link.source==me).update(accepted=True)
    elif a0=='deny':
        # deny an existing friendship request
        db(Link.target==me)(Link.source==a1).delete()
    elif a0=='remove':
        # delete a previous friendship request
        db(Link.source==me)(Link.target==a1).delete()
        db(Link.source==a1)(Link.target==me).delete()
