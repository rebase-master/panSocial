from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    fullname = db.Column(db.String(64))
    username = db.Column(db.String(64), index = True, unique = True)
    email = db.Column(db.String(120), index = True, unique = True)
    location = db.Column(db.String(120), index = True)
    photo = db.Column(db.String(255))

    def __init__(self , username ,fullname , email,location,photo):
        self.username = username
        self.email = email
        self.fullname = fullname
        self.location = location
        self.photo = photo

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    @staticmethod
    def get_photo(self):
        return self.photo

    def __repr__(self):
        return '<Username %r, Fullname %r Photo %r>' % (self.username, self.fullname, self.photo)
class Comment(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    photo_id = db.Column(db.Integer, index=True)
    body = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'))

    @staticmethod
    def get_comments(self,photo_id):
        return db.session.query(User.username, User.fullname,User.photo, Comment.body, Comment.timestamp, Comment.id, Comment.uid).filter(User.id==Comment.uid).filter(Comment.photo_id==photo_id).all()

    def __repr__(self):
        return '<Body %r, Id %r, Created %r, Photo %r>' % (self.body, self.id, self.timestamp, User.get_photo(User))

class UserActivity(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'))
    activity = db.Column(db.String(255))
    photo_id = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime)

    @staticmethod
    def get_activity(self):
        return db.session.query(User.username, UserActivity.activity, UserActivity.photo_id, UserActivity.timestamp).filter(User.id==UserActivity.uid).order_by(UserActivity.timestamp.desc()).limit(10).all()
    @staticmethod
    def get_my_activity(self, uid):
        return db.session.query(User.username, UserActivity.activity, UserActivity.photo_id, UserActivity.timestamp).filter(User.id==UserActivity.uid).filter(User.id==uid).order_by(UserActivity.timestamp.desc()).limit(10).all()
