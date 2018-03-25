import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'DASA23sAdDaDSaer21esdA'
    UPLOAD_CLUSTER = './result/model/cluster/'
    UPLOAD_VEKTOR = './result/model/vektor/'
    UPLOAD_2D = './result/model/2d/'
    UPLOAD_IMAGE_VEKTOR = './app/static/img/analisis/vektor/'
    UPLOAD_IMAGE_CLUSTER = './app/static/img/analisis/cluster/'
    UPLOAD_IMAGE_HIRARKI = './app/static/img/analisis/hirarki/'
    UPLOAD_CORPORA = './result/corpora/'
    UPLOAD_DICTIONARY = './result/model/dictionary/'
    UPLOAD_BOKEH = './result/model/bokeh/'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[Admin]'
    FLASKY_MAIL_SENDER = 'mustofahisyam13@gmail.com'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'mysql+pymysql://root@localhost/latihan_dev'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'mysql+pymysql://root@localhost/latihan_test'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('PRODUCT_DATABASE_URL') or \
                              'mysql+pymysql://root@localhost/latihan'

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production' : ProductionConfig,

    'default': DevelopmentConfig
}