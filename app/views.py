import urllib
from flask import render_template, redirect, url_for, request, g, jsonify, json
from flask.ext.login import login_user, logout_user, current_user
from app import app, db,lm
from models import User, Comment, UserActivity
from datetime import datetime
from geopy import geocoders

# Add the current user to the global object
# If user is authenticated, add user activity and the
# logged in user activity to the global object
@app.before_request
def before_request():
    g.user = current_user
    if g.user is not None and g.user.is_authenticated():
        g.activity = UserActivity.get_activity(UserActivity)
        g.my_activity = UserActivity.get_my_activity(UserActivity, g.user.id)
    else:
        g.activity = None
        g.my_activity = None

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

# Render the hompage
# Redirect logged in user to popular page
@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('stream', category='popular'))
    return render_template('index.html')

# Load the photos for the specified geocodes from Panoramio API
# Render recent or popular template depending on the category param
@app.route('/stream/<string:category>', methods=['GET'])
def stream(category):
    if category == 'popular' or category == 'recent':
        if category == 'popular':
            mode = 'public'
        else:
            mode = 'full'

        if g.user.is_authenticated():
            g.user = current_user
            minx = (float)(g.user.location.split(",",2)[0])
            miny = (float)(g.user.location.split(",",2)[1])
        else:
            minx = 12.97160
            miny = 77.59456
        maxx = minx+30.0
        maxy = miny+30.0
        params = urllib.urlencode({'set': mode, 'from': 0, 'to': 20, 'minx': minx, 'miny': miny, 'maxx': maxx, 'maxy': maxy, 'size':'medium', 'mapfilter': 'true'})
        result = urllib.urlopen("http://www.panoramio.com/map/get_panoramas.php?%s" % params)
        data = json.loads(result.read())
        for photo in data['photos']:
            comment = Comment.get_comments(Comment, int(photo['photo_id']))
            if len(comment) != 0:
                photo['comments'] = comment
            else:
                photo['comments'] = None

        return render_template('stream.html',
                               user = g.user,
                               data=data,
                               cat=category,
                               activity=g.activity,
                               myActivity=g.my_activity)
    return render_template('404.html')

# Receive photo_id, comment from AJAX request and add comment to DB
@app.route('/comment', methods=['POST'])
def addComment():
    data = json.loads(request.get_data())
    photo_id = data['photo_id']
    body = data['comment']
    comment = Comment(photo_id=photo_id, body=body, timestamp=datetime.utcnow(), uid=g.user.id)
    activity = UserActivity(uid=g.user.id, activity="commented on", photo_id=photo_id, timestamp=datetime.utcnow())
    db.session.add(comment)
    db.session.add(activity)
    db.session.commit()

    return jsonify(id= comment.id, fullname=g.user.fullname, photo=g.user.photo)

# Delete comment specified by the id parameter
@app.route('/comment/<int:id>', methods=['DELETE'])
def deleteComment(id):
    comment = Comment.query.filter_by(id= id).first()
    if comment is None:
        return jsonify(msg=-1)
    db.session.delete(comment)
    db.session.commit()
    return jsonify(msg=1)

# Convert the location name received in the POST request to geocodes
# render Search page to display location on the map based on the geocodes
@app.route("/search", methods=['GET','POST'])
def search():
    if request.method == 'POST':
        search_for = request.form['search']
        g = geocoders.GoogleV3()
        t = g.geocode(search_for)
        if t is not None:
            place, (lat,lng) = g.geocode(search_for)
        else:
            place=lat=lng="null"

        return render_template('search.html',
                               data=search_for,
                               place=place,
                               lat=lat,
                               lng=lng)
    return render_template('search.html')

# Log user into the system if username received from the AJAX request is found
@app.route('/login', methods=['POST'])
def login():
    data = json.loads(request.get_data())
    username = data['username']
    user = User.query.filter_by(username = username).first()
    if user is None:
        return jsonify(msg=-1)
    db.session.add(user)
    db.session.commit()
    g.user = user
    g.user.username = user.username
    db.session.add(g.user)
    db.session.commit()
    login = login_user(user,force=True)
    return jsonify(msg=login)

# Log user out of the system
@app.route('/logout')
def logout():
    logout_user()
    return jsonify(msg="You have been logged out!")

# Register user into the system by the information received from the AJAX POST request
@app.route('/register', methods=['POST'])
def register():
    data = json.loads(request.get_data())
    username = data['username']
    user = User.query.filter_by(username = username).first()
    if user is None:
        fullname = data['fullname']
        email = data['email']
        location = data['location']
        photo = 'https://graph.facebook.com/'+username+'/picture'
        user = User(fullname = fullname, username = username, email = email, location = location, photo = photo)
        db.session.add(user)
        db.session.commit()

        g.user = user
        db.session.add(g.user)
        db.session.commit()
        login_user(user,force=True)
        return jsonify(msg=1);
    return jsonify(msg="You have already signed up for panSocial!")

# Render custom template for resource not found error
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

# Render custom template for internal server error error
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500