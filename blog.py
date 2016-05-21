import os
import re
import string
import hmac
import hashlib
import random
# import bcrypt
import webapp2
import jinja2
import json

from google.appengine.ext import ndb
from webapp2_extras import sessions


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

# jinja2 helper filters

def filterKey(key):
    return str(key).split(',')[1][1:-1]

jinja_env.filters['filterKey'] = filterKey

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

# ndb database classes
from google.appengine.ext import ndb

class Comment(ndb.Model):
    username = ndb.StringProperty()
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    comment = ndb.TextProperty()


class Post(ndb.Model):
    """Models an individual content post with title, message, date, and user"""
    title = ndb.StringProperty(required=True)
    message = ndb.TextProperty()
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    username = ndb.StringProperty()
    likes = ndb.StringProperty(repeated=True)
    comments = ndb.StructuredProperty(Comment, repeated=True)


class User(ndb.Model):
    username = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    account_created = ndb.DateTimeProperty(auto_now_add=True)
    # this is a list of integer keys for every article that the user 'liked'
    likes = ndb.IntegerProperty(repeated=True)

def convert_ndb_key(Key):
    """converts ndb Key object to integer"""
    return int(str(Key).split(', ')[1][:-1])

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
        posts = Post.query().order(-Post.created_at)
        self.render('home.html', posts=posts, session=self.session)

    def post(self):
        key = int(self.request.get('key'))
        print '###', key
        post = ndb.Key('Post', key).get()
        print '###', post
        user = User.query().filter(
            User.username==self.session['username']
            ).fetch(1)[0]
        if self.request.get('like'):
            post.likes.append(user.username)
            post.put()
            json_string = {'likes': post.likes,
                           'num_likes': len(post.likes)}
            self.write(json.dumps(json_string))
            user.likes.append(key)
            user.put()
            return
        if self.request.get('unlike'):
            post.likes.remove(user.username)
            post.put()
            json_string = {'likes': post.likes,
                           'num_likes': len(post.likes)}
            self.write(json.dumps(json_string))
            user.likes.append(key)
            user.put()
            return
        if self.request.get('comment'):
            comment = self.request.get('comment')
            print '###', comment
            n = Comment(username=self.session['username'],
                        comment=comment)
            post.comments.append(n)
            post.put()
            self.write(json.dumps({'comment': comment,
                                   'time_stamp': str(post.created_at)}))
            return


class Welcome(BaseHandler):

    def get(self):
        username = self.session.get('username')
        self.render('welcome.html', username=username, session=self.session)

class Signup(BaseHandler):

    def get(self):
        self.render('signup.html', params=None,
                    error='', session=self.session)

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
        if User.query().filter(User.username==username):
            error= 'An account is already registered \
                    with this account'
        if error:
            self.render('signup.html', error=error,
                        params=params, session=self.session)
        else:
            self.session['username'] = username
            n = User(username=username,
                         password=make_pw_hash(username, password),
                         email=email)
            n.put()
            self.redirect('/welcome')


class Login(BaseHandler):

    def get(self):
        self.render('login.html', error='', username='', session=self.session)

    def post(self):
        """
        Takes username and password from html form and checks to ensure
        username is in database and hashed password
        matches password stored in database
        """
        # Todo not sure what this below logic is trying to accomplish
        # if not self.session['username']:
        #     return self.redirect('/signup?error')
        username = self.request.get('username')
        password = self.request.get('password')
        user_query = User.query().filter(User.username==username)
        if user_query.fetch():
            user = user_query.fetch(1)[0]
            given_password = make_pw_hash(
                                          username, password,
                                          salt=user.password.split('|')[1]
                                          )
            if user.password == given_password:
                self.session['username'] = username
                self.session['email'] = user.email
                return self.redirect('/welcome')
        return self.render('login.html', username=username, session=self.session,
                    error='Incorrect username/ password combo')


class Logout(BaseHandler):
    def get(self):
        self.render('logout.html', error='', username='', session=self.session)

    def post(self):
        if self.session['username']:
            self.session['username'] = ''
            self.session['email'] = ''
            self.redirect('/')
        else:
            self.render('login.html', username=username,
                        error='You were never logged in to being with!',
                        session=self.session)

class NewPost(BaseHandler):
    def get(self):
        if not 'username' in self.session:
            error = 'You need to login or signup to post!'
            return self.redirect('/signup?error=' + error)
        return self.render('create_new.html', session=self.session, error='')

    def post(self):
        title = self.request.get('title')
        num = self.request.get('like')
        print "### %s" % num
        message = self.request.get('message')
        if title and message:
            a = Post(title=title,
                         message=message,
                         username=self.session['username'],
                         )
            a.put()
            key = convert_ndb_key(a.key)
            self.redirect('/article?key=' + str(key))
        else:
            self.render('home.html', title='', message='', congrats='Hello!',
                        error="You need to enter both title and message!",
                        session=self.session, num=num)

class Article(BaseHandler):
    def get(self):
        #todo get key from parameter sent to article handler
        key = int(self.request.get('key'))
        post = ndb.Key('Post', key).get()
        print key
        print post
        self.render('article.html', session=self.session, post=post)

    def post(self):
        title = self.request.get('comment')
        username = self.session.get('username')
        if title and username:
            a = Comment(comment=comment,
                            username=username
                           )
            a.put()
        else:
            print 'Error Comment not inserted.'


class Profile(BaseHandler):
    def get(self):
        username = self.session['username']
        user = User.query().filter(User.username==username).fetch(1)[0]
        posts = Post.query().filter(Post.username==username).fetch()
        num_posts = len(posts)
        self.render('profile.html', user=user,
                    posts=posts, num_posts=num_posts, session=self.session)


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
                               ('/welcome', Welcome),
                               ('/signup', Signup),
                               ('/test', TestPage),
                               ('/login', Login),
                               ('/newpost', NewPost),
                               ('/logout', Logout),
                               ('/article', Article),
                               ('/profile', Profile)],
                              config=config,
                              debug=True)
