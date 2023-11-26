#!/usr/bin/python3
# -*-coding:iso-8859-15-*-
# -*- coding: utf-8 -*-
# -*- coding: 850 -*-
# -*- coding: cp1252 -*-

#from DirectionsIO import coinDroppedBySelf
#from DirectionsIO import createOrders
from itertools import cycle
import smtplib
from traceback import print_tb
from flask import Flask, jsonify, request, Response
from werkzeug.wrappers import ResponseStream, response
import BackEnd.generalInfo.KeysIO as globalInfo
import BackEnd.generalInfo.ResponseMessages as ResponseMessages
import importlib
import random
import hashlib

#from pymongo import MongoClient
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import email
import email.mime.application
# from datetime import datetime
import datetime
'''
import BackEnd.generalInfo.FuncionesCRON as funcionesCron
import BackEnd.pdfReportGenerator as reporte
import BackEnd.MailServer as MailServer
#### Librerias para fechas
import datetime
from datetime import date, timedelta
import time
'''
import requests
import urllib.request

import jwt

import json
import sys
import base64
import os
import uuid
import linecache
import pymysql.cursors

from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/var/www/html/profiles'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

versionApp = 1.0

# Connection for DB
def getConectionMYSQL():
	return pymysql.connect(host=globalInfo.strDBHost,port=globalInfo.strDBPort,
                             user=globalInfo.strDBUser,
                             password=globalInfo.strDBPassword,
                             db=globalInfo.strDBName,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
MysqlCnx = getConectionMYSQL()
cursor = MysqlCnx.cursor()
cursor.execute("SELECT * FROM oferta;")
print(getConectionMYSQL())
print(MysqlCnx)
#################################################################################
# FUNCIONES DE USO GENERAL
#################################################################################


def fnGetTest():
    try:
        ##print("degug ok en fngetTest")
        return {"intResponse": 200, "strAnswer": "Respuesta Exitosa", "jsnAnswer": 7}

    except Exception as e:
        # PrintException()
        return {"intResponse": 500, "strAnswer": "Error en servidor"}
    finally:
        print("mns finallly")

# CREATED BY: DCM
# MODIFY BY:
# SUMMARY: funcion para validar login de usuario


def canUserAccess(strCorreo):
    try:

        #strPass = dbConnLocal.clUsers.find_one({'userid': strCorreo}, {'_id':0, 'userid':0})

        if(strPass != None):
            #print'Email registered')
            #password = str(strPass['pass'])
            return {'intResponse': 200, 'strAnswer': 'Usuario registrado', 'strPassRecover': 1}
        else:
            print("Email unregistered")
            return {'intResponse': 404, 'strAnswer': 'Usuario no registrado', 'strPassRecover': None}

    except Exception as e:
        print(e)
        return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}

# CREATED BY: DCM
# MODIFY BY:
# SUMMARY: funcion para validar login de usuario



def fnSetCandidato(nombreCandidato, correo, password, telefono, discapacidad,curriculum):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (nombreCandidato, correo, password, telefono, discapacidad,curriculum)
		cursor.callproc("sp_setCandidato",params)
		jsnRows = cursor.fetchall()
		return {'intResponse': 200, 'strAnswer': jsnRows}

	except Exception as e:
		print(e)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}

def fnUpdateOferta(idOferta,idEmpresa, tituloOferta, ubicacion, descripcion, requisito,actividad,salario,arrCategorias):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (idOferta,idEmpresa, tituloOferta, ubicacion, descripcion, requisito,actividad,salario,arrCategorias)
		cursor.callproc("sp_updateOferta",params)
		jsnRows = cursor.fetchall()
		return {'intResponse': 200, 'strAnswer': jsnRows}

	except Exception as e:
		print(e)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}
def fnDeleteOferta(idOferta):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (idOferta)
		cursor.callproc("sp_deleteOferta",[params])
		jsnRows = cursor.fetchone()
		return {'intResponse': 200, 'strAnswer': jsnRows}

	except Exception as e:
		print(e)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}
	
def fnGetCandidatosByOferta(idOferta):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (idOferta)
		cursor.callproc("sp_getCandidatosByOferta",[params])
		jsnRows = cursor.fetchone()
		return {'intResponse': 200, 'strAnswer': jsnRows}

	except Exception as e:
		print(e)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}
