import os
import re
import string
import hmac
import hashlib
import random
# import bcrypt
import webapp2
import jinja2

from google.appengine.ext import ndb
from webapp2_extras import sessions

import database_classes as dbc

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

with open('secrets.txt') as secret:
    CLIENT_SECRET = secret.read().strip()


# valid signin functions
def valid_username(username):
    """returns True if username entered and is valid"""
    user_RE = re.compile("^[a-zA-Z0-9_-]{3,20}$")
    return username and user_RE.match(username)

def valid_pass(password):
    pass_RE = re.compile("^.{3,20}$")
    return password and pass_RE.match(password)

def valid_email(email):
    email_RE = re.compile("^[\S]+@[\S]+.[\S]+$")
    return email_RE.match(email)

# hash functions
def hash_str(s):
    s = str(s)
    return hmac.new(CLIENT_SECRET, s).hexdigest()

def make_secure_val(s):
    """given a string value, returns string and sha256 hash in tuple form"""
    return '%s|%s' % (s, hash_str(s))

def check_secure_value(h):
    """
    args: comma seperated string where first value is int and second value is
    hash
    returns: value if hash of value matched hashed_value or None
    """
    value = h[0]
    hash = h[1:]
    if make_secure_val(value) == h:
        return value
    else:
        return None

# Todo add bcrypt module

def make_salt(n):
    """returns string of n random characters for use in hashing"""
    choices = string.ascii_letters + string.digits
    salt = ''.join(choices[random.randint(0, len(choices))] for i in range(n))
    return salt

def make_pw_hash(name, pw, salt=None):
    """
    returns hash of name and password with salt of 5 random alpanumeric chars
    User can specify own salt, default is randomly generated
    """
    if not salt:
        salt = make_salt(5)
    hash = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s|%s' % (hash, salt)

def valid_password(name, pw, hash):
    hash = hash.split('|')
    salt = hash[1]
    if make_pw_hash(name, pw, salt=salt) == hash:
        return True
    else:
        return False


# webapp2 Request Handlers
class BaseHandler(webapp2.RequestHandler):

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.response.out.write(self.render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)
        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()


class MainPage(BaseHandler):

    def get(self):
        # get cookies showing how many visits
        visits_cookie = self.request.cookies.get('visits')
        # set new cookie showing a new visits
        if visits_cookie:
            visits = check_secure_value(visits_cookie)
            if visits:
                visits = int(visits) + 1
            else:
                visits = 1
        else:
            visits = 1
        visits_cookie = make_secure_val(visits)
        self.response.headers.add_header('Set-Cookie',
                                         'visits=%s;' % visits_cookie)
        # change query to ndb query
        posts = dbc.Post.query().order(-dbc.Post.created_at)
        if visits > 100:
            self.render('home.html', posts=posts, visits=visits,
                        congrats='Congrats, you\'re a power user!')
        else:
            self.render('home.html', posts=posts, visits=visits)

    def post(self):
        title = self.request.get('title')
        message = self.request.get('message')
        if title and message:
            a = dbc.Post(title=title,
                         message=message,
                         username=self.session['username']
                         )
            a.put()
            self.redirect('/')
        else:
            self.render('home.html', title=title, message=message,
                        error="You need to enter both title and message!")

class Welcome(BaseHandler):

    def get(self):
        username = self.session.get('username')
        self.render('welcome.html', username=username)

class Signup(BaseHandler):

    def get(self):
        self.render('signup.html', params=None, error=None)

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        password_check = self.request.get('password_check')
        email = self.request.get('email')
        error = {}
        params = {'username': username, 'email':email}

        if not valid_username(username):
            error['username'] = 'Enter valid username between 3 and 20 characters.'
        if not valid_pass(password):
            error['password'] = 'Enter valid username between 3 and 20 characters.'
        if not password == password_check:
            error['password_check'] = 'Passwords must match'
        if email:
            if not valid_email(email):
                error['email'] = 'Enter valid email address'
        if error:
            self.render('signup.html', error=error, params=params)
        else:
            self.session['username'] = username
            n = dbc.User(username=username,
                         password=make_pw_hash(username, password),
                         email=email)
            n.put()
            self.redirect('/welcome')


class Login(BaseHandler):

    def get(self):
        self.render('login.html', error='', username='')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        user = dbc.User.query().filter(dbc.User.username==username).fetch(1)[0]
        print '### %s' % user
        if user:
            print '### password %s' % user.password
            given_password = make_pw_hash(
                                          username, password,
                                          salt=user.password.split('|')[1]
                                          )
            if user.password == given_password:
                self.session['username'] = username
                self.session['email'] = user.email
                return self.redirect('/welcome')
        self.render('login.html', username=username,
                    error='Incorrect username/ password combo')

class TestPage(BaseHandler):

    def get(self):
        session = self.session
        users = dbc.User.query()
        posts = dbc.Post.query()
        self.render('testpage.html', users=users, posts=posts, session=session)

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': CLIENT_SECRET,
}

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/welcome', Welcome),
                               ('/signup', Signup),
                               ('/test', TestPage),
                               ('/login', Login)],
                              config=config,
                              debug=True)
