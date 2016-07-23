
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


# Decorator functions for request Handler
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
    def func_wrapper(*args, **kwargs):
        self = args[0]
        username = args[1].username
        if self.session['username'] != username:
            # TODO what do you do if user doesn't have permission?
            error = 'You don\'t have permission to edit this object!'
            print error
            warnings.warn(error)
            return self.get(error=error)
        else:
            return func(*args, **kwargs)
    return func_wrapper

# Jinja2 filter allowing use of ndb Keys as div ids in html templates
def filterKey(Key):
    """converts ndb Key object to str object for use in jinja filters"""
    return int(str((Key)).split(', ')[1][:-1])


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
    """Class that contains all CRUD methods"""

    def parse_AJAX(self):
        """
        Helper method for CRUD updates. Converts AJAX request from JSON to
        datatypes useful for database access
        """
        key = int(self.request.get('key'))
        action = self.request.get('action')
        data = self.request.get('data')
        post = ndb.Key('Post', key).get()
        user = User.query().filter(
            User.username == post.username
        ).fetch()[0]
        return action, user, post, data

    def new_comment(self, user, post, data, *args):
        n = Comment(username=user.username,
                    comment=data)
        post.comments.append(n)
        post.put()
        key = str(filterKey(post.key))
        return self.redirect('/article?key=' + key)

    @permissions_check
    def edit_comment(self, user, post, data, *args):
        new_comment = self.request.get('edit_comment')
        old_comment = self.request.get('data')
        print '###', old_comment, new_comment
        comment = [c for c in post.comments if c.comment == old_comment][0]
        index = post.comments.index(comment)
        post.comments[index].comment = new_comment
        post.put()
        key = str(filterKey(post.key))
        return self.redirect('/article?key=' + key)

    @permissions_check
    def delete_comment(self, user, post, data, *args):
        post.comments = [c for c in post.comments if c.comment != data]
        post.put()

    @permissions_check
    def edit_article(self, user, post, data, *args):
        print '### called'
        post.message = data
        post.title = self.request.get('title')
        post.put()
        action = self.request.get('action')
        return self.redirect('/article?key=' + str(filterKey(post.key)))

    @permissions_check
    def delete_article(self, user, post, *args):
        print 'delete method called'
        post.key.delete()
        return self.redirect('/')

    # function that will call correct method above using request inputs
    @login_required
    def CRUD_action(self):
        print 'crud action called'
        action, user, post, data = self.parse_AJAX()
        print action, user
        getattr(self, action)(user, post, data)
        key = str(filterKey(post.key))
        return self.redirect('/')

    # not CRUD methods

    def add_like(self, action, user, post):
        print 'add like called'
        if filterKey(user.key) not in post.likes:
            post.likes.append(filterKey(user.key))
            post.put()
        if filterKey(post.key) not in user.likes:
            user.likes.append(filterKey(post.key))
            user.put()
        json_string = {'num_likes': len(post.likes)}
        print json_string
        self.write(json.dumps(json_string))

    # def unlike(self, post, user, *args):
    #     print 'this func'
    #     curr_user = User.query().filter(
    #         User.username == self.session.get('username')
    #     ).fetch()[0]
    #     post.likes = set(
    #         [c for c in post.likes if c != filterKey(curr_user.key)]
    #     )
    #     post.put()
    #     curr_user.likes = set(
    #         [c for c in curr_user.likes if c != filterKey(post.key)]
    #     )
    #     user.put()
    #     print len(post.likes)
    #     # json_string = {'likes': post.likes,
    #     #                'num_likes': len(post.likes)}
    #     # return self.write(json.dumps(json_string))


class DataController(CRUDHandler):
    """this class would handle all the data calls from the Javascript front
        end controller"""


class MainPage(CRUDHandler):

    def get(self, error=''):
        posts = Post.query().order(-Post.created_at)
        self.render('home.html', posts=posts,
                    error=error, session=self.session)

    def post(self):
        print self.request.get('likes')
        likes = self.request.get('likes')
        return self.CRUD_action()

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


class Article(CRUDHandler):

    def get(self):
        key = int(self.request.get('key'))
        post = ndb.Key('Post', key).get()
        self.render('article.html', session=self.session, post=post)

    @login_required
    def post(self):
        return self.CRUD_action()


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
