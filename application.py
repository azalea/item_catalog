import datetime
import random
import string
import httplib2
import json
import re
import os
import uuid
import requests
from flask import Flask, make_response, render_template, request, redirect
from flask import url_for, flash, jsonify, send_from_directory
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from werkzeug import secure_filename
from urlparse import urljoin
from werkzeug.contrib.atom import AtomFeed

from jinja2 import evalcontextfilter, Markup, escape

from utils import login_required
import database_operation as dbo

client_id = json.loads(open('client_secrets.json').read())['web']['client_id']

# Settings for image upload
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


@app.context_processor
def inject_context():
    '''Make categories available to all templates'''
    return dict(categories=dbo.get_categories())


@app.template_filter()
@evalcontextfilter
def as_paragraph(eval_ctx, value):
    '''A context filter to convert line break into paragraphs'''
    paragraphs = re.split(r'\r\n|\r|\n', value)
    result = ''.join(['<p>%s</p>' % p for p in paragraphs])
    if eval_ctx.autoescape:
        result = Markup(result)
    return result


def get_csrf_token():
    '''Generate a random alphanumeric string to serve as an identifier
    to protect against cross-site request forgery (csrf).'''
    return ''.join(random.choice(string.ascii_uppercase + string.digits)
                   for x in range(32))


@app.route('/uploads/<path:filename>')
def send_uploads(filename):
    '''Serve files in uploads folder'''
    print filename
    return send_from_directory('uploads', filename)


@app.route('/')
def show_homepage():
    items = dbo.get_latest_items()
    return render_template('home.html', items=items)


@app.route('/category/<int:category_id>/<slug>')
@app.route('/category/<int:category_id>/<slug>/items')
def show_category(category_id, slug):
    category = dbo.get_category(category_id)
    items = dbo.get_items(category_id)
    return render_template('category.html', category=category, items=items)


@app.route('/category/<int:category_id>/<slug>/item/<int:item_id>')
@app.route('/category/<int:category_id>/<slug>/item/<int:item_id>/<item_slug>')
def show_item(category_id, slug, item_id, item_slug=None):
    item = dbo.get_item(category_id, item_id)
    return render_template('item.html', item=item)


def _allowed_file(filename):
    '''Helper function to test whether filename has allowed extensions'''
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/item/new', methods=['GET', 'POST'])
@login_required
def add_item():
    if request.method == 'POST':
        picture_file = request.files['picture']
        if picture_file and _allowed_file(picture_file.filename):
            filename = str(uuid.uuid4()) + \
                secure_filename(picture_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            picture_file.save(filepath)
        else:
            filename = ''
        dbo.create_item(category_id=request.form['category_id'],
                        user_id=login_session['user_id'],
                        name=request.form['name'],
                        description=request.form['description'],
                        picture=filename
                        )
        flash('New item %s is successfully added' % request.form['name'])
        return redirect(url_for('show_homepage'))
    else:
        return render_template('add_item.html')


@app.route(
    '/category/<int:category_id>/<slug>/item/<int:item_id>/edit',
    methods=['GET', 'POST'])
@app.route(
    '/category/<int:category_id>/<slug>/item/<int:item_id>/<item_slug>/edit',
    methods=['GET', 'POST'])
@login_required
def edit_item(category_id, slug, item_id, item_slug=None):
    item = dbo.get_item(category_id, item_id)
    if login_session.get('user_id') != item.user_id:
        flash('Sorry you cannot edit item created by another user.')
        return redirect(url_for(
            'show_item', category_id=item.category_id,
            slug=item.category.slug, item_id=item_id, item_slug=item.slug))
    if request.method == 'POST':
        picture_file = request.files['picture']
        if picture_file and _allowed_file(picture_file.filename):
            filename = str(uuid.uuid4()) + \
                secure_filename(picture_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            picture_file.save(filepath)
        else:
            filename = ''
        if filename:
            original_filepath = os.path.join(
                app.config['UPLOAD_FOLDER'], item.picture)
            os.remove(original_filepath)
        category_id = request.form['category_id']
        name = request.form['name']
        description = request.form['description']
        edited_item = dbo.edit_item(
            item_id, category_id, name, description, filename)
        flash('Item %s is successfully edited.' % edited_item.name)
        return redirect(url_for(
            'show_item', category_id=edited_item.category_id,
            slug=edited_item.category.slug, item_id=edited_item.id,
            item_slug=edited_item.slug))
    else:
        return render_template(
            'edit_item.html', category_id=category_id, item=item)


@app.route(
    '/category/<int:category_id>/<slug>/item/<int:item_id>/delete',
    methods=['GET', 'POST'])
@app.route(
    '/category/<int:category_id>/<slug>/item/<int:item_id>/<item_slug>/delete',
    methods=['GET', 'POST'])
@login_required
def delete_item(category_id, slug, item_id, item_slug=None):
    item = dbo.get_item(category_id, item_id)
    if login_session.get('user_id') != item.user_id:
        flash('Sorry you cannot delete item created by another user.')
        return redirect(url_for(
            'show_item', category_id=item.category_id,
            slug=item.category.slug, item_id=item_id,
            item_slug=item.slug))

    if request.method == 'POST':
        # Make sure csrf_token matches,
        # to protect against cross-site request forgery
        if request.form['csrf_token'] != login_session['csrf_token']:
            response = make_response(json.dumps('Invalid csrf token'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        if item.picture:
            original_filepath = os.path.join(
                app.config['UPLOAD_FOLDER'], item.picture)
            os.remove(original_filepath)
        name = item.name
        slug = item.category.slug
        dbo.delete_item(category_id, item_id)
        flash('Item %s is successfully deleted.' % name)
        return redirect(url_for(
            'show_category', category_id=category_id, slug=slug))
    else:
        # Generate csrf_token, and pass it to html form,
        # to protect against cross-site request forgery
        csrf_token = get_csrf_token()
        login_session['csrf_token'] = csrf_token
        return render_template('delete_item.html',
                               category_id=category_id,
                               item=item,
                               csrf_token=csrf_token)


def _make_external(url):
    '''Make a reletive url as external.
    ref: http://flask.pocoo.org/snippets/10/'''
    return urljoin(request.url_root, url)


@app.route('/recent.atom')
def show_recent_feed():
    '''Create Atom feed.
    ref: http://flask.pocoo.org/snippets/10/'''
    feed = AtomFeed('Recent Items',
                    feed_url=request.url, url=request.url_root)
    items = dbo.get_latest_items()
    for item in items:
        feed.add(item.name, item.description,
                 content_type='html',
                 author=item.user.name,
                 url=_make_external(url_for(
                     'show_item', category_id=item.category_id,
                     slug=item.category.slug,
                     item_id=item.id)),
                 updated=datetime.datetime.now(),
                 )
    return feed.get_response()


@app.route('/catalog.json')
def show_catalog_json():
    categories = dbo.get_categories()
    return jsonify(Category=[c.serialize for c in categories])


@app.route('/category/<int:category_id>/<slug>/items.json')
def show_category_json(category_id, slug):
    category = dbo.get_category(category_id)
    return jsonify(Category=category.serialize)


@app.route('/category/<int:category_id>/<slug>/<int:item_id>.json')
@app.route('/category/<int:category_id>/<slug>/<int:item_id>/<item_slug>.json')
def show_item_json(category_id, slug, item_id, item_slug=None):
    item = dbo.get_item(category_id, item_id)
    return jsonify(Item=item.serialize)


@app.route('/login')
def login():
    state = get_csrf_token()
    login_session['state'] = state
    return render_template('login.html', state=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    # Exchange client token for long-lived server-side token
    secret_data = json.loads(open('fb_client_secrets.json', 'r').read())
    app_id = secret_data['web']['app_id']
    app_secret = secret_data['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?'
    url += 'grant_type=fb_exchange_token'
    url += '&client_id={0}&client_secret={1}&fb_exchange_token={2}'.format(
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # Strip expire tag from access_token
    token = result.split('&')[0]

    url = 'https://graph.facebook.com/v2.5/me?'
    url += '{0}&fields=name,id,email,picture'.format(
        token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    print 'ddddddaata', data
    login_session['provider'] = 'facebook'
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['facebook_id'] = data['id']
    login_session['picture'] = data['picture']['data']['url']
    login_session['access_token'] = token
    user_id = dbo.get_user_id(data['email'])
    if user_id is None:
        user_id = dbo.create_user(login_session)
    login_session['user_id'] = user_id

    flash('you are now logged in as {username}'.format(
        username=login_session['username']))
    print "done!"
    return _get_welcome_message()


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must be included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "You have been logged out"


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        print 'Failed to upgrade the authorization code.'
        return response
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != client_id:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = dbo.get_user_id(data['email'])
    if user_id is None:
        user_id = dbo.create_user(login_session)
    login_session['user_id'] = user_id

    flash('you are now logged in as {username}'.format(
        username=login_session['username']))
    return _get_welcome_message()


def _get_welcome_message():
    '''Helper function to specify the welcome message'''
    output = '<h1> Welcome, {username}!</h1>'.format(
        username=login_session['username'])
    output += '<img src = "{picture}" style = "width: 300px; height: 300px;'
    output += 'border - radius: 150px;-webkit - border - radius: 150px;'
    output += '-moz - border - radius: 150px; ">'.format(
        picture=login_session['picture'])
    return output


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps('Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    if access_token is None:
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')
    result = result[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/logout')
def logout():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
    flash('You are successfully logged out.')
    return redirect(url_for('show_homepage'))


if __name__ == '__main__':
    app.secret_key = 'a super secret key'
    app.debug = False
    app.run(host='0.0.0.0', port=8000)
