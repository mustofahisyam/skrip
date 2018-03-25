from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin
from . import db, login_manager



class Fitur:
    Dashboard = ('Dashboard', 'main.index')
    Analisis = ('Analisis', 'analisis.index')
    Akun = ('Kelola','adminis.index')
    Hasil = ('Hasil', 'hasil.index')
    Keluar = ('Log Out', 'auth.logout')


class Permission:
    GENERAL = 0x01
    ANALISIS = 0x02
    KELOLA =  0x04
        

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='joined')

    def permission(self):
        if self.id == 1:
            return [Fitur.Dashboard, Fitur.Akun]
        else:
            return [Fitur.Dashboard, Fitur.Analisis, Fitur.Hasil]

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def verify_password(self, password):
        return self.password == password

    def hak(self, permissions):
        return self.role is not None and \
                (self.role.permissions & permissions) == permissions
    
    def __repr__(self):
        return '<User %r>' % self.username


class Vectorspace(db.Model):
    __tablename__ = 'vectorspaces'
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(64), unique=True)

    def __repr__(self):
        return '<Vektor %r>' % self.nama


class Klustermodel(db.Model):
    __tablename__ = 'klustermodels'
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(64), unique=True)
    active = db.Column(db.Integer)
    kelompoks = db.relationship('Kelompok', backref='klustermodel', lazy='joined')

    def __repr__(self):
        return '<Kluster %r>' % self.nama
        

class Kelompok(db.Model):
    __tablename__ = 'kelompoks'
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.Integer)
    kuncikata = db.Column(db.String(128))
    warna = db.Column(db.String(32))
    klustermodel_id = db.Column(db.Integer, db.ForeignKey('klustermodels.id'))
    cleandatas = db.relationship('Cleandata', backref='kelompok', lazy='joined')

    def __repr__(self):
        return '<Kelompok %r>' % self.nama


class Cleandata(db.Model):
    __tablename__ = 'cleandatas'
    id = db.Column(db.Integer, primary_key=True)
    pertanyaan = db.Column(db.String(256))
    data_asli = db.Column(db.String(256))
    kelompok_id = db.Column(db.Integer, db.ForeignKey('kelompoks.id'))

    def __repr__(self):
        return '<Data %r>' % self.pertanyaan


    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


