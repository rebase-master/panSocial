from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
followers = Table('followers', pre_meta,
    Column('follower_id', INTEGER(display_width=11)),
    Column('followed_id', INTEGER(display_width=11)),
)

post = Table('post', pre_meta,
    Column('id', INTEGER(display_width=11), primary_key=True, nullable=False),
    Column('body', VARCHAR(length=140)),
    Column('timestamp', DATETIME),
    Column('user_id', INTEGER(display_width=11)),
)

user = Table('user', pre_meta,
    Column('id', INTEGER(display_width=11), primary_key=True, nullable=False),
    Column('nickname', VARCHAR(length=64)),
    Column('email', VARCHAR(length=120)),
    Column('role', SMALLINT(display_width=6)),
    Column('about_me', VARCHAR(length=140)),
    Column('last_seen', DATETIME),
)

user = Table('user', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('fullname', String(length=64)),
    Column('username', String(length=64)),
    Column('email', String(length=120)),
    Column('location', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['followers'].drop()
    pre_meta.tables['post'].drop()
    pre_meta.tables['user'].columns['about_me'].drop()
    pre_meta.tables['user'].columns['last_seen'].drop()
    pre_meta.tables['user'].columns['nickname'].drop()
    pre_meta.tables['user'].columns['role'].drop()
    post_meta.tables['user'].columns['fullname'].create()
    post_meta.tables['user'].columns['location'].create()
    post_meta.tables['user'].columns['username'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['followers'].create()
    pre_meta.tables['post'].create()
    pre_meta.tables['user'].columns['about_me'].create()
    pre_meta.tables['user'].columns['last_seen'].create()
    pre_meta.tables['user'].columns['nickname'].create()
    pre_meta.tables['user'].columns['role'].create()
    post_meta.tables['user'].columns['fullname'].drop()
    post_meta.tables['user'].columns['location'].drop()
    post_meta.tables['user'].columns['username'].drop()
