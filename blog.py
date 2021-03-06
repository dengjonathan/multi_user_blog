# standard library imports
import os
import re
import string
import hmac
import hashlib
import random
import json
import time
import warnings

# Google App Engine Imports
import webapp2
from google.appengine.ext import ndb
from webapp2_extras import sessions
with open('secrets.txt') as secret:
    CLIENT_SECRET = secret.read().strip()

# Jinja2 enviroment config
import jinja2
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

# Jinja2 filter allowing use of ndb Keys as div ids in html templates


def filterKey(Key):
    """converts ndb Key object to str object for use in jinja filters"""
    return int(str((Key)).split(', ')[1][:-1])

jinja_env.filters['filterKey'] = filterKey

# sign-in/ password helper functions


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

# ndb database classes


class Comment(ndb.Model):
    """Model for comments which are a StructuredProperty of Posts"""
    username = ndb.StringProperty()
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    comment = ndb.TextProperty()


class Post(ndb.Model):
    """Models for individual content post with likes and comments associated"""
    title = ndb.StringProperty(required=True)
    message = ndb.TextProperty()
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    username = ndb.StringProperty()
    likes = ndb.IntegerProperty(repeated=True)
    comments = ndb.StructuredProperty(Comment, repeated=True)


class User(ndb.Model):
    """Model for an individual user in ndb model"""
    username = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    account_created = ndb.DateTimeProperty(auto_now_add=True)
    # this is a list of integer keys for every article that the user 'liked'
    likes = ndb.IntegerProperty(repeated=True)

# Decorator functions for request Handlers


def login_required(func):
    def func_wrapper(*args, **kwargs):
        self = args[0]
        if 'username' not in self.session:
            error = 'You need to login or signup to post!'
            return self.redirect('/signup?error=' + error)
        else:
            return func(*args, **kwargs)
    return func_wrapper

def permissions_check(func):
    """checks if user is creator of object"""
    def func_wrapper(self, user, post, data, creator, *args, **kwargs):
        print 'user '
        print user.username
        print 'creator'
        print creator
        if user.username != creator:
            error = 'You don\'t have permission to edit this object!'
            warnings.warn(error)
            raise Exception(error)
        else:
            return func(self, user, post, data, creator, *args, **kwargs)
    return func_wrapper

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


class CRUDHandler(BaseHandler):
    """
    Handler for all CRUD methods

    When JS script sends AJAX post requests, this hand will update the ndb
    models accordingly and send AJAX response back to client, which will update
    the view.
    """

    @login_required
    def post(self):
        """
        Parses AJAX request, updates database based on request.action and
        send response to client
        """
        action, user, post, data = self.parse_AJAX()
        if 'edit_comment or delete_comment' in action:
            comment = [c for c in post.comments if c.comment ==
                       self.request.get('data')][0]
            creator = comment.username
        else:
            creator = post.username
        data = getattr(self, action)(user, post, data, creator)
        json_string = {'data': data}
        return self.write(json.dumps(json_string))

    def parse_AJAX(self):
        """
        Helper method for CRUD updates. Converts AJAX request from JSON to
        datatypes useful for database access
        """
        key = int(self.request.get('key'))
        action = self.request.get('action')
        data = self.request.get('data')
        post = ndb.Key('Post', key).get()
        # gets user making CRUD action, NOT the original post author
        user = User.query().filter(
            User.username == self.session.get('username')
        ).fetch()[0]
        return action, user, post, data

    def new_comment(self, user, post, data, *args):
        comment = Comment(username=user.username, comment=data)
        post.comments.append(comment)
        post.put()
        index = post.comments.index(comment)
        # render html string for a new comment div to be appended to DOM
        return self.render_str('comment_template.html', post=post,
                               comment=comment, session=self.session)

    @permissions_check
    def edit_comment(self, user, post, data, *args):
        comment = [c for c in post.comments if c.comment == data]
        if comment:
            comment = comment[0]
            comment.comment = self.request.get('new_comment')
            post.put()
        return

    @permissions_check
    def delete_comment(self, user, post, data, *args):
        post.comments = [c for c in post.comments if c.comment != data]
        post.put()
        return

    @permissions_check
    def edit_article(self, user, post, data, *args):
        post.title = data
        post.message = self.request.get('message')
        post.put()
        return

    @permissions_check
    def delete_article(self, user, post, *args):
        post.key.delete()
        return

    def add_like(self, user, post, *args):
        if filterKey(user.key) not in post.likes:
            post.likes.append(filterKey(user.key))
            post.put()
        if filterKey(post.key) not in user.likes:
            user.likes.append(filterKey(post.key))
            user.put()
        return len(post.likes)

    def unlike(self, user, post, *args):
        post.likes = set(
            [c for c in post.likes if c != filterKey(user.key)]
        )
        post.put()
        user.likes = set(
            [c for c in user.likes if c != filterKey(post.key)]
        )
        user.put()
        return len(post.likes)


class MainPage(BaseHandler):

    def get(self, error=''):
        posts = Post.query().order(-Post.created_at)
        self.render('home.html', posts=posts,
                    error=error, session=self.session)


class Signup(BaseHandler):

    def get(self):
        self.render('signup.html', session=self.session, params='', error='')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        password_check = self.request.get('password_check')
        email = self.request.get('email')
        error = {}
        params = {'username': username, 'email': email}

        if not valid_username(username):
            error['username'] = 'Enter valid username between 3 and 20 characters.'
        if not valid_pass(password):
            error['password'] = 'Enter valid username between 3 and 20 characters.'
        if not password == password_check:
            error['password_check'] = 'Passwords must match'
        if email:
            if not valid_email(email):
                error['email'] = 'Enter valid email address'
        if User.query().filter(User.username == username).fetch():
            error = 'An account is already registered \
                    with this account'
        if error:
            self.render('signup.html', error=error,
                        params=params, session=self.session)
        else:
            n = User(username=username,
                     password=make_pw_hash(username, password),
                     email=email)
            n.put()
            self.redirect('/')


class Login(BaseHandler):

    def get(self):
        self.render('login.html', session=self.session)

    def post(self):
        """
        Takes username and password from html form and checks to ensure
        username is in database and hashed password
        matches password stored in database
        """
        username = self.request.get('username')
        password = self.request.get('password')
        user_query = User.query().filter(User.username == username)
        if user_query.fetch():
            user = user_query.fetch(1)[0]
            given_password = make_pw_hash(
                username, password,
                salt=user.password.split('|')[1]
            )
            if user.password == given_password:
                self.session['username'] = username
                self.session['email'] = user.email
                return self.redirect('/')
        return self.render('login.html', username=username, session=self.session,
                           error='Incorrect username/ password combo')


class Logout(BaseHandler):

    def get(self):
        self.render('logout.html', session=self.session)

    def post(self):
        if self.session['username']:
            self.session['username'] = ''
            self.session['email'] = ''
            self.redirect('/')
        else:
            self.render('login.html', username=username,
                        error='You were never logged in to being with!',
                        session=self.session)


class NewPost(CRUDHandler):

    @login_required
    def get(self):
        return self.render('create_new.html', session=self.session)

    @login_required
    def post(self):
        title = self.request.get('title')
        num = self.request.get('like')
        message = self.request.get('message')
        if title and message:
            a = Post(title=title,
                     message=message,
                     username=self.session['username'],
                     )
            a.put()
            key = filterKey(a.key)
            self.redirect('/article?key=' + str(key))
        else:
            self.render('home.html',
                        error="You need to enter both title and message!",
                        session=self.session, num=num)


class Article(BaseHandler):

    def get(self):
        key = int(self.request.get('key'))
        post = ndb.Key('Post', key).get()
        self.render('article.html', session=self.session, post=post)


class Profile(BaseHandler):

    @login_required
    def get(self):
        username = self.session['username']
        user = User.query().filter(User.username == username).fetch(1)[0]
        posts = Post.query().filter(Post.username == username).fetch()
        self.render('profile.html', user=user,
                    posts=posts, session=self.session)


class TestPage(BaseHandler):

    def get(self):
        session = self.session
        users = User.query()
        posts = Post.query()
        self.render('testpage.html', users=users, posts=posts, session=session)

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': CLIENT_SECRET
}

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/signup', Signup),
                               ('/test', TestPage),
                               ('/login', Login),
                               ('/newpost', NewPost),
                               ('/logout', Logout),
                               ('/article', Article),
                               ('/profile', Profile),
                               ('/post', CRUDHandler)],
                              config=config,
                              debug=True)
