import os
import re
from string import letters

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


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
        posts = db.GqlQuery('SELECT * FROM Post ORDER BY created_at DESC')
        self.render('home.html', posts=posts)

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
