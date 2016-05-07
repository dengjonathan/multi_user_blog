import os
import re
from string import letters
import hashlib

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

# hash functions
def hash_str(s):
    s = str(s)
    return hashlib.sha256(s).hexdigest()

def make_secure_val(s):
    """given a string value, returns string and sha256 hash in tuple form"""
    return '%s%s' % (s, hash_str(s))

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

class BaseHandler(webapp2.RequestHandler):

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.response.out.write(self.render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)


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
                visits = 0
        else:
            visits = 0
        visits_cookie = make_secure_val(visits)
        self.response.headers.add_header('Set-Cookie',
                                         'visits=%s;' % visits_cookie)

        posts = db.GqlQuery('SELECT * FROM Post ORDER BY created_at DESC')
        if visits > 100:
            self.render('home.html', posts=posts, visits=visits,
                        congrats='Congrats, you\'re a power user!')
        else:
            self.render('home.html', posts=posts, visits=visits)

    def post(self):
        title = self.request.get('title')
        message = self.request.get('message')
        if title and message:
            a = Post(title=title, message=message)
            a.put()
            self.redirect('/')
        else:
            self.render('home.html', title=title, message=message,
                        error="You need to enter both title and message!")

class Welcome(BaseHandler):

    def get(self):
        title = self.request.get('title')
        message = self.request.get('message')
        self.render('welcome.html', title=title, message=message)

# database classes

class Post(db.Model):
    title = db.StringProperty(required=True)
    message = db.TextProperty()
    created_at = db.DateTimeProperty(auto_now_add=True)


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/welcome', Welcome)],
                              debug=True)
