import re
from functools import wraps
from flask import flash, redirect, url_for
from flask import session as login_session

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def slugify(text, delim=u'-'):
    '''Generates an ASCII-only slug.
    ref: http://flask.pocoo.org/snippets/5/
    '''
    result = []
    for word in _punct_re.split(text.lower()):
        if word:
            result.append(word)
    return delim.join(result)[:40]


def login_required(f):
    '''A decorator that checks if user is logged in.
    ref: http://flask.pocoo.org/docs/0.10/patterns/viewdecorators/#login-required-decorator
    '''
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if login_session.get('user_id') is None:
            flash('Please log in to perform this action.')
            return redirect(url_for('show_homepage'))
        return f(*args, **kwargs)
    return decorated_function
