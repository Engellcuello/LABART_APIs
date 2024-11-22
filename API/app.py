from API import create_app
from API.modelos.modelos import Asistente,Estado,Sexo,Reaccion,Usuario
from.modelos import db
from flask_restful import Api
from .vistas import VistaAsistente,VistaAsistente_All,VistaEstado,VistaEstado_All,VistaSexo,VistaSexo_All,VistaReaccion,VistaReaccion_All,VistaUsuario_All,VistaLogin,VistaSignin
from flask_jwt_extended import JWTManager
#from modelos import db
app = create_app('default')
app_context = app.app_context()
app_context.push()
db.init_app(app)
db.create_all()

api = Api(app)
api.add_resource(VistaAsistente_All, '/asistente')

api.add_resource(VistaAsistente, '/asistente/<int:id>')

api.add_resource(VistaEstado, '/estado/<int:id>')

api.add_resource(VistaEstado_All, '/estado')

api.add_resource(VistaSexo, '/sexo/<int:id>')

api.add_resource(VistaSexo_All, '/sexo')

api.add_resource(VistaReaccion,'/reaccion/<int:id>')

api.add_resource(VistaReaccion_All,'/reaccion')

api.add_resource(VistaUsuario_All, '/usuario')

api.add_resource(VistaSignin, '/signin')

api.add_resource(VistaLogin, '/login')


jwt = JWTManager(app)