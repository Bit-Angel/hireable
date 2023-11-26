from sys import int_info
from gevent import monkey
monkey.patch_all()
from flask import Flask, jsonify, request
from flask.json import JSONDecoder
from werkzeug.wrappers import Response, response
from flask_socketio import SocketIO, join_room, leave_room
from flask_cors import CORS
import json
#import socketio
####Imports de los archivos principales
import BackEnd.generalInfo.ResponseMessages as ResponseMessages
import BackEnd.FunctionsIO  as callMethod


usersConnected = {}

users = {
    "betomper@gmail.com": "qwerty",
    "prueba@gmail.com": "prueba123",
    "hola@gmail.com": "hola123"
}

app = Flask(__name__)
CORS(app)
#manage_session para poder utilizar sockets y apis
socketio = SocketIO(app, cors_allowed_origins="*", manage_session=False, async_mode='gevent')
#sio = socketio.Server()
#app = socketio.WSGIApp(socketio)
#enviroment = config['development']
#app = create_app(enviroment)


@app.route('/apiGet/<strId>', methods=['GET'])
def ApiGet(strId):
    try:
        print("apiGet StrId: ",strId)
        print("ip2: ",request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr))
        return jsonify({'data':{'status': 'succes'}})
    except Exception as exception:
        print('functionApiGet', exception)
        return jsonify({'intResponse':'500','strAnswer':'Server Error.'})

@app.route('/api/general/login/auth', methods=['POST'])
def PostLogin():
    try:
        strEmail = '' if request.json['strEmail'] == None else request.json['strEmail']
        strPassword = '' if request.json['strPassword'] == None else request.json['strPassword']
        print(strEmail,strPassword)
        if strEmail == None or strPassword == None:
           return ResponseMessages.err203
        jsonUser = callMethod.fnLogin(strEmail, strPassword)
        return jsonify(jsonUser)
    except Exception as exception:
         print('funcitionLogin', exception)
         return ResponseMessages.err202

@app.route('/api/general/login/updatePassword', methods=['POST'])
def UpdatePassword():
    try:
        #print(request.json)
        strEmail = '' if request.json['strEmail'] == None else request.json['strEmail']
        userId = '' if request.json['userId'] == None else request.json['userId']
        if strEmail == None:
           return ResponseMessages.err203
        jsonUser = callMethod.updatePassword(strEmail, userId)
        return jsonify(jsonUser)
    except Exception as exception:
         print('funcitionUpdatePassword', exception)
         return ResponseMessages.err202

##Canditado
@app.route('/api/general/candidato/setCandidato', methods=['POST'])
def setCandidato():
    try:
        #print(request.json)
        nombreCandidato = '' if request.json['nombreCandidato'] == None else request.json['nombreCandidato']
        correo = '' if request.json['correo'] == None else request.json['correo']
        password = '' if request.json['password'] == None else request.json['password']
        telefono = '' if request.json['telefono'] == None else request.json['telefono']
        discapacidad = '' if request.json['discapacidad'] == None else request.json['discapacidad']
        curriculum = '' if request.json['curriculum'] == None else request.json['curriculum']
        if nombreCandidato == None:
           return ResponseMessages.err203
        jsonUser = callMethod.fnSetCandidato(nombreCandidato, correo, password, telefono, discapacidad,curriculum)
        return jsonify(jsonUser)
    except Exception as exception:
         print('setCandidato', exception)
         return ResponseMessages.err202
    
##Empresa 
@app.route('/api/general/empresa/setEmpresa', methods=['POST'])
def setEmpresa():
    try:
        #print(request.json)
        nombreEmpresa = '' if request.json['nombreEmpresa'] == None else request.json['nombreEmpresa']
        info = '' if request.json['info'] == None else request.json['info']
        promocion = '' if request.json['promocion'] == None else request.json['promocion']
        if nombreEmpresa == None:
           return ResponseMessages.err203
        jsonUser = callMethod.fnSetEmpresa(nombreEmpresa, info, promocion)
        return jsonify(jsonUser)
    except Exception as exception:
         print('setEmpresa', exception)
         return ResponseMessages.err202
    

##Empleador
@app.route('/api/general/empleador/setEmpleador', methods=['POST'])
def setEmpleador():
    try:
        #print(request.json)
        idEmpresa = '' if request.json['idEmpresa'] == None else request.json['idEmpresa']
        nombreEmpleador = '' if request.json['nombreEmpleador'] == None else request.json['nombreEmpleador']
        correo = '' if request.json['correo'] == None else request.json['correo']
        password = '' if request.json['password'] == None else request.json['password']
        telefono = '' if request.json['telefono'] == None else request.json['telefono']
        if idEmpresa == None:
           return ResponseMessages.err203
        jsonUser = callMethod.fnSetEmpleador(idEmpresa, nombreEmpleador, correo, password, telefono)
        return jsonify(jsonUser)
    except Exception as exception:
         print('setEmpleador', exception)
         return ResponseMessages.err202
    
##Ofertas
@app.route('/api/general/oferta/setOferta', methods=['POST'])
def setOferta():
    try:
        #print(request.json)
        idEmpresa = '' if request.json['idEmpresa'] == None else request.json['idEmpresa']
        tituloOferta = '' if request.json['tituloOferta'] == None else request.json['tituloOferta']
        ubicacion = '' if request.json['ubicacion'] == None else request.json['ubicacion']
        descripcion = '' if request.json['descripcion'] == None else request.json['descripcion']
        requisito = '' if request.json['requisito'] == None else request.json['requisito']
        actividad = '' if request.json['actividad'] == None else request.json['actividad']
        salario = '' if request.json['salario'] == None else request.json['salario']
        arrCategorias = '' if request.json['arrCategorias'] == None else request.json['arrCategorias']
        if idEmpresa == None:
           return ResponseMessages.err203
        jsonUser = callMethod.fnSetOferta(idEmpresa, tituloOferta, ubicacion, descripcion, requisito,actividad,salario,arrCategorias)
        return jsonify(jsonUser)
    except Exception as exception:
         print('setOferta', exception)
         return ResponseMessages.err202

@app.route('/api/general/oferta/updateOferta', methods=['PUT'])
def updateOferta():
    try:
        #print(request.json)
        idOferta = '' if request.json['idOferta'] == None else request.json['idOferta']
        idEmpresa = '' if request.json['idEmpresa'] == None else request.json['idEmpresa']
        tituloOferta = '' if request.json['tituloOferta'] == None else request.json['tituloOferta']
        ubicacion = '' if request.json['ubicacion'] == None else request.json['ubicacion']
        descripcion = '' if request.json['descripcion'] == None else request.json['descripcion']
        requisito = '' if request.json['requisito'] == None else request.json['requisito']
        actividad = '' if request.json['actividad'] == None else request.json['actividad']
        salario = '' if request.json['salario'] == None else request.json['salario']
        arrCategorias = '' if request.json['arrCategorias'] == None else request.json['arrCategorias']
        if idEmpresa == None:
           return ResponseMessages.err203
        jsonUser = callMethod.fnUpdateOferta(idOferta,idEmpresa, tituloOferta, ubicacion, descripcion, requisito,actividad,salario,arrCategorias)
        return jsonify(jsonUser)
    except Exception as exception:
         print('updateOferta', exception)
         return ResponseMessages.err202

@app.route('/api/general/oferta/deleteOferta', methods=['DELETE'])
def deleteOferta():
    try:
        #print(request.json)
        idOferta = '' if request.json['idOferta'] == None else request.json['idOferta']
        if idOferta == None:
           return ResponseMessages.err203
        jsonUser = callMethod.fnDeleteOferta(idOferta)
        return jsonify(jsonUser)
    except Exception as exception:
         print('deleteOferta', exception)
         return ResponseMessages.err202

@app.route('/api/general/oferta/getCandidatosByOferta/<int:idOferta>', methods=['GET'])
def getCandidatosByOferta(idOferta):
    try:
        #print(request.json)
        if idOferta == None:
            return ResponseMessages.err203
        
        jsonUser = callMethod.fnGetCandidatosByOferta(idOferta)
        return jsonify(jsonUser)
    except Exception as exception:
         print('getCandidatosByOferta', exception)
         return ResponseMessages.err202

##SolicitudOferta
@app.route('/api/general/solicitud/setSolicitud', methods=['POST'])
def setSolicitud():
    try:
        #print(request.json)
        idOferta = '' if request.json['idOferta'] == None else request.json['idOferta']
        idCandidato = '' if request.json['idCandidato'] == None else request.json['idCandidato']
        fechaSolicitud = '' if request.json['fechaSolicitud'] == None else request.json['fechaSolicitud']
        if idOferta == None:
           return ResponseMessages.err203
        jsonUser = callMethod.fnSetSolicitud(idOferta, idCandidato, fechaSolicitud)
        return jsonify(jsonUser)
    except Exception as exception:
         print('setSolicitud', exception)
         return ResponseMessages.err202
 
if __name__ == '__main__':
   socketio.run(app, host="0.0.0.0", port=6007, debug=True)
# #if __name__ == '__main__':
   #socketio.run(app, host="192.168.0.4", port=6007, debug=True)

