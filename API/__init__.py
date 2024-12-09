from flask import Flask
def create_app(config_name):
    app = Flask (__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///labart.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/labart_api'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['FLASK_RUN_PORT'] = 5001

    app.config['JWT_SECRET_KEY']='frase-secreta'
    app.config['PROPAGATE_EXCEPTIONS']= True
    return app
