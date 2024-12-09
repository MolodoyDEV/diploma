from app import db

users_and_roles = db.Table(
    'users_and_roles', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id')),
)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    roles = db.relationship('Role', secondary=users_and_roles)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32), unique=True, nullable=False)
    users = db.relationship('User', secondary=users_and_roles)


class Settings(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32), unique=True, nullable=False)
    description = db.Column(db.String(256), nullable=True)
    value = db.Column(db.String(256), nullable=False)
