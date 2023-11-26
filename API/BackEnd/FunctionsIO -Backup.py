#!/usr/bin/python3
# -*-coding:iso-8859-15-*-
# -*- coding: utf-8 -*-
# -*- coding: 850 -*-
# -*- coding: cp1252 -*-

#from DirectionsIO import coinDroppedBySelf
#from DirectionsIO import createOrders
import smtplib
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

#################################################################################
# FUNCIONES DE USO GENERAL
#################################################################################


def fnGetTest():
    try:
        #print("degug ok en fngetTest")
        return {"intResponse": 200, "strAnswer": "Respuesta Exitosa", "jsnAnswer": 7}

    except Exception as e:
        PrintException()
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
            print('Email registered')
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


def fnGetAllUsers1():
	try:
		usersAdministrators = []
		usersFacilitators = []
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		#para usuarions administradores
		_type = 1
		params = (_type)
		#cursor.callproc("sp_getuserbyID",[params])
		cursor.callproc("sp_getallusersByType",[params])
		MysqlCnx.commit()
		jsnRows = cursor.fetchall()
		for objResult in jsnRows:
			usersAdministrators.append(objResult)
		# para usuarios facilitadores
		_type = 2
		params = (_type)
		#cursor.callproc("sp_getuserbyID",[params])
		cursor.callproc("sp_getallusersByType",[params])
		MysqlCnx.commit()
		jsnRows = cursor.fetchall()
		for objResult in jsnRows:
			usersFacilitators.append(objResult)
		# para usuarios facilitadores
		_type = 6
		params = (_type)
		#cursor.callproc("sp_getuserbyID",[params])
		cursor.callproc("sp_getallusersByType",[params])
		MysqlCnx.commit()
		jsnRows = cursor.fetchall()
		for objResult in jsnRows:
			usersFacilitators.append(objResult)
		for facilitator in usersFacilitators:
			jsonResponse = fnGetWorkShopsClosedByFacId(facilitator['UserID'])
			if(jsonResponse['intResponse'] == 200):
				facilitator['WorkShopClosed'] = jsonResponse['WorkShopsClosed']
			else:
			 	facilitator['WorkShopClosed'] = 0 
		return {'intResponse': 200, 'usersAdministrators': usersAdministrators, 'usersFacilitators': usersFacilitators,}
	except Exception as e:
		print(e)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}


'''****************************************************************************
   * Author: BPR
   * Date: 14/04/2021
   * Summary: <Obtener Numero de WorkShops Cerrados>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnGetWorkShopsClosedByFacId(facilitatorId):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (facilitatorId)
		cursor.callproc("sp_getNumWorkShopsClosedByFacId", [params])
		jsonRows = cursor.fetchall()
		#print("jsonRows",jsonRows)
		return {'intResponse': 200, 'WorkShopsClosed': jsonRows[0]['WorkShopsClosed']}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
   * Author: AJLL
   * Date: 26/02/2021
   * Summary: <Enviar correo al usuario con una nueva contrasena>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''

def 	updatePassword(email,userId):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (email, userId, 0)
		cursor.callproc("sp_getUserByEmail",params)
		MysqlCnx.commit()
		jsonRow = cursor.fetchone()
		print("responseGetuserbyEmail:",jsonRow)
		if jsonRow == None:
			return ({'intResponse': '203', 'strAnswer': 'Email not found'})
		newPassword = ''
		for i in range(4):
			n = random.randint(0,9)
			newPassword += str(n)
		strBodyUpdatePassword = '''
		<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
		<html>

		<head>
			<meta http-equiv="CONTENT-TYPE" content="text/html; charset=utf-8" />
			<title></title>
			<meta name="GENERATOR" content="LibreOffice 4.1.6.2 (Linux)" />
			<meta name="AUTHOR" content="Salvador" />
			<meta name="CREATED" content="20210305;172800000000000" />
			<meta name="CHANGED" content="0;0" />
			<meta name="KSOProductBuildVer" content="2058-11.2.0.10017" />
			<style type="text/css">
				<!--
				@page {
					margin-left: 1.25in;
					margin-right: 1.25in;
					margin-top: 1in;
					margin-bottom: 1in
				}

				P {
					margin-bottom: 0.08in;
					direction: ltr;
					widows: 2;
					orphans: 2
				}

				P.western {
					font-family: "Calibri", serif;
					so-language: en-US
				}

				P.cjk {
					so-language: zh-CN
				}

				P.ctl {
					font-family: ;
					so-language: ar-SA
				}

				A:link {
					color: #0000ff;
					so-language: zxx
				}
				-->
			</style>
		</head>

		<body lang="es-MX" link="#0000ff" dir="LTR">
			<p lang="en-US" class="western" align="JUSTIFY" style="text-align: center;">
				<img src="https://app.income-outcome.com/IOlogo_linear21.png" name="graphics1" align="CENTER" hspace="12"
					width="305" height="77" border="0" /><br />
			</p>
			<p lang="en-US" class="western" style="margin-bottom: 0in">
				<font face="Arial, serif">
					<font size="3">Hi ''' + jsonRow['FirstName'] +' '+ jsonRow['LastName'] + '''</font>
				</font>
			</p>
			<p lang="en-US" class="western" style="margin-bottom: 0in">
				<font face="Arial, serif">
					<font size="3"><span STYLE="font-weight: normal">We have received a request to reset your password, please
						</span></font>
				</font>
				<font face="Arial, serif">
					<font size="3">use the following temporary password to access the system.</font>
				</font>
			</p>
			<p lang="en-US" class="western" style="margin-bottom: 0in">
				<a name="_heading=h.gjdgxs"></a>
				<font face="Arial, serif">
					<font size="3"><b>'''+newPassword+'''</b></font>
				</font>
			</p>
			<p lang="en-US" class="western" align="JUSTIFY" style="margin-bottom: 0in">
				<font face="Arial, serif">
					<font size="3">You will be prompted to create a new password.
					</font>
				</font>
			</p>
			<p lang="en-US" class="western" align="JUSTIFY" style="margin-bottom: 0in">
				<font face="Arial, serif">
					<font size="3">If you have any problems please contact </font>
				</font><a href="http://mailto@petra@income-outcome.com">
					<font color="#1155cc">
						<font face="Arial, serif">
							<font size="3"><u>Petra Andrews</u></font>
						</font>
					</font>
				</a>
				<font face="Arial, serif">
					<font size="3">.</font>
				</font>
			</p>
			<p lang="en-US" class="western" align="JUSTIFY" style="margin-bottom: 0in">
				<font face="Arial, serif">
					<font size="3"><span STYLE="font-weight: normal">If you have</span></font>
				</font>
				<font face="Arial, serif">
					<font size="3"> not requested</font>
				</font>
				<font face="Arial, serif">
					<font size="3"><span STYLE="font-weight: normal">
							this password reset, please ignore this email.</span></font>
				</font>
			</p>
			<p lang="en-US" class="western" align="JUSTIFY" style="margin-bottom: 0in">
				<font face="Arial, serif">
					<font size="3"><b>Have a great day!</b></font>
				</font>
			</p>
			<p lang="en-US" class="western" align="JUSTIFY" style="margin-bottom: 0in">
				<font face="Arial, serif">
					<font size="3"><span STYLE="font-weight: normal"> </span></font>
				</font>
			</p>    
		</body>

		</html>
		'''
		# Enviar Correo

		# lmcs_4@hotmail.com
		print("sending email:",strBodyUpdatePassword)
		print("sent to: ", email)
		blnMtrReportSent = fnSendEmailPassword('Password reset request', strBodyUpdatePassword, email)

		md5 = hashlib.md5()
		aux = bytes(newPassword, encoding='utf-8')
		md5.update(aux)
		pswEncriptada =  md5.hexdigest()
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (email, pswEncriptada,1,jsonRow['UserID'])
		cursor.callproc("sp_changePasswordByEmail",params)
		MysqlCnx.commit()
		if(blnMtrReportSent):
			return {'intResponse': 200, 'strAnswer': 'Contraseña generada y enviada correctamente'}
		else:
			return {'intResponse': 202, 'strAnswer': 'Hubo un error al enviar el correo porfavor revisa tus datos'}
	except Exception as exception:
		print('Error', exception)
		return ResponseMessages.err500


def changeEmailSendPassword(email,userId, firstName, lastName):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (email, userId, 1)
		cursor.callproc("sp_getUserByEmail",params)
		MysqlCnx.commit()
		jsonRow = cursor.fetchone()
		if jsonRow == None:
			return ({'intResponse': '203', 'strAnswer': 'Email not found'})
		newPassword = ''
		for i in range(4):
			n = random.randint(0,9)
			newPassword += str(n)
		strBodyUpdatePassword = '''
		<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
		<html>

		<head>
			<meta http-equiv="CONTENT-TYPE" content="text/html; charset=utf-8" />
			<title></title>
			<meta name="GENERATOR" content="LibreOffice 4.1.6.2 (Linux)" />
			<meta name="AUTHOR" content="Salvador" />
			<meta name="CREATED" content="20210305;172800000000000" />
			<meta name="CHANGED" content="0;0" />
			<meta name="KSOProductBuildVer" content="2058-11.2.0.10017" />
			<style type="text/css">
				<!--
				@page {
					margin-left: 1.25in;
					margin-right: 1.25in;
					margin-top: 1in;
					margin-bottom: 1in
				}

				P {
					margin-bottom: 0.08in;
					direction: ltr;
					widows: 2;
					orphans: 2
				}

				P.western {
					font-family: "Calibri", serif;
					so-language: en-US
				}

				P.cjk {
					so-language: zh-CN
				}

				P.ctl {
					font-family: ;
					so-language: ar-SA
				}

				A:link {
					color: #0000ff;
					so-language: zxx
				}
				-->
			</style>
		</head>

		<body lang="es-MX" link="#0000ff" dir="LTR">
			<p lang="en-US" class="western" style="text-align: center;">
				<img src="https://app.income-outcome.com/IOlogo_linear21.png" name="image1.png" align="CENTER" hspace="12"
					width="305" height="77" border="0" /><br />
			</p>
			<p lang="en-US" class="western" style="margin-bottom: 0in">
				<font face="Arial, serif">
					<font size="3">Hi '''+ firstName + ''' ''' + lastName + '''</font>
				</font>
			</p>
			<p lang="en-US" class="western" style="margin-bottom: 0in"><br /></p>
			<p lang="en-US" class="western" style="margin-bottom: 0in">
				<font face="Arial, serif">
					<font size="3">Welcome to the </font>
				</font>
				<font face="Arial, serif">
					<font size="3"><i>Online</i></font>
				</font>
				<font face="Arial, serif">
					<font size="3">
						Income/Outcome Business Simulation. To start using the platform,
						please click on this link:
					</font>
				</font><a href="https://app.income-outcome.com/login">
					<font color="#1155cc">
						<font face="Arial, serif">
							<font size="3"><u>https://app.income-outcome.com</u></font>
						</font>
					</font>
				</a>
				<font face="Arial, serif">
					<font size="3">. Use this email (i.e. where you received this message) and the
						following password:</font>
				</font>
			</p>
			<p lang="en-US" class="western" style="margin-bottom: 0in">
				<font face="Arial, serif">
					<font size="3"><b>'''+newPassword+'''</b></font>
				</font>
			</p>
			<p lang="en-US" class="western" align="JUSTIFY" style="margin-bottom: 0in">
				<font face="Arial, serif">
					<font size="3">You will be prompted to create a new password.
					</font>
				</font>
			</p>
			<p lang="en-US" class="western" align="JUSTIFY" style="margin-bottom: 0in">
				<font face="Arial, serif">
					<font size="3">If you have any problems please contact </font>
				</font><a href="http://mailto@petra@income-outcome.com">
					<font color="#1155cc">
						<font face="Arial, serif">
							<font size="3"><u>Petra Andrews</u></font>
						</font>
					</font>
				</a>
				<font face="Arial, serif">
					<font size="3">.</font>
				</font>
			</p>
			<p lang="en-US" class="western" align="JUSTIFY" style="margin-bottom: 0in">
				<font face="Arial, serif">
					<font size="3"><b>Have a great day!</b></font>
				</font>
			</p>
			<p lang="en-US" class="western" align="JUSTIFY" style="margin-bottom: 0in">
				<font face="Arial, serif">
					<font size="3"><b>Geoff, Nikolai, Ana &amp; Petra</b></font>
				</font>
			</p>
			<p lang="en-US" class="western" align="JUSTIFY" style="margin-bottom: 0in">
				<img src="https://app.income-outcome.com/IOlogo_linear21.png" name="image2.png" align="LEFT" hspace="12"
					width="608" height="1" border="0" /><br />
			</p>
			
		</body>

		</html>'''
		# Enviar Correo

		# lmcs_4@hotmail.com
		blnMtrReportSent = fnSendEmailPassword('Your Password', strBodyUpdatePassword, email)

		md5 = hashlib.md5()
		aux = bytes(newPassword, encoding='utf-8')
		md5.update(aux)
		pswEncriptada =  md5.hexdigest()
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (email, pswEncriptada,1)
		cursor.callproc("sp_changePasswordByEmail",params)
		MysqlCnx.commit()
		if(blnMtrReportSent):
			return {'intResponse': 200, 'strAnswer': 'Contraseña generada y enviada correctamente'}
		else:
			return {'intResponse': 202, 'strAnswer': 'Hubo un error al enviar el correo porfavor revisa tus datos'}
	except Exception as exception:
		print('Error', exception)
		return ResponseMessages.err500



###############################################################################
######                                                                   ######
#####                                                                     #####
##                                EMAIL SERVER                               ##
#####                                                                     #####
######                                                                   ######
###############################################################################
class ServerMailPassword(object):
	def __init__(self, strEmail, strPassword, strServer, intPort):
		self.strEmail = strEmail
		self.strPassword = strPassword
		self.strServer = strServer
		self.intPort = intPort
		objSession = smtplib.SMTP(self.strServer, self.intPort)
		objSession.ehlo()
		objSession.starttls()
		objSession.ehlo
		objSession.login(globalInfo.strSmtpEmail, self.strPassword)
		self.objSession = objSession

	def fnSendMessage(self, strSubject, strBody, strToSend):
		msg = MIMEMultipart('alternative')
		msg['Subject'] = strSubject
		msg['From'] = globalInfo.strSmtpEmail
		msg['To'] = strToSend

		HTML_Contents = MIMEText(strBody, 'html')

		
		msg.attach(HTML_Contents)
		self.objSession.sendmail(msg['From'], msg['To'], msg.as_string())

# CODIFICAR ACENTOS - FUNCTIONS
def fnGetHTML(strText):
    objDic = {
        u"á": u"&aacute;", u"é": u"&eacute;", u"í": u"&iacute;", u"ó": u"&oacute;", u"ú": u"&uacute;",
        u"Á": u"&Aacute;", u"É": u"&Eacute;", u"Í": u"&Iacute;", u"Ó": u"&Oacute;", u"Ú": u"&Uacute;",
        u"à": u"&agrave;", u"è": u"&egrave;", u"ì": u"&igrave;", u"ò": u"&ograve;", u"ù": u"&ugrave;",
        u"À": u"&Agrave;", u"È": u"&Egrave;", u"Ì": u"&Igrave;", u"Ò": u"&Ograve;", u"Ù": u"&Ugrave;",
        u"ñ": u"&ntilde;", u"Ñ": u"&Ntilde;", u"_": u"&#x5f;"
    }
    strToConvert = strText
    # Recorrer string para convertir caracteres
    for valueSearch, valueReplace in objDic.items():
        strToConvert = strToConvert.replace(valueSearch, valueReplace)
    return strToConvert


#### Envio de emails #### -FUNCTIONS
def fnSendEmailPassword(strSubject,strBody,strEmail):
	try:
		objServerMail = ServerMailPassword(globalInfo.strSmtpEmail,globalInfo.strSmtpPassword,globalInfo.strSmtpServer, globalInfo.intSmtpPort)
		objServerMail.fnSendMessage(strSubject,strBody,strEmail)

		return True
	except Exception as e:
		print(e)
		return False


def sendPasswordEmail(email, password, firstName, lastName):
	try:
		strBodySendPassword = '''
		<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
		<html>

		<head>
			<meta http-equiv="CONTENT-TYPE" content="text/html; charset=utf-8" />
			<title></title>
			<meta name="GENERATOR" content="LibreOffice 4.1.6.2 (Linux)" />
			<meta name="AUTHOR" content="Salvador" />
			<meta name="CREATED" content="20210305;172800000000000" />
			<meta name="CHANGED" content="0;0" />
			<meta name="KSOProductBuildVer" content="2058-11.2.0.10017" />
			<style type="text/css">
				<!--
				@page {
					margin-left: 1.25in;
					margin-right: 1.25in;
					margin-top: 1in;
					margin-bottom: 1in
				}

				P {
					margin-bottom: 0.08in;
					direction: ltr;
					widows: 2;
					orphans: 2
				}

				P.western {
					font-family: "Calibri", serif;
					so-language: en-US
				}

				P.cjk {
					so-language: zh-CN
				}

				P.ctl {
					font-family: ;
					so-language: ar-SA
				}

				A:link {
					color: #0000ff;
					so-language: zxx
				}
				-->
			</style>
		</head>

		<body lang="es-MX" link="#0000ff" dir="LTR">
			<p lang="en-US" class="western" style="text-align: center;">
				<img src="https://app.income-outcome.com/IOlogo_linear21.png" name="image1.png" align="CENTER" hspace="12"
					width="305" height="77" border="0" /><br />
			</p>
			<p lang="en-US" class="western" style="margin-bottom: 0in">
				<font face="Arial, serif">
					<font size="3">Hi '''+ firstName + ''' ''' + lastName + '''</font>
				</font>
			</p>
			<p lang="en-US" class="western" style="margin-bottom: 0in"><br /></p>
			<p lang="en-US" class="western" style="margin-bottom: 0in">
				<font face="Arial, serif">
					<font size="3">Welcome to the </font>
				</font>
				<font face="Arial, serif">
					<font size="3"><i>Online</i></font>
				</font>
				<font face="Arial, serif">
					<font size="3">
						Income/Outcome Business Simulation. To start using the platform,
						please click on this link:
					</font>
				</font><a href="https://app.income-outcome.com/login">
					<font color="#1155cc">
						<font face="Arial, serif">
							<font size="3"><u>https://app.income-outcome.com</u></font>
						</font>
					</font>
				</a>
				<font face="Arial, serif">
					<font size="3">. Use this email (i.e. where you received this message) and the
						following password:</font>
				</font>
			</p>
			<p lang="en-US" class="western" style="margin-bottom: 0in">
				<font face="Arial, serif">
					<font size="3"><b>'''+password+'''</b></font>
				</font>
			</p>
			<p lang="en-US" class="western" align="JUSTIFY" style="margin-bottom: 0in">
				<font face="Arial, serif">
					<font size="3">You will be prompted to create a new password.
					</font>
				</font>
			</p>
			<p lang="en-US" class="western" align="JUSTIFY" style="margin-bottom: 0in">
				<font face="Arial, serif">
					<font size="3">If you have any problems please contact </font>
				</font><a href="http://mailto@petra@income-outcome.com">
					<font color="#1155cc">
						<font face="Arial, serif">
							<font size="3"><u>Petra Andrews</u></font>
						</font>
					</font>
				</a>
				<font face="Arial, serif">
					<font size="3">.</font>
				</font>
			</p>
			<p lang="en-US" class="western" align="JUSTIFY" style="margin-bottom: 0in">
				<font face="Arial, serif">
					<font size="3"><b>Have a great day!</b></font>
				</font>
			</p>
			<p lang="en-US" class="western" align="JUSTIFY" style="margin-bottom: 0in">
				<font face="Arial, serif">
					<font size="3"><b>Geoff, Nikolai, Ana &amp; Petra</b></font>
				</font>
			</p>
			<p lang="en-US" class="western" align="JUSTIFY" style="margin-bottom: 0in">
				<img src="https://app.income-outcome.com/IOlogo_linear21.png" name="image2.png" align="LEFT" hspace="12"
					width="608" height="1" border="0" /><br />
			</p>
			
		</body>

		</html>'''
		blnMtrReportSent = fnSendEmailPassword('Your Password', strBodySendPassword, email)

		
		if(blnMtrReportSent):
			return {'intResponse': 200, 'strAnswer': 'Contraseña generada y enviada correctamente'}
		else:
			return {'intResponse': 202, 'strAnswer': 'Hubo un error al enviar el correo porfavor revisa tus datos'}
	except Exception as exception:
		print('Error', exception)
		return ResponseMessages.err500


'''****************************************************************************
   * Author: AJLL
   * Date: 03/03/2021
   * Summary: <Crear usuario>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''

def fnCreateUser(strFirstName, strLastName, strEmail, intProfile, distributorID, clientID, isFacilitator,country, city, notes, languages, phone, alternatePhone):
	#conexion a la bd y creacion del usuario
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	#TeamId por ahora lo puse en 1
	password = ''
	for i in range(4):
		n = random.randint(0,9)
		password += str(n)
	#print(password)
	md5 = hashlib.md5()
	aux = bytes(password, encoding='utf-8')
	md5.update(aux)
	pswEncriptada =  md5.hexdigest()

	params = (1, strFirstName, strLastName, strEmail, intProfile, pswEncriptada, distributorID, clientID, isFacilitator, country, city, notes, languages, phone, None, alternatePhone)
	cursor.callproc("sp_createuser",params)
	jsonRow = cursor.fetchone()
	if(jsonRow != None):
		if(jsonRow['intResponse'] == 203):
			return ({'intResponse': 203, 'strAnswer': 'User already exists!'})
	MysqlCnx.commit()
	sendPasswordEmail(strEmail,password, strFirstName, strLastName)
	return ResponseMessages.sus200

'''****************************************************************************
   * Author: AJLL
   * Date: 03/03/2021
   * Summary: <Regresar un usuario por su id>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''

def fnGetUserById(strId):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (strId)
		#print("idclient::",strId)
		cursor.callproc("sp_getuserbyID",[params])
		MysqlCnx.commit()
		jsnRow = cursor.fetchone()
		if jsnRow == None:
			return {'intResponse': 404, 'strAnswer': 'User not found'}
		#print("objResult::",jsnRow)
		return {'intResponse': 200, 'data':jsnRow}
	except Exception as exception:
		print('fnGetUserByIDFunctions: ', exception)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}


'''****************************************************************************
   * Author: LJGF
   * Date: 06/05/2021
   * Summary: <Regresar un usuario por su id y idDistributor>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''

def fnGetUserInfo(strIdUser):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (strIdUser)
		cursor.callproc("sp_getuserbyInfo",[params])
		MysqlCnx.commit()
		jsnRow = cursor.fetchone()
		if jsnRow == None:
			return {'intResponse': 404, 'strAnswer': 'User not found'}
		#print("objResult::",jsnRow)
		return {'data':jsnRow}
	except Exception as exception:
		print('fnGetUserInfo: ', exception)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}

'''****************************************************************************
   * Author: AJLL
   * Date: 03/03/2021
   * Summary: <Eliminar a un usuario mediante su id>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnDeleteUserById(userID):
	#print("Entra funcion")
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	params = (userID)
	cursor.callproc("sp_getCountTeamFacilitatorByFacilitID",[params])
	jsonResponse = cursor.fetchall()
	if jsonResponse != None:
		for team in jsonResponse:
			if team['Facilitators'] <= 1:
				print("BORRAAAANDO TEAM POR QUE ES EL ULTIMO FACILITADOR")
				params = (team['TeamId'])
				cursor.callproc("sp_deleteTeamByID",[params])
	params = (userID)
	cursor.callproc("sp_deleteuserbyID",[params])
	MysqlCnx.commit()
	return ResponseMessages.sus200

'''****************************************************************************
   * Author: AJLL
   * Date: 03/03/2021
   * Summary: <Actualizar la informacion de un usuario>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnUpdateUser(intUserID, strFirstName, strLastName, strEmail,  intProfile, intDistributorID, intClientID, isFacilitator, country, city, notes, languages, phone, isChangeEmail, alternatePhone):
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	#TeamId por ahora lo puse en 1
	
	params = (intUserID, strFirstName, strLastName, strEmail,  intProfile, intDistributorID, intClientID, isFacilitator, country, city, notes, languages, phone, alternatePhone)
	cursor.callproc("sp_updateuser",params)
	jsonResponse = cursor.fetchone()
	#print(jsonResponse)
	MysqlCnx.commit()
	if(jsonResponse != None):
		return ({'intResponse': 203, 'strAnswer': 'User already exists!'})
	else: 
		#print(strEmail)
		if(isChangeEmail):
			resp = changeEmailSendPassword(strEmail,intUserID,strFirstName,strLastName)
			#print(resp)
			if resp['intResponse']!=200:
				return resp
	return ResponseMessages.sus200


'''****************************************************************************
   * Author: AJLL
   * Date: 11/03/2021
   * Summary: <Cambiar la contrasena si es el primer login>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''

def fnFirstLoginChangePassword(userID, email, newPassword):
		md5 = hashlib.md5()
		aux = bytes(newPassword, encoding='utf-8')
		md5.update(aux)
		pswEncriptada =  md5.hexdigest()
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (email, pswEncriptada, 0, userID)
		cursor.callproc("sp_changePasswordByEmail",params)
		MysqlCnx.commit()
		params = (userID)
		cursor.callproc("sp_setLastLogin",[params])
		MysqlCnx.commit()

		return ResponseMessages.sus200

'''****************************************************************************
   * Author: AJLL
   * Date: 11/03/2021
   * Summary: <Bloquear usuarios por el id>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''

def fnBlockUserById(strId, status, intOrg):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (strId, status)
		if(intOrg == 1):
			cursor.callproc("sp_setStatusActive",params)
		else: 
			cursor.callproc("sp_setStatusActiveClientContacts",params)
		MysqlCnx.commit()
		return ResponseMessages.sus200
	except Exception as exception:
		print('fnBlockUserById: ', exception)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}

'''****************************************************************************
   * Author: DCM
   * Date: 14/04/2021
   * Summary: <Bloquear distributors por el id>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''

def fnBlockDistributorById(strId, status):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (strId, status)
		cursor.callproc("sp_setStatusActiveDistributor",params)
		MysqlCnx.commit()
		return ResponseMessages.sus200
	except Exception as exception:
		print('fnBlockDistributorById: ', exception)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}

'''****************************************************************************
   * Author: AJLL
   * Date: 03/03/2021
   * Summary: <Regresar los workshop asociados al facilitador>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnGetWorkshopAssociatedByID(strId):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (strId)
		cursor.callproc("sp_getAssociatedWorkshopIDbyUserID",[params])
		MysqlCnx.commit()
		jsonRows = cursor.fetchall()
		return ({'intResponse': '200', 'data': jsonRows})
	except Exception as exception:
		print('fnGetWorkshopAssociatedByID: ', exception)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}

'''****************************************************************************
   * Author: DCM
   * Date: 03/26/2021
   * Summary: <Regresar los facilitadores de Andromeda>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fngetFacilitators(strIdDistributor):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (strIdDistributor)
		cursor.callproc("sp_getFacilitatorsByIdDistributor",[params])
		MysqlCnx.commit()
		jsonRows = cursor.fetchall()
		return ({'intResponse': '200', 'data': jsonRows})
	except Exception as exception:
		print('fngetFacilitators: ', exception)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}

'''****************************************************************************
   * Author: AJLL
   * Date: 03/26/2021
   * Summary: <Regresar todos los facilitadores>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fngetAllFacilitators():
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		cursor.callproc("sp_getAllFacilitators")
		MysqlCnx.commit()
		jsonRows = cursor.fetchall()
		return ({'intResponse': '200', 'data': jsonRows})
	except Exception as exception:
		print('fngetAllFacilitators: ', exception)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}

'''****************************************************************************
   * Author: AJLL
   * Date: 03/03/2021
   * Summary: <Dar de alta un distribuidor y sus contactos>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnCreateDistributorAndContacts(companyName, arrayOfContacts, isResponseErrorEmailAlreadyRegister):
	i = 0
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (companyName)
		if isResponseErrorEmailAlreadyRegister:
			cursor.callproc("sp_getDistributorIDbyName",[params])
			jsonResponseDistributorID = cursor.fetchone()
			if(jsonResponseDistributorID != None):
				idOfDistributor = jsonResponseDistributorID['DistributorID']
		else:
			cursor.callproc("sp_createDistributorAndReturnID",[params])
			MysqlCnx.commit()
			jsonRow = cursor.fetchone()
			#print(jsonRow)
			if jsonRow['intResponse'] == 203:
				return ({'intResponse': 203, 'strAnswer': 'Distriutor already exists!','remainingEmails': arrayOfContacts })
			idOfDistributor = jsonRow['DistributorID']
			#print("le generamos copia de language Base English")
			params = (idOfDistributor,1)
			cursor.callproc("sp_copyLanguage",params)
			MysqlCnx.commit()
			jsnRows = cursor.fetchall()
			params = (jsnRows[0]['LanguageId'], 1)
			cursor.callproc("sp_setAllLabels",params)
			MysqlCnx.commit()
	
		#print(arrayOfContacts)
		#print(idOfDistributor)
		for contact in arrayOfContacts:
			print(contact)
			isFacilitator = 0
			if contact['IsFacilitator']:
				isFacilitator = 1
			jsonResponse = fnCreateUser(contact['FirstName'],contact['LastName'], contact['Email'],6,idOfDistributor, None, isFacilitator, contact['Country'], contact['City'], contact['Notes'], contact['Languages'],contact['Phone'], contact['AlternatePhone'] )
			print("JSON DENTRO DE FOR",jsonResponse)
			if(jsonResponse != None):
				if(jsonResponse['intResponse'] == 203):
					remainingEmails = arrayOfContacts[i:]
					return(
						{'intResponse': 203, 
						'strAnswer': 'User already exists!', 
						'emailInvalid': arrayOfContacts[i]['Email'], 
						'remainingEmails': remainingEmails
						})
			i+=1
		return ResponseMessages.sus200
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
   * Author: AJLL
   * Date: 03/03/2021
   * Summary: <Obtener todos los distribuidores y el contador de todos sus contactos>
   * Edited: BPR
   * 
   * Summary change: <Obtencion del Last login mas reciente entre sus usuarios >
   *
   ****************************************************************************'''
def fnGetAllDistributors():
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		cursor.callproc("sp_getallDistributors")
		jsonRows = cursor.fetchall()
		#print(jsonRows)
		for distributor in jsonRows:
			jsonResponse = fnGetLastLoginFromDistributorUser(distributor['DistributorID'])
			if(jsonResponse['intResponse'] == 200):
				distributor['LastLogin'] = jsonResponse['LastLogin']
			else:
				distributor['LastLogin'] = None
		return {'intResponse': 200, 'strAnwser': 'Success', 'distributors': jsonRows}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})
	
'''****************************************************************************
   * Author: BPR
   * Date: 03/03/2021
   * Summary: <Obtener el ingreso mas reciente entre todos sus usuarios>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnGetLastLoginFromDistributorUser(DistributorID):
	try:
		print("DistributorID",DistributorID)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (DistributorID)
		cursor.callproc("sp_getLastLoginDistributorUser", [params])
		jsonRows = cursor.fetchall()
		print("LASTLOGIN",jsonRows)
		return {'intResponse': 200, 'LastLogin': jsonRows[0]['LastLogin']}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
   * Author: AJLL
   * Date: 03/03/2021
   * Summary: <Obtener todos contactos asociados a un distribuidor>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnGetContactsByDistributorID(strID):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (strID)
		cursor.callproc("sp_getallUsersByDistributorID", [params])
		jsonRows = cursor.fetchall()
		#print(jsonRows)
		return {'intResponse': 200, 'strAnwser': 'Success', 'contacts': jsonRows}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})


'''****************************************************************************
   * Author: DCM
   * Date: 08/04/2021
   * Summary: <Obtener todos workshops asociados a un distribuidor>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnGetAllWorkshopsbyUserID(strID):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (strID)
		cursor.callproc("sp_getAllWorkshopsofContact", [params])
		jsonRows = cursor.fetchall()
		print("Teams",jsonRows)
		for workShop in jsonRows:
			jsonResponse = fnGetTeamsByWorkShopId(workShop['WorkshopId'])
			if(jsonResponse['intResponse'] == 200):
				workShop['Teams'] = jsonResponse['Teams']
			else:
				workShop['Teams'] = 0
			jsonResponse = fnfacilitatorsgetData(workShop['WorkshopId'])
			if(jsonResponse['intResponse'] == 200):
				workShop['Facilitators'] = jsonResponse['data']
			else:
				workShop['Facilitators'] = []
		return {'intResponse': 200, 'strAnwser': 'Success', 'workshops': jsonRows}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
   * Author: BPR
   * Date: 14/04/2021
   * Summary: <Obtener Nombres de Teams del WorkShop>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnGetTeamsByWorkShopId(workShopId):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (workShopId)
		cursor.callproc("sp_getTeamByWorkShopId", [params])
		jsonRows = cursor.fetchall()
		#print("Teams2",jsonRows)
		return {'intResponse': 200, 'Teams': jsonRows[0]['totalTeams']}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
   * Author: DCM
   * Date: 06/04/2021
   * Summary: <Obtener todos contactos de todos los distribuidores>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnGetContactsofAllDistributors():
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		cursor.callproc("sp_getallUsersofAllDistributors")
		jsonRows = cursor.fetchall()
		#print(jsonRows)
		return {'intResponse': 200, 'strAnwser': 'Success', 'contacts': jsonRows}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})


def fnGetOnlyContactsByDistributorID(strID):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (strID)
		cursor.callproc("sp_getOnlyallContactsByDistributorID", [params])
		jsonRows = cursor.fetchall()
		#print(jsonRows)
		return {'intResponse': 200, 'strAnwser': 'Success', 'contacts': jsonRows}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})
'''****************************************************************************
   * Author: AJLL
   * Date: 03/03/2021
   * Summary: <Eliminar a un distribuidor y toda su informacion mediante su id>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnDeleteDistributorByID(distributorID):
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	params = (distributorID)
	cursor.callproc("sp_deleteDistributorByID",[params])
	MysqlCnx.commit()
	return ResponseMessages.sus200

def 	fnGetDistributorByID(distributorID, dateUTC):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (distributorID, dateUTC)
		cursor.callproc("sp_getAllFuturesWorkhopsByDistributorID",params)
		jsonRows = cursor.fetchall()
		return {'intResponse': 200, 'strAnwser': 'Success', 'Workshops': jsonRows}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
   * Author: AJLL
   * Date: 03/03/2021
   * Summary: <Actualizar la informacion de un usuario>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnUpdateDistributor(distributorID, companyName, arrayOfContacts, arrayOfNewContacts):
	i = 0
	try:
		#print("HOLAAAAAAAAAAAAAA:")
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		#------
		params = (distributorID, companyName)
		cursor.callproc("sp_updateNameDistributor",params)
		MysqlCnx.commit()
		jsonRow = cursor.fetchone()
		#print(jsonRow)
		#print("HOLAAAAAAAAAAAAAA")
		if jsonRow['intResponse'] == 203:
			return ({'intResponse': 203, 'strAnswer': 'Distriutor already exists!','remainingEmails': arrayOfContacts + arrayOfNewContacts })
		#------
		for contact in arrayOfContacts:
			#print(contact)
			isFacilitator = 0
			if contact['IsFacilitator']:
				isFacilitator = 1
			isChange = False
			if('isChangeEmail' in contact):
				#print("CAMBIO DE EMAIL? ",contact['isChangeEmail'])
				if(contact['isChangeEmail']):
					isChange = True
			jsonResponse = fnUpdateUser(contact['UserID'],contact['FirstName'],contact['LastName'], contact['Email'],6, contact['DistributorID'], None, isFacilitator, contact['Country'], contact['City'], contact['Notes'], contact['Languages'],contact['Phone'], isChange, contact['AlternatePhone'] )
			#print("JSON DENTRO DE FOR",jsonResponse)
			if(jsonResponse['intResponse'] == 203):
				remainingEmails = arrayOfContacts[i:]
				remainingEmails = remainingEmails + arrayOfNewContacts
				return(
					{'intResponse': 203, 
					'strAnswer': 'User already exists!', 
					'emailInvalid': arrayOfContacts[i]['Email'], 
					'remainingEmails': remainingEmails
					})
			else: 
				if(isChange):
					resp = changeEmailSendPassword(contact['Email'],contact['UserID'],contact['FirstName'],contact['LastName'])
					#print(resp)
					if resp['intResponse']!=200:
						return resp
			i+=1
		i=0
		for contact in arrayOfNewContacts:
			#print(contact)
			isFacilitator = 0
			if contact['IsFacilitator']:
				isFacilitator = 1
			jsonResponse = fnCreateUser(contact['FirstName'],contact['LastName'], contact['Email'],6,distributorID, None, isFacilitator, contact['Country'], contact['City'], contact['Notes'], contact['Languages'],contact['Phone'],contact['AlternatePhone'])
			#print("JSON DENTRO DE FOR New CONTACTS",jsonResponse)
			if(jsonResponse != None):
				if(jsonResponse['intResponse'] == 203):
					remainingEmails = arrayOfNewContacts[i:]
					return(
						{'intResponse': 203, 
						'strAnswer': 'User already exists!', 
						'emailInvalid': arrayOfNewContacts[i]['Email'], 
						'remainingEmails': remainingEmails
						})
			i+=1
		return ResponseMessages.sus200
	except Exception as exception:
		#print("fnupdatDistributoraaaaa", exception)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
   * Author: AJLL
   * Date: 03/03/2021
   * Summary: <Dar de alta un distribuidor y sus contactos>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnCreateTeamMembersByArray(workshopID, nameTeam, avatarTeam, arrayOfTeamMembers, isResponseErrorEmailAlreadyRegister, teamId):
	i = 0
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (nameTeam)
		if isResponseErrorEmailAlreadyRegister:
			idOfTeam = teamId
		else:
			#print("EEEEEEEEELSE", workshopID, nameTeam, avatarTeam)
			params = (workshopID, nameTeam)
			cursor.callproc("sp_createTeamAndReturnID",params)
			MysqlCnx.commit()
			jsonRow = cursor.fetchone()
			#print(jsonRow)
			idOfTeam = jsonRow['TeamId']
		#print(idOfTeam)
		for contact in arrayOfTeamMembers:
			jsonResponse = fnCreateTeamMemeber(workshopID,idOfTeam, contact['FirstName'],contact['LastName'], contact['Email'],contact['type'],contact['JobTitle'])
			#print("JSON DENTRO DE FOR",jsonResponse)
			if(jsonResponse != None):
				if(jsonResponse['intResponse'] == 203):
					#print("error idteam:",idOfTeam)
					remainingEmails = arrayOfTeamMembers[i:]
					#print("eliminamos el team que ya fue creado pero solo si no tiene members")
					params = (idOfTeam)
					cursor.callproc("sp_deleteTeamIfIsEmpty",[params])
					MysqlCnx.commit()
					return(
						{'intResponse': 203, 
						'strAnswer': 'User already exists!', 
						'emailInvalid': arrayOfTeamMembers[i]['Email'], 
						'remainingEmails': remainingEmails,
						'teamId': idOfTeam
						})
			i+=1
		return ResponseMessages.sus200
	except Exception as exception:
		print(exception)
		return ({'intResponse': 203, 'strAnswer': 'Error Database'})

def fnCreateTeamMemeber(workshopID, teamID, strFirstName, strLastName, strEmail, intProfile,jobTitle):
	#conexion a la bd y creacion del usuario
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	params = (teamID, strFirstName, strLastName, strEmail, intProfile, None, None, None,None, None, None,None, None, jobTitle, None, None)
	cursor.callproc("sp_createuser",params)
	jsonRow = cursor.fetchone()
	print("Usuario cradooooooo", jsonRow)
	if(jsonRow['intResponse'] == 203):
		return ({'intResponse': 203, 'strAnswer': 'User already exists!'})
	else:
		params = (jsonRow['UserID'], workshopID, teamID)
		cursor.callproc("sp_setRelacionWorkshopTeamIdUserId",params)
			
	MysqlCnx.commit()
	#falta crear el email que le llegara al team memeber      !!!!!!!!!!!!!!!!!!!!!!!
	#sendTeamMemberEmail(strEmail, strFirstName, strLastName)
	return ResponseMessages.sus200

def fnCreateTeamMemeberDemoMode(workshopID, teamID, strFirstName, strLastName, strEmail, intProfile,jobTitle):
	#conexion a la bd y creacion del usuario
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	params = (teamID, strFirstName, strLastName, strEmail, intProfile, None, None, None,None, None, None,None, None, jobTitle, None, None)
	cursor.callproc("sp_createuser",params)
	jsonRow = cursor.fetchone()
	fnSetMemberRolByID(teamID, jsonRow['UserID'], jobTitle)
	if(jsonRow['intResponse'] == 203):
		return ({'intResponse': 203, 'strAnswer': 'User already exists!'})
	else:
		params = (jsonRow['UserID'], workshopID, teamID)
		cursor.callproc("sp_setRelacionWorkshopTeamIdUserId",params)
			
	MysqlCnx.commit()
	#falta crear el email que le llegara al team memeber      !!!!!!!!!!!!!!!!!!!!!!!
	#sendTeamMemberEmail(strEmail, strFirstName, strLastName)
	return ResponseMessages.sus200


def fnGetAllObserversByWorkshopID(workshopID):
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	params = (workshopID)
	cursor.callproc("sp_getAllObserversByWorkshopID",[params])
	jsonResponse = cursor.fetchall()
	return ({'intResponse': 200, 'strAnswer': 'Success', 'observers': jsonResponse})
	
'''****************************************************************************
   * Author: BPR
   * Date: 04/21/2021
   * Summary: <Obtener todos los contactos de un workshop>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnGetAllContactsByWorkshopID(workshopID):
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	params = (workshopID)
	cursor.callproc("sp_getAllContactsByWorkshopID",[params])
	jsonResponse = cursor.fetchall()
	return ({'intResponse': 200, 'strAnswer': 'Success', 'contacts': jsonResponse})

'''****************************************************************************
   * Author: AJLL
   * Date: 03/03/2021
   * Summary: <Dar de alta un distribuidor y sus contactos>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnCreateObservers(workshopID, arrayOfContacts, isResponseErrorEmailAlreadyRegister, teamId):
	i = 0
	try:
		nameTeam = "TeamObserver"
		jsonResponse = fnCreateTeamMembersByArray(workshopID, nameTeam,'',arrayOfContacts, isResponseErrorEmailAlreadyRegister, teamId)
		#print(arrayOfContacts)
		#print(idOfDistributor)
		# for contact in arrayOfContacts:
		# 	print(contact)
		# 	jsonResponse = fnCreateUser(contact['FirstName'],contact['LastName'], contact['Email'],contact['type'],None, None )
		# 	print("JSON DENTRO DE FOR",jsonResponse)
		# 	if(jsonResponse != None):
		# 		if(jsonResponse['intResponse'] == 203):
		# 			remainingEmails = arrayOfContacts[i:]
		# 			return(
		# 				{'intResponse': 203, 
		# 				'strAnswer': 'User already exists!', 
		# 				'emailInvalid': arrayOfContacts[i]['Email'], 
		# 				'remainingEmails': remainingEmails
		# 				})
		# 	i+=1
		return jsonResponse
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})


def fnCreateRegistryWS(intWorkshopID, ditributor, createupdate):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		print("fncreateregistryparams:", intWorkshopID, str(ditributor))
		params = (intWorkshopID,  str(ditributor))
		if (createupdate == 0):
			cursor.callproc("sp_updateregistryWS",params)
		else:
			cursor.callproc("sp_updateregistryUpdatedWS",params)
		print("despues de sp registry")
		MysqlCnx.commit()
		
		print("despues commit regiistry")
		return ResponseMessages.sus200
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})



'''****************************************************************************
   * Author: AJLL
   * Date: 03/03/2021
   * Summary: <Actualizar la informacion de un usuario>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnUpdateObservers(workshopID, teamId, arrayOfObservers, arrayOfNewObservers):
	i = 0
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		#print("TEAM IDDDDD", teamId)
		if teamId == -1:
			return fnCreateObservers(workshopID,arrayOfObservers+arrayOfNewObservers,False,teamId)
		for contact in arrayOfObservers:
			#print(contact)
			isChange = False
			if('isChangeEmail' in contact):
				if(contact['isChangeEmail']):
					isChange = True
			jsonResponse = fnUpdateUser(contact['UserID'],contact['FirstName'],contact['LastName'], contact['Email'],contact['type'], None, None, None,None,None,None,None,None,isChange,None )
			#print("JSON DENTRO DE FOR",i,jsonResponse)
			if(jsonResponse['intResponse'] == 203):
				remainingEmails = arrayOfObservers[i:]
				remainingEmails = remainingEmails + arrayOfNewObservers
				return(
					{'intResponse': 203, 
					'strAnswer': 'User already exists!', 
					'emailInvalid': arrayOfObservers[i]['Email'], 
					'remainingEmails': remainingEmails,
					'teamId': teamId
					})
			else: 
				#print(contact['Email'])
				if(isChange):
					print(" Reenviar correo")
					# resp = changeEmailSendPassword(contact['Email'],contact['FirstName'],contact['LastName'])
					# print(resp)
					# if resp['intResponse']!=200:
					# 	return resp
			i+=1
		i=0
		for contact in arrayOfNewObservers:
			#print("Contacto a crear update observers: ",contact)
			#print("TeamID")
			jsonResponse = fnCreateTeamMemeber(workshopID,teamId, contact['FirstName'],contact['LastName'], contact['Email'],contact['type'],None)
			#print("JSON DENTRO DE FOR New CONTACTS",jsonResponse)
			if(jsonResponse != None):
				if(jsonResponse['intResponse'] == 203):
					remainingEmails = arrayOfNewObservers[i:]
					return(
						{'intResponse': 203, 
						'strAnswer': 'User already exists!', 
						'emailInvalid': arrayOfNewObservers[i]['Email'], 
						'remainingEmails': remainingEmails,
						'teamId': teamId
						})
			i+=1
		return ResponseMessages.sus200
	except Exception as exception:
		print("fnObservers", exception)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})



'''****************************************************************************
   * Author: AJLL
   * Date: 03/03/2021
   * Summary: <Eliminar a un workshop  y toda su informacion mediante su id>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnDeleteWorkshopByID(workshopID):
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	params = (workshopID)
	cursor.callproc("sp_deleteWorkshopByID",[params])
	MysqlCnx.commit()
	return ResponseMessages.sus200

'''****************************************************************************
   * Author: AJLL
   * Date: 11/03/2021
   * Summary: <Bloquear usuarios por el id>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''

def fnChangeStatusWorkshop(workshopId, status, lstDate):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		if status == 1:
			fnCreateDates(workshopId,lstDate)
		params = (workshopId, status)
		cursor.callproc("sp_setStatusActiveWorkshop",params)
		MysqlCnx.commit()
		return ResponseMessages.sus200
	except Exception as exception:
		print('fnChangeStatusWorkshop: ', exception)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}

def fnGetAllTeamMembersByWorkshopId(workshopID):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (workshopID)
		#cursor.callproc("sp_getuserbyID",[params])
		cursor.callproc("sp_getAllTeamMembersByWorkshopID",[params])
		MysqlCnx.commit()
		jsnRows = cursor.fetchall()	
		return {'intResponse': 200, 'teamMembers': jsnRows}
	except Exception as e:
		print(e)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}


def fnGetAllMessages(typeChat, workshopId, teamId):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (typeChat, workshopId, teamId)
		#cursor.callproc("sp_getuserbyID",[params])
		cursor.callproc("sp_getMesagges",params)
		MysqlCnx.commit()
		jsnRows = cursor.fetchall()	
		return {'intResponse': 200, 'messages': jsnRows}
	except Exception as e:
		print(e)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}


'''****************************************************************************
   * Author: AJLL
   * Date: 03/03/2021
   * Summary: <Actualizar la informacion de un usuario>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnUpdateTeamMembers(workshopID, teamId, arrayOfTeamMembers, arrayOfNewTeamMembers):
	i = 0
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		for contact in arrayOfTeamMembers:
			#print(contact)
			if('isChangeEmail' in contact):
				if(contact['isChangeEmail']):
					isChange = True
			jsonResponse = fnUpdateUser(contact['UserID'],contact['FirstName'],contact['LastName'], contact['Email'],3, None,  None, None,isChange )
			#print("JSON DENTRO DE FOR",i,jsonResponse)
			if(jsonResponse['intResponse'] == 203):
				remainingEmails = arrayOfTeamMembers[i:]
				remainingEmails = remainingEmails + arrayOfNewTeamMembers
				return(
					{'intResponse': 203, 
					'strAnswer': 'User already exists!', 
					'emailInvalid': arrayOfTeamMembers[i]['Email'], 
					'remainingEmails': remainingEmails,
					'teamId': teamId
					})
			else:
				#print(contact['Email'])
				if(isChange):
					# Reenviar correo
					print(" Reenviar correo")
					# resp = changeEmailSendPassword(contact['Email'],contact['FirstName'],contact['LastName'])
					# print(resp)
					# if resp['intResponse']!=200:
					# 	return resp
			i+=1
		i=0
		for contact in arrayOfNewTeamMembers:
			#print("Contacto a crear update observers: ",contact)
			#print("TeamID")
			jsonResponse = fnCreateTeamMemeber(workshopID,teamId, contact['FirstName'],contact['LastName'], contact['Email'],3,contact['JobTitle'])
			#print("JSON DENTRO DE FOR New CONTACTS",jsonResponse)
			if(jsonResponse != None):
				if(jsonResponse['intResponse'] == 203):
					remainingEmails = arrayOfNewTeamMembers[i:]
					return(
						{'intResponse': 203, 
						'strAnswer': 'User already exists!', 
						'emailInvalid': arrayOfNewTeamMembers[i]['Email'], 
						'remainingEmails': remainingEmails,
						'teamId': teamId
						})
			i+=1
		return ResponseMessages.sus200
	except Exception as exception:
		print("fnupdatDistributor", exception)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

def fnUpdateTeamMember(userId, firstName, lastName, teamId):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (userId, firstName, lastName, teamId)
		cursor.callproc("sp_updateTeamMemeberByUserId",params)
		MysqlCnx.commit()
		return({'intResponse': 200, 'strAnswer': 'update Team member succesffuly'})
	except Exception as exception:
		print("fnupdatDistributor", exception)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

def fnCreateTeamsMembersByArrayOfTeams(workshopID, arrayOfTeams, isResponseErrorEmailAlreadyRegister, teamId, cycles, BoardMode):
	i = 0
	j=0
	arrayOfTeamsAux = arrayOfTeams
	arrTeamsId = []
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		for i, team in enumerate(arrayOfTeams):
			#print("TEAM::  ",team)
			params = (team['TeamName'])
			#print("ANTES IF")
			if isResponseErrorEmailAlreadyRegister:
				idOfTeam = team['TeamId'] 
				#print("IFFF:: ", idOfTeam)
			else:
				#print("EEEEEEEEELSE", workshopID, team['TeamName'])
				params = (workshopID, team['TeamName'])
				cursor.callproc("sp_createTeamAndReturnID",params)
				MysqlCnx.commit()
				jsonRow = cursor.fetchone()
				#print(jsonRow)
				idOfTeam = jsonRow['TeamId']
				params = (getFacilitatorsUsersId(i), workshopID, idOfTeam)
				cursor.callproc("sp_setRelacionWorkshopTeamIdUserId",params)
				MysqlCnx.commit()
				arrTeamsId.append(idOfTeam)
				team['TeamId'] = idOfTeam
				arrayOfTeamsAux[j]['TeamId'] = idOfTeam
				# para crear inicializar el board
				fnInitBoard(idOfTeam)
			#print("idOfTeam, ", idOfTeam)
			for contact in team['teamMembers']:
				jsonResponse = fnCreateTeamMemeber(workshopID,idOfTeam, contact['FirstName'],contact['LastName'], contact['Email'],contact['type'],contact['JobTitle'])
				#print("JSON DENTRO DE FOR",jsonResponse)
				remainingEmails = team['teamMembers'][i:]
				if(jsonResponse != None):
					if(jsonResponse['intResponse'] == 203):
						user = arrayOfTeamsAux[j]['teamMembers'][i]['Email']
						#print("UserRepetido: ",user)
						arrayOfTeamsAux[j]['teamMembers'] = remainingEmails
						#print("eliminamos el team que ya fue creado pero solo si no tiene members")
						params = (idOfTeam)
						cursor.callproc("sp_deleteTeamIfIsEmpty",[params])
						MysqlCnx.commit()
						return(
							{'intResponse': 203, 
							'strAnswer': 'User already exists!', 
							'emailInvalid': user, 
							'remainingEmails': arrayOfTeamsAux,
							'teamId': idOfTeam
							})
				i+=1
			isResponseErrorEmailAlreadyRegister = False
			#print("Fin for de equipo")
			#print("teamMembers:: ",arrayOfTeamsAux[j]['teamMembers'])
			arrayOfTeamsAux[j]['teamMembers'] = []
			i=0
			j+=1
			#print("Fin for de equipo")
		print("CLYCLEEEES",cycles, type(cycles))
		for i in range(int(cycles)):
			jsonResponseOrders = fnCreateOrders(workshopID, arrTeamsId, (i+1), BoardMode)
			#print("jsonResponseOrders", (i+1), jsonResponseOrders)
		jsonResponseImprovements = fnCreateImprovements(workshopID, arrTeamsId)
		#print("jsonResponseImprovements", jsonResponseImprovements)
		return ResponseMessages.sus200
	except Exception as exception:
		print(exception)
		return ({'intResponse': 203, 'strAnswer': 'Error Database'})

def getFacilitatorsUsersId(index):
	# id de la tabla users para los correos de los facilitadores que podran estar en los diferentes teams
	lstFacUsersId = [
		2368,
		2369,
		2370,
		2371,
		2372,
		2373
	]
	return(lstFacUsersId[index])

def fnCreateTeamsMembersByArrayOfTeamsDemoMode(workshopID, arrayOfTeams, isResponseErrorEmailAlreadyRegister, teamId, cycles, BoardMode):
	i = 0
	j=0
	arrayOfTeamsAux = arrayOfTeams
	arrTeamsId = []
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		for i,team in enumerate(arrayOfTeams):
			#print("TEAM::  ",team)
			params = (team['TeamName'])
			#print("ANTES IF")
			if isResponseErrorEmailAlreadyRegister:
				idOfTeam = team['TeamId'] 
				#print("IFFF:: ", idOfTeam)
			else:
				#print("EEEEEEEEELSE", workshopID, team['TeamName'])
				params = (workshopID, team['TeamName'])
				cursor.callproc("sp_createTeamAndReturnID",params)
				MysqlCnx.commit()
				jsonRow = cursor.fetchone()
				#print(jsonRow)
				idOfTeam = jsonRow['TeamId']
				params = (getFacilitatorsUsersId(i), workshopID, idOfTeam)
				cursor.callproc("sp_setRelacionWorkshopTeamIdUserId",params)
				MysqlCnx.commit()
				arrTeamsId.append(idOfTeam)
				team['TeamId'] = idOfTeam
				arrayOfTeamsAux[j]['TeamId'] = idOfTeam
				# para crear inicializar el board
				fnInitBoard(idOfTeam)
				# Inicializamos el teamSetup de una vez: avatar y color
				jsonResponseTeamAvatar = fnSetTeamAvatarByID(idOfTeam, workshopID, "Team "+ str(i+1)) 
				print("jsonResponseTeamAvatar",jsonResponseTeamAvatar)
				jsonResponseTeamColor = fnSetTeamColorByID(idOfTeam, workshopID, getColor(i))
				print("jsonResponseTeamColor",jsonResponseTeamColor)
			#print("idOfTeam, ", idOfTeam)
			for contact in team['teamMembers']:
				jsonResponse = fnCreateTeamMemeberDemoMode(workshopID,idOfTeam, contact['FirstName'],contact['LastName'], contact['Email'],contact['type'],contact['JobTitle'])
				#print("JSON DENTRO DE FOR",jsonResponse)
				remainingEmails = team['teamMembers'][i:]
				if(jsonResponse != None):
					if(jsonResponse['intResponse'] == 203):
						user = arrayOfTeamsAux[j]['teamMembers'][i]['Email']
						#print("UserRepetido: ",user)
						arrayOfTeamsAux[j]['teamMembers'] = remainingEmails
						#print("eliminamos el team que ya fue creado pero solo si no tiene members")
						params = (idOfTeam)
						cursor.callproc("sp_deleteTeamIfIsEmpty",[params])
						MysqlCnx.commit()
						return(
							{'intResponse': 203, 
							'strAnswer': 'User already exists!', 
							'emailInvalid': user, 
							'remainingEmails': arrayOfTeamsAux,
							'teamId': idOfTeam
							})
				i+=1
			isResponseErrorEmailAlreadyRegister = False
			#print("Fin for de equipo")
			#print("teamMembers:: ",arrayOfTeamsAux[j]['teamMembers'])
			arrayOfTeamsAux[j]['teamMembers'] = []
			i=0
			j+=1
			#print("Fin for de equipo")
		print("CLYCLEEEES",cycles, type(cycles))
		for i in range(int(cycles)):
			jsonResponseOrders = fnCreateOrders(workshopID, arrTeamsId, (i+1), BoardMode)
			#print("jsonResponseOrders", (i+1), jsonResponseOrders)
		jsonResponseImprovements = fnCreateImprovements(workshopID, arrTeamsId)
		#print("jsonResponseImprovements", jsonResponseImprovements)
		return ResponseMessages.sus200
	except Exception as exception:
		print(exception)
		return ({'intResponse': 203, 'strAnswer': 'Error Database'})

def getColor(index):
	colors = [
		"#84eeeb",
		"#bec3ff",
		"#083584",
		"#7f2378",
		"#af753a",
		"#50b1a8"
	]
	return colors[index]

# def fnUpdateTeamsMembersByArrayOfTeams(workshopID, arrayOfTeams, isResponseErrorEmailAlreadyRegister, teamId):
# 	i = 0
# 	j=0
# 	arrayOfTeamsAux = arrayOfTeams
# 	try:
# 		MysqlCnx = getConectionMYSQL()
# 		cursor = MysqlCnx.cursor()
# 		for team in arrayOfTeams:
# 			print("TEAM::  ",team)
# 			params = (team['TeamName'])
# 			print("ANTES IF")
# 			if isResponseErrorEmailAlreadyRegister:
# 				idOfTeam = team['TeamId'] 
# 				print("IFFF:: ", idOfTeam)
# 			else:
# 				print("EEEEEEEEELSE", workshopID, team['TeamName'])
# 				params = (workshopID, team['TeamName'], 'Avatar'+team['TeamName'])
# 				cursor.callproc("sp_createTeamAndReturnID",params)
# 				MysqlCnx.commit()
# 				jsonRow = cursor.fetchone()
# 				print(jsonRow)
# 				idOfTeam = jsonRow['TeamId']
# 				team['TeamId'] = idOfTeam
# 				arrayOfTeamsAux[j]['TeamId'] = idOfTeam
# 				# para crear inicializar el board
# 				fnInitBoard(idOfTeam)
# 			print("idOfTeam, ", idOfTeam)
# 			for contact in team['teamMembers']:
# 				jsonResponse = fnCreateTeamMemeber(workshopID,idOfTeam, contact['FirstName'],contact['LastName'], contact['Email'],contact['type'],contact['JobTitle'])
# 				print("JSON DENTRO DE FOR",jsonResponse)
# 				if(jsonResponse != None):
# 					if(jsonResponse['intResponse'] == 203):
# 						user = arrayOfTeamsAux[j]['teamMembers'][i]['Email']
# 						print("UserRepetido: ",user)
# 						return(
# 							{'intResponse': 203, 
# 							'strAnswer': 'User already exists!', 
# 							'emailInvalid': user, 
# 							'remainingEmails': arrayOfTeamsAux,
# 							'teamId': idOfTeam
# 							})
# 				i+=1
# 			isResponseErrorEmailAlreadyRegister = False
# 			print("Fin for de equipo")
# 			print("teamMembers:: ",arrayOfTeamsAux[j]['teamMembers'])
# 			i=0
# 			j+=1
# 			print("Fin for de equipo")
# 		return ResponseMessages.sus200
# 	except Exception as exception:
# 		print(exception)
# 		return ({'intResponse': 203, 'strAnswer': 'Error Database'})

def fnUpdateTeamsMembersByArrayOfTeams(workshopID, arrayOfTeams, isResponseErrorEmailAlreadyRegister, teamId, cycles, BoardMode, blnUpdBoardMode):
	i = 0
	j=0
	idOfTeam = -1
	arrayOfTeamsAux = arrayOfTeams
	arrTeamsId = []
	blnCreateOrders = False
	try:
		#print("jsonResponseDelete",jsonResponseDelete)
		#print("jsonResponseDeleteImprovements",jsonResponseDeleteImprovements)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		for index, team in enumerate(arrayOfTeams):
			params = (team['TeamName'])
			if "TeamIdBD" in team and team['TeamIdBD'] != None:
				idOfTeam = team['TeamIdBD'] 
				arrTeamsId.append(idOfTeam)
				len(team['teamMembers'])
				if (len(team['teamMembers']) == 0):
					params = (team['TeamIdBD'])
					cursor.callproc("sp_deleteTeamByID",[params])
					MysqlCnx.commit()
			else:
				params = (workshopID, team['TeamName'])
				cursor.callproc("sp_createTeamAndReturnID",params)
				MysqlCnx.commit()
				jsonRow = cursor.fetchone()
				idOfTeam = jsonRow['TeamId']
				blnCreateOrders = True
				arrTeamsId.append(idOfTeam)
				team['TeamId'] = idOfTeam
				arrayOfTeamsAux[j]['TeamId'] = idOfTeam
				# para crear inicializar el board
				fnInitBoard(idOfTeam)
			params = (getFacilitatorsUsersId(index), int(workshopID), idOfTeam)
			cursor.callproc("sp_setRelacionWorkshopTeamIdUserId",params)
			MysqlCnx.commit()
			for contact in team['teamMembers']:
				jsonResponse = fnCreateTeamMemeber(workshopID,idOfTeam, contact['FirstName'],contact['LastName'], contact['Email'],contact['type'],contact['JobTitle'])
				if(jsonResponse != None):
					if(jsonResponse['intResponse'] == 203):
						user = arrayOfTeamsAux[j]['teamMembers'][i]['Email']
						params = (idOfTeam)
						cursor.callproc("sp_deleteTeamIfIsEmpty",[params])
						MysqlCnx.commit()
						return(
							{'intResponse': 203, 
							'strAnswer': 'User already exists!', 
							'emailInvalid': user, 
							'remainingEmails': arrayOfTeamsAux,
							'teamId': idOfTeam
							})
				i+=1
			isResponseErrorEmailAlreadyRegister = False
			i=0
			j+=1
			#print("Fin for de equipo")
		print("CLYCLEEEES",cycles, type(cycles))
		if(blnCreateOrders or not blnUpdBoardMode):
			jsonResponseDelete = fnDeleteOrders(workshopID)
			jsonResponseDeleteImprovements = fnDeleteImprovements(workshopID)
			for i in range(int(cycles)):
				jsonResponseOrders = fnCreateOrders(workshopID, arrTeamsId, (i+1), BoardMode)
			jsonResponseImprovements = fnCreateImprovements(workshopID, arrTeamsId)
		return ResponseMessages.sus200
	except Exception as exception:
		print(exception)
		return ({'intResponse': 203, 'strAnswer': 'Error Database'})

def fnInitBoard(teamId):
	#print("INICIALIZANDO BOAAAARD")
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	params = (teamId)
	cursor.callproc("sp_initBoard",[params])
	MysqlCnx.commit()

# Daniel develop**********************************************

def fnGetAllLanguages(idDistributor, isPrivate, ownLanguages):
	try:
		#print("entramos a getall languages")
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (idDistributor, isPrivate, ownLanguages)
		cursor.callproc("sp_getLanguages", params)
		MysqlCnx.commit()
		#print('Users getter successfully!')
		#print("cursor:",cursor)
		jsnRows = cursor.fetchall()
		#print("jsnRows:",jsnRows)
		return {"intResponse":200,"jsnAnswer":jsnRows}
	except Exception as e:
		print(e)
		return ResponseMessages.err500

def fnGetAllLabelsbyLanguage(intID):
	try:
		#print("entramos a getall labels by language ",intID)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (intID)
		cursor.callproc("sp_getLabelsScreensbyLanguage",[params])
		MysqlCnx.commit()
		jsnRows = cursor.fetchall()
		#print("jsnRows:",jsnRows)
		return {"intResponse":200,"jsnAnswer":jsnRows}
	except Exception as e:
		print(e)
		return ResponseMessages.err500



def fnGetdescbyLanguage(intLangId):
	try:
		#print("entramos a getall labels by language ",intID)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (intLangId)
		cursor.callproc("sp_getdescbyLanguageId",[params])
		MysqlCnx.commit()
		jsnRow = cursor.fetchone()
		print("jsnRow language desc:",jsnRow)
		return {"intResponse":200,"jsnAnswer":jsnRow}
	except Exception as e:
		print(e)
		return ResponseMessages.err500

def fnGetLangSaved(workshopId, userId):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (workshopId,userId)
		cursor.callproc("sp_getLanguageSelectedbyUser",params)
		MysqlCnx.commit()
		jsnRow = cursor.fetchone()
		print("jsnRow language selected:",jsnRow)
		return {"intResponse":200,"jsnAnswer":jsnRow}
	except Exception as e:
		print(e)
		return ResponseMessages.err500


def fngetscreenscomplete(idLanguage,sreenId):
	try:
		#print("fngetscreenscomplete ")
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (idLanguage,sreenId)
		cursor.callproc("sp_getstatusscreen",params)
		MysqlCnx.commit()
		jsnRows = cursor.fetchall()
		#print("jsnRows:",jsnRows)
		return {"intResponse":200,"jsnAnswer":jsnRows}
	except Exception as e:
		print(e)
		return ResponseMessages.err500

def fnsetscreenscomplete(idLanguage,sreenId,complet):
	try:
		#print("fngetscreenscomplete ")
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (idLanguage,sreenId,complet)
		cursor.callproc("sp_setstatusscreen",params)
		MysqlCnx.commit()
		#print("jsnRows:",jsnRows)
		return {"intResponse":200}
	except Exception as e:
		print(e)
		return ResponseMessages.err500


def fnupdateLabels(arrDataUpdate):
	#conexion a la bd y creacion del usuario
	#print("llega hasta functions arrDataUpdate:",arrDataUpdate)
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	for objData in arrDataUpdate:
		#print("objData", objData["Label"])
		params = (objData["LabelCode"],objData["ScreenId"],objData["LanguageId"],objData["Label"])
		cursor.callproc("sp_updListLabels",params)
		MysqlCnx.commit()
	return {"intResponse":200}

def updateLabelBase(LabelId, LabelBase, Label):
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	params = (LabelId, LabelBase, Label)
	cursor.callproc("sp_updLabelBase", params)
	MysqlCnx.commit()
	return {"intResponse":200}

def fncreateLabels(arrDataUpdate, idLanguage):
	#conexion a la bd y creacion del usuario
	#print("llega hasta functions arrDataUpdate:",arrDataUpdate)
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	for objData in arrDataUpdate:
		#print("objData", objData["Label"])
		params = (objData["LabelCode"],objData["ScreenId"],idLanguage,objData["Label"])
		cursor.callproc("sp_newListLabels",params)
		MysqlCnx.commit()
	return {"intResponse":200}

def fncreateLanguage(descLanguage, idDistributor, languageisPrivate):
	#conexion a la bd 
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	#print("descLanguage:", descLanguage)
	params = (descLanguage,idDistributor,languageisPrivate)
	cursor.callproc("sp_newLanguage",params)
	MysqlCnx.commit()
	jsnRows = cursor.fetchall()
	params = (jsnRows[0]['LanguageId'],1)
	cursor.callproc("sp_setAllLabels",params)
	MysqlCnx.commit()
	#print("idLanguage = jsnRows:",jsnRows[0]['LanguageId'])
	return {"intResponse":200,"idLanguage":jsnRows[0]['LanguageId']}

def getScreenLabelsByLanguage(languageId):
	#conexion a la bd 
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	params = (languageId)
	cursor.callproc('sp_getScreenLabelsByLanguage', [params])
	MysqlCnx.commit()
	jsnRows = cursor.fetchall()
	return {"intResponse": 200, "textLabels": jsnRows}

def getValidationLabels(workshopID):
	#conexion a la bd 
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	params = (workshopID)
	cursor.callproc('sp_getValidationLabels', [params])
	MysqlCnx.commit()
	jsnRows = cursor.fetchall()
	return {"intResponse": 200, "textLabels": jsnRows}

def fncupdNameLanguage(idLanguage, nameLanguage, isPrivate ):
	#conexion a la bd 
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	#print("descLanguage:", nameLanguage)
	#print("idLanguage:",idLanguage)
	#params = (6, 'languageDemoUpd88')
	params = ( int(idLanguage), str(nameLanguage), int(isPrivate))
	#print("params:",params)
	cursor.callproc("sp_updateNameLanguage",params)
	MysqlCnx.commit()
	return {"intResponse":200}

def fncopyLanguage(idDistributor,idLanguage):
	#conexion a la bd 
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	#print("idDistributor:", idDistributor)
	#print("idLanguage:",idLanguage)
	#params = (6, 'languageDemoUpd88')
	params = ( int(idDistributor), int(idLanguage))
	#print("params:",params)
	#print("le generamos copia del language recibido")
	cursor.callproc("sp_copyLanguage",params)
	MysqlCnx.commit()
	jsnRows = cursor.fetchall()
	params = (jsnRows[0]['LanguageId'], int(idLanguage))
	cursor.callproc("sp_setAllLabels",params)
	MysqlCnx.commit()
	return {"intResponse":200}

def fnInsUpdLanguageSelected(LanguageId, WorkshopId, UserId):
	#conexion a la bd 
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	#print("idDistributor:", idDistributor)
	#print("idLanguage:",idLanguage)
	#params = (6, 'languageDemoUpd88')
	params = ( int(LanguageId), int(WorkshopId), int(UserId))
	#print("params:",params)
	#print("le generamos copia del language recibido")
	cursor.callproc("sp_SetUpdLanguageSelectedbyUser",params)
	MysqlCnx.commit()
	return {"intResponse":200}

def fnGetAllTimeZones():
	try:
		#print("entramos a getall languages")
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		cursor.callproc("sp_getTimeZones")
		MysqlCnx.commit()
		#print("cursor:",cursor)
		jsnRows = cursor.fetchall()
		# print("jsnRows:",jsnRows)
		return {"intResponse":200,"jsnAnswer":jsnRows}
	except Exception as e:
		print(e)
		return ResponseMessages.err500

def fnLogin(strEmail, strPassword):
	md5 = hashlib.md5()
	aux = bytes(strPassword, encoding='utf-8')
	md5.update(aux)
	pswEncriptada =  md5.hexdigest()
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	print("entro fnloginnn")
	params = (strEmail, 0, 0)
	cursor.callproc("sp_getUserByEmail",params)
	MysqlCnx.commit()
	jsnRow = cursor.fetchall()
	print("jsonrowresult:",jsnRow)
	#print("jsrow user::",jsnRow)
	if(len(jsnRow) > 0):
		print("dentro if lenght:")
		print("dentro if lenght:", len(jsnRow))
		for row in jsnRow:
			print("entra for row:", row)
			if(row['Password'] == pswEncriptada):
				if row['Active'] == 1:
					paramsSend = (row['UserID'])
					cursor.callproc("sp_setLastLogin",[paramsSend])
					MysqlCnx.commit()
					if row['IsFirstLogin'] == None or row['IsFirstLogin'] == 1:
						return {'intResponse': '200', 'strAnswer': 'First Login', 'UserID':row['UserID'], 'type':row['type'],'DistributorID': row['DistributorID'], 'CompanyName': row['CompanyName'], 'IsFacilitator': row['IsFacilitator']}
					else:
						return {'intResponse': '200', 'strAnswer': 'You are logged', 'UserID':row['UserID'], 'type':row['type'],'DistributorID': row['DistributorID'], 'CompanyName': row['CompanyName'], 'IsFacilitator': row['IsFacilitator']}
				else:
					return {'intResponse':'210','strAnswer':'Your access has been removed. If you think this is an error, please contact Petra Andrews.'}
			else:
				return {'intResponse':'203','strAnswer':'Wrong Password or Email.'}
	else:
		return {'intResponse':'203','strAnswer':'Wrong Password or Email.'}

'''****************************************************************************
   * Author: DCM
   * Date: 27/03/2021
   * Summary: <Crear WorkShop>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnCreateWorkShop(intDistributorID, strName, strClient, Facilitator, Language, TimeZone, Notes,BusinessModel, BoardMode, Cycles,LanguageOrgPriv):
	try:
		#print("recibo en fn create work::",intDistributorID, strName, strClient, Facilitator, Language, TimeZone, Notes,BusinessModel,Cycles,LanguageOrgPriv)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		#now = datetime.datetime.now()
		# print("strStartDate:", strStartDate)
		#formatted_date = strStartDate.strftime('%Y-%m-%d %H:%M:%S')
		formatted_startdate = None
		formatted_startEnd = None
		# if(strStartDate != ""):
		# 	dateIni = datetime.fromisoformat(strStartDate[:-1])
		# 	formatted_startdate = dateIni.strftime('%Y-%m-%d %H:%M:%S')
		# if(strEndDate != ""):
		# 	dateFin = datetime.fromisoformat(strEndDate[:-1])
		# 	formatted_startEnd = dateFin.strftime('%Y-%m-%d %H:%M:%S')
		strLngOrgPriv = ""
		for i in LanguageOrgPriv:
			strLngOrgPriv+=str(i['LanguageId'])+","
		#print("LENGUAJES A MANDAR ORG PRIV::: "+strLngOrgPriv)
		params = (intDistributorID, strName, strClient, Facilitator, Language, 
		None, None, TimeZone, Notes, BusinessModel, BoardMode, Cycles, strLngOrgPriv)
		#print("parametros a enviar:",params)
		cursor.callproc("sp_createWorkShopAndReturnID",params)
		MysqlCnx.commit()
		jsonRow = cursor.fetchone()
		#print(jsonRow)
		idOfWorkshop = jsonRow['WorkshopId']
		#print("idOfWorkshopCreated:",idOfWorkshop)
		return {'intResponse': '200', 'idOfWorkshop': idOfWorkshop}
	except Exception as exception:
		print(exception)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})


def fnCreateDeliveryMails(WorkshopId, DeliveryDate, templetes):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		DeliveryDate = datetime.datetime.fromisoformat(DeliveryDate)
		deliveryDateWelcome = DeliveryDate - datetime.timedelta(weeks=2)
		deliveryDateReminder = DeliveryDate - datetime.timedelta(days=1)
		deliveryDateUpComing = DeliveryDate - datetime.timedelta(hours=1)
		params = (WorkshopId, str(deliveryDateWelcome), str(deliveryDateReminder), str(deliveryDateUpComing))
		#print("parametros a enviar:",params)
		cursor.callproc("sp_createDeliveryMails",params)
		MysqlCnx.commit()
		jsonRow = cursor.fetchone()

		for value in templetes:
			params = (WorkshopId, value['emailType'], value['userType'], value['body'], value['subject'])
			cursor.callproc("sp_createBodySubjectEmail",params)
			MysqlCnx.commit()


		#print(jsonRow)
		return {'intResponse': '200', 'strAnswer': "Success"}
	except Exception as exception:
		print(exception)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

def fnUpdateDateDeliveryMails(WorkshopId, DeliveryDate):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		DeliveryDate = datetime.datetime.fromisoformat(DeliveryDate)
		deliveryDateWelcome = DeliveryDate - datetime.timedelta(weeks=2)
		deliveryDateReminder = DeliveryDate - datetime.timedelta(days=1)
		deliveryDateUpComing = DeliveryDate - datetime.timedelta(hours=1)
		params = (WorkshopId, str(deliveryDateWelcome), str(deliveryDateReminder), str(deliveryDateUpComing))
		cursor.callproc("sp_updateDateDeliveryMails",params)
		MysqlCnx.commit()
		return {'intResponse': '200', 'strAnswer': "Success"}
	except Exception as exception:
		print(exception)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})


'''****************************************************************************
   * Author: DCM
   * Date: 27/03/2021
   * Summary: <Update WorkShop>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnupdateworkshop(WorkshopId,intDistributorID, strName, strClient, Facilitator, Language, TimeZone, Notes, BusinessModel, BoardMode, Cycles,LanguageOrgPriv):
	try:
		#print("recibo en fn create work::",intDistributorID, strName, strClient, Facilitator, Language, TimeZone, Notes,LanguageOrgPriv)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		#now = datetime.datetime.now()
		# print("strStartDate:", strStartDate)
		# #formatted_date = strStartDate.strftime('%Y-%m-%d %H:%M:%S')
		# formatted_startdate = None
		# formatted_startEnd = None
		# if(strStartDate != ""):
		# 	dateIni = datetime.fromisoformat(strStartDate)
		# 	formatted_startdate = dateIni.strftime('%Y-%m-%d %H:%M:%S')
		# if(strEndDate != ""):
		# 	dateFin = datetime.fromisoformat(strEndDate)
		# 	formatted_startEnd = dateFin.strftime('%Y-%m-%d %H:%M:%S')
		strLngOrgPriv = ""
		for i in LanguageOrgPriv:
			strLngOrgPriv+=str(i['LanguageId'])+","
		#print("LENGUAJES A MANDAR ORG PRIV::: "+strLngOrgPriv)
		params = (WorkshopId,intDistributorID, strName, strClient, Facilitator, Language, None, None, TimeZone, Notes, BusinessModel, BoardMode, Cycles,strLngOrgPriv)
		#print("parametros a enviar:",params)
		cursor.callproc("sp_updateWorkShop",params)
		MysqlCnx.commit()
		'''jsonRow = cursor.fetchone()
		#print(jsonRow)
		idOfWorkshop = jsonRow['WorkshopId']'''
		#print("idOfWorkshopCreated:",WorkshopId)
		return {'intResponse': '200', 'idOfWorkshop': WorkshopId}
	except Exception as exception:
		print(exception)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})


def fnInactivateWorkshopMiddleNight():
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	cursor.callproc("sp_getAllWorkshopsAndTheirEndDate")
	jsonRows = cursor.fetchall()
	now = datetime.datetime.utcnow()
	for row in jsonRows:
		dateTimeBD = row['DateEndTimeUTC']
		print("row:",row)
		print("now:",now)
		print("(dateTimeBD + datetime.timedelta(days=1):", (dateTimeBD + datetime.timedelta(days=1)))
		if now > (dateTimeBD + datetime.timedelta(days=1)):
			print("inactivando a: ",row)
			params = (row['WorkshopId'], 0)
			cursor.callproc("sp_setStatusActiveWorkshop",params)
			MysqlCnx.commit()
	return ResponseMessages.sus200

def fnSendReports(typeReport):
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	paramType = typeReport
	cursor.callproc("sp_getCreatedWorkshops", [paramType])
	jsonRowsCreated = cursor.fetchall()
	cursor.callproc("sp_getUpdatedWorkshops", [paramType])
	jsonRowsUpd = cursor.fetchall()
	paramsgetCreationdelete = (1, paramType)
	cursor.callproc("sp_getDeletedWorkshops", paramsgetCreationdelete)
	jsonRowsCreatedDelted = cursor.fetchall()
	paramsgetUpdateddelete = (2, paramType)
	cursor.callproc("sp_getDeletedWorkshops", paramsgetUpdateddelete)
	jsonRowsUpdDeleted = cursor.fetchall()
	#print("paramsgetCreationdelete:", jsonRowsCreatedDelted,"jsonRowsUpdateDelted:", jsonRowsUpdDeleted)
	#print("jsn final jsonRowsUpdDeleted:", jsonRowsUpdDeleted)
	#print("jsn final jsonRowsCreatedDelted:", jsonRowsCreatedDelted)
	#return
	#print("jsonrows lenght", len(jsonRowsUpd), len(jsonRows))
	"""htmlSendCreated = '''<style type='text/css'>
	.tftable {font-size:12px;color:#333333;width:100%;border-width: 1px;border-color: #729ea5;border-collapse: collapse;}
	.tftable th {background-color: #234b91 !important;color:white;font-size: 14;font-family:Calibri;border-width: 1px;padding: 6px;border-style: solid;border-color: white;text-align:center;height: 15px;}
	.tftable tr {background-color:#ffffff;text-align:center;}
	.tftable td {font-size:12px;border-width: 1px;padding: 5px;border-style: solid;border-color: #234b91;text-align:center;}
	.tftable tr:hover {background-color:#ced7d8;}
	.th5{width:5% !important}
	.th10{width:10% !important}
	.th13 {width:13% !important}
	.th15 {width:15% !important}
	.Fieldchanged {color: red !important;}
	.titleDiv {background-color:#925D9C;text-align:center;color: white;width:100%; font-size: 16;font-family:Calibri;height: 20px;font-weight: bold;}
	</style>
	<div class='titleDiv'>Workshops created last week</div>
	<table class='tftable' border='1'>
	<tr style="+tr+" ><th class='th5'>Workshop</th><th class='th13'>ATI</th><th class='th15'>Client name</th><th class='th10'>Start date</th><th class='th5'>Model</th><th>Facilitator(s)</th><th class='th5'>Ppt count</th><th class='th15'>Observers</th></tr>'''
	"""
	tftable = "font-size:12px;color:#333333;width:100%;border-width: 1px;border-color: #729ea5;border-collapse: collapse;}"
	th = "background-color: #234b91 !important;color:white;font-size: 14;font-family:Calibri;border-width: 1px;padding: 6px;border-style: solid;border-color: white;text-align:center;height: 15px;"
	tr = "background-color:#ffffff;text-align:center;"
	td = "font-size:12px;border-width: 1px;padding: 5px;border-style: solid;border-color: #234b91;text-align:center;"
	#.tftable tr:hover {background-color:#ced7d8;}
	th5 = "width:5% !important;"
	th10 = "width:10% !important;"
	th13 = "width:13% !important;"
	th15 = "width:15% !important;"
	#Fieldchanged {color: red !important;}
	titleDiv = "background-color:#925D9C;text-align:center;color: white;width:100%; font-size: 16;font-family:Calibri;height: 20px;font-weight: bold;"
	htmlSendUpdatedWS = "<div style="+titleDiv+">Workshops Updated last week</div><table style="+tftable+" border='1'>"
	htmlSendCreated = "<div style="+titleDiv+">Workshops created last week</div><table style="+tftable+" border='1'>"
	htmlSendDeleted = "<div style="+titleDiv+">Workshops deleted / inactivated last week</div><table style="+tftable+" border='1'>"
	htmlSendCreated = htmlSendCreated + "<tr style="+tr+" ><th style="+th5+th+">Workshop</th><th style="+th13+th+">ATI</th><th style="+th15+th+">Client name</th><th style="+th10+th+">Start date</th><th style="+th5+th+">Model</th><th>Facilitator(s)</th><th style="+th5+th+">Ppt count</th><th style="+th15+th+">Observers</th></tr>"
	htmlSendUpdatedWS = htmlSendUpdatedWS + "<tr style="+tr+" ><th style="+th5+th+">Workshop</th><th style="+th13+th+">ATI</th><th style="+th15+th+">Client name</th><th style="+th10+th+">Start date</th><th style="+th5+th+">Model</th><th>Facilitator(s)</th><th style="+th5+th+">Ppt count</th><th style="+th15+th+">Observers</th></tr>"
	htmlSendDeleted = htmlSendDeleted + "<tr style="+tr+" ><th style="+th5+th+">Workshop</th><th style="+th13+th+">ATI</th><th style="+th15+th+">Client name</th><th style="+th10+th+">Deleted date</th><th style="+th5+th+">Model</th><th>Facilitator(s)</th><th style="+th5+th+">Ppt count</th><th style="+th15+th+">Observers</th><th style="+th5+th+">Status</th></tr>"
	for row in jsonRowsCreated:
		htmlSendCreated = htmlSendCreated + "<tr style="+tr+" ><td style="+th5+td+">"+ str(row['WorkshopId']) + "</td>"+"<td style="+th13+td+">"+ ('Unassigned' if row['ATI'] is None else str(row['ATI']) ) +"</td>"+"<td style="+th15+td+">"+ ('Unassigned' if row['Client'] is None else str(row['Client']) ) +"</td>"+"<td style="+th10+td+">"+ ('Unassigned' if row['StartTime'] is None else str(row['StartTime']) ) +"</td><td style="+th5+td+">"+ row['Model'] +"</td><td style="+td+">"+ ( 'Unassigned' if row['Facilitators'] is None else str(row['Facilitators']) ) +"</td>"+"<td style="+th5+td+">"+ ( 'Unassigned' if row['ParticipantsCount'] is None else str(row['ParticipantsCount']) ) +"</td>"+"<td style="+th15+td+">"+ ( 'Unassigned' if row['ObserversCount'] is None else str(row['ObserversCount']) ) +"</td></tr>"
	for rowUPD in jsonRowsUpd:
		htmlSendUpdatedWS = htmlSendUpdatedWS + "<tr style="+tr+" ><td style="+th5+td+">"+ str(rowUPD['WorkshopId']) + "</td>"+"<td style="+th13+td+">"+ ('Unassigned' if rowUPD['ATI'] is None else str(rowUPD['ATI']) ) +"</td>"+"<td style="+th15+td+">"+ ('Unassigned' if rowUPD['Client'] is None else str(rowUPD['Client']) ) +"</td>"+"<td style="+th10+td+">"+ ('Unassigned' if rowUPD['StartTime'] is None else str(rowUPD['StartTime']) ) +"</td><td style="+th5+td+">"+ rowUPD['Model'] +"</td><td style="+td+">"+ ( 'Unassigned' if rowUPD['Facilitators'] is None else str(rowUPD['Facilitators']) ) +"</td>"+"<td style="+th5+td+">"+ ( 'Unassigned' if rowUPD['ParticipantsCount'] is None else str(rowUPD['ParticipantsCount']) ) +"</td>"+"<td style="+th15+td+">"+ ( 'Unassigned' if rowUPD['ObserversCount'] is None else str(rowUPD['ObserversCount']) ) +"</td></tr>"
	for rowDEL in jsonRowsCreatedDelted:
		htmlSendDeleted = htmlSendDeleted + "<tr style="+tr+" ><td style="+th5+td+">"+ str(rowDEL['WorkshopId']) + "</td>"+"<td style="+th13+td+">"+ ('Unassigned' if rowDEL['ATI'] is None else str(rowDEL['ATI']) ) +"</td>"+"<td style="+th15+td+">"+ ('Unassigned' if rowDEL['Client'] is None else str(rowDEL['Client']) ) +"</td>"+"<td style="+th10+td+">"+ ('Unassigned' if rowDEL['ClosedDate'] is None else str(rowDEL['ClosedDate']) ) +"</td><td style="+th5+td+">"+ rowDEL['Model'] +"</td><td style="+td+">"+ ( 'Unassigned' if rowDEL['Facilitators'] is None else str(rowDEL['Facilitators']) ) +"</td>"+"<td style="+th5+td+">"+ ( 'Unassigned' if rowDEL['ParticipantsCount'] is None else str(rowDEL['ParticipantsCount']) ) +"</td>"+"<td style="+th15+td+">"+ ( 'Unassigned' if rowDEL['ObserversCount'] is None else str(rowDEL['ObserversCount']) ) +"</td><td style="+th5+td+">"+ ( 'Inactivated'  if rowDEL['Closed'] == 2 else 'Deleted' ) +"</tr>"
	for rowDEL in jsonRowsUpdDeleted:
		htmlSendDeleted = htmlSendDeleted + "<tr style="+tr+" ><td style="+th5+td+">"+ str(rowDEL['WorkshopId']) + "</td>"+"<td style="+th13+td+">"+ ('Unassigned' if rowDEL['ATI'] is None else str(rowDEL['ATI']) ) +"</td>"+"<td style="+th15+td+">"+ ('Unassigned' if rowDEL['Client'] is None else str(rowDEL['Client']) ) +"</td>"+"<td style="+th10+td+">"+ ('Unassigned' if rowDEL['ClosedDate'] is None else str(rowDEL['ClosedDate']) ) +"</td><td style="+th5+td+">"+ rowDEL['Model'] +"</td><td style="+td+">"+ ( 'Unassigned' if rowDEL['Facilitators'] is None else str(rowDEL['Facilitators']) ) +"</td>"+"<td style="+th5+td+">"+ ( 'Unassigned' if rowDEL['ParticipantsCount'] is None else str(rowDEL['ParticipantsCount']) ) +"</td>"+"<td style="+th15+td+">"+ ( 'Unassigned' if rowDEL['ObserversCount'] is None else str(rowDEL['ObserversCount']) ) +"</td><td style="+th5+td+">"+ ( 'Inactivated'  if rowDEL['Closed'] == 2 else 'Deleted' ) +"</tr>"
	htmlSendCreated = htmlSendCreated + "</table> <br><br><br>"
	htmlSendUpdatedWS =  htmlSendUpdatedWS + "</table> <br><br>"
	htmlSendDeleted =  htmlSendDeleted + "</table> <br><br>"

	htmlFinalReport = htmlSendCreated + htmlSendUpdatedWS + htmlSendDeleted
	#print("hmlformado::",htmlSendCreated)
	if(paramType == 1):
		blnMtrReportSent = fnSendEmailPassword("IO Simulator: Andromeda - Workshops Created last week", htmlFinalReport, "OIOReports@income-outcome.com")
		#blnMtrReportSent2 = fnSendEmailPassword("IO Simulator: Andromeda - Workshops Created last week", htmlFinalReport, "isc154649@gmail.com")
		#blnMtrReportSent3 = fnSendEmailPassword("IO Simulator: Andromeda - Workshops Created last week", htmlFinalReport, "dany_zantany@hotmail.com")
	else:
		blnMtrReportSent = fnSendEmailPassword("IO Simulator: Distributor - Workshops Created last week", htmlFinalReport, "OIOReports@income-outcome.com")
		#blnMtrReportSent2 = fnSendEmailPassword("IO Simulator: Distributor - Workshops Created last week", htmlFinalReport, "isc154649@gmail.com")
		#blnMtrReportSent3 = fnSendEmailPassword("IO Simulator: Distributor - Workshops Created last week", htmlFinalReport, "dany_zantany@hotmail.com")
	#blnMtrReportSent = fnSendEmailPassword(subject, strBody, email)
	if(blnMtrReportSent):
		return {'intResponse': 200, 'strAnswer': 'Mail send successfully'} 
	return ResponseMessages.err500

def fnCreateContact(idWorkShop, arrayOfContacts):
	#conexion a la bd y creacion del usuario
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	deleteRegisters=0
	if(len(arrayOfContacts) > 0):
		for contact in arrayOfContacts:
			deleteRegisters = deleteRegisters +1
			params = (idWorkShop, contact['UserID'], 1,deleteRegisters)
			cursor.callproc("sp_createContacWorkshop",params)
			MysqlCnx.commit()
	else:
		params = (idWorkShop, 0, 0,deleteRegisters)
		cursor.callproc("sp_createContacWorkshop",params)
		MysqlCnx.commit()


# def fnCreateUpdFacilitators(idWorkShop, arrayOfFacilitators):
# 	#conexion a la bd y creacion del usuario
# 	MysqlCnx = getConectionMYSQL()
# 	cursor = MysqlCnx.cursor()
# 	deleteRegisters=0
# 	if(len(arrayOfFacilitators) > 0):
# 		for facilitator in arrayOfFacilitators:
# 			print("facilitator:::",facilitator)
# 			deleteRegisters = deleteRegisters +1
# 			params = (idWorkShop, facilitator['UserId'], 1,deleteRegisters)
# 			cursor.callproc("sp_createUpdFacilitatorsWorkshop",params)
# 			MysqlCnx.commit()
# 	else:
# 		params = (idWorkShop, 0, 0,deleteRegisters)
# 		cursor.callproc("sp_createUpdFacilitatorsWorkshop",params)
# 		MysqlCnx.commit()
		
# 	#falta crear el email que le llegara al team memeber      !!!!!!!!!!!!!!!!!!!!!!!
# 	#sendTeamMemberEmail(strEmail, strFirstName, strLastName)
# 	return ResponseMessages.sus200

def fnCreateUpdFacilitators(idWorkShop, arrayOfFacilitators):
	# funcion actualizada, agregando a los facilitadores el team id
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	deleteRegisters=0
	if(len(arrayOfFacilitators) > 0):
		#print(arrayOfFacilitators[0]['UserId'])
		params = (idWorkShop)
		cursor.callproc("sp_getFacilitTeamIdByWorkshopId",[params])
		jsonRow = cursor.fetchone()
		#print("HAY team listo?  ",jsonRow)
		teamId = None if jsonRow == None else jsonRow['TeamId']
		if teamId == None:
			params = (idWorkShop, "Team Facilitators")
			cursor.callproc("sp_createTeamAndReturnID",params)
			MysqlCnx.commit()
			jsonRow = cursor.fetchone()
			#print(jsonRow)
			teamId = jsonRow['TeamId']
			fnInitBoard(teamId)
			#print("nuevo team!!    ",teamId)
		
		for facilitator in arrayOfFacilitators:
			#print("facilitator:::",facilitator)
			deleteRegisters = deleteRegisters +1
			params = (idWorkShop, facilitator['UserId'], 1,deleteRegisters, teamId)
			cursor.callproc("sp_createUpdFacilitatorsWorkshop",params)
			MysqlCnx.commit()
	else:
		params = (idWorkShop)
		cursor.callproc("sp_getFacilitTeamIdByWorkshopId",[params])
		jsonRow = cursor.fetchone()
		#print("HAY team listo?  ",jsonRow)
		teamId = 0 if jsonRow == None else jsonRow['TeamId']
		params = (idWorkShop, 0, 0,deleteRegisters, teamId)
		cursor.callproc("sp_createUpdFacilitatorsWorkshop",params)
		MysqlCnx.commit()
		
	#falta crear el email que le llegara al team memeber      !!!!!!!!!!!!!!!!!!!!!!!
	#sendTeamMemberEmail(strEmail, strFirstName, strLastName)
	return ResponseMessages.sus200


def fnCreateUpdateSchedule(idWorkShop, arrayOfSchedules):
	deleteRegisters=0
	for schedule in arrayOfSchedules:
		deleteRegisters = deleteRegisters +1
		jsonResponse = fnExecuteCreateUpdateSchedule(idWorkShop, schedule['day'], schedule['textDay'],deleteRegisters,1)
	if(len(arrayOfSchedules) == 0):
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (idWorkShop, 0, "", 0, 0)
		cursor.callproc("sp_CreateUpdateSchedule",params)
		MysqlCnx.commit()
	return ResponseMessages.sus200

def fnCreateDates(idWorkShop, arrayOfDates):
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	formatted_startdate = None
	formatted_startEnd = None
	for date in arrayOfDates:
		# if(strStartDate != ""):
		# 	dateIni = datetime.fromisoformat(strStartDate[:-1])
		# 	formatted_startdate = dateIni.strftime('%Y-%m-%d %H:%M:%S')
		# if(strEndDate != ""):
		# 	dateFin = datetime.fromisoformat(strEndDate[:-1])
		# 	formatted_startEnd = dateFin.strftime('%Y-%m-%d %H:%M:%S')
		# if(strStartDate != ""):
		# 	dateIni = datetime.fromisoformat(strStartDate[:-1])
		# 	formatted_startdate = dateIni.strftime('%Y-%m-%d %H:%M:%S')
		# if(strEndDate != ""):
		# 	dateFin = datetime.fromisoformat(strEndDate[:-1])
		# 	formatted_startEnd = dateFin.strftime('%Y-%m-%d %H:%M:%S')	
		params = (idWorkShop, date['DateStartTime'], date['DateStartTimeUTC'], date['DateEndTime'], date['DateEndTimeUTC'])
		cursor.callproc("sp_CreateDate",params)
		params = (idWorkShop)
		cursor.callproc("sp_getStartDateTimeByIdWorkshop",[params])
		jsonDates = cursor.fetchone()
		#print("JASON MIN DATEEEEES",jsonDates)
		startDate = jsonDates['StartDate']
		endDate = jsonDates['EndDate']
		params = (idWorkShop, str(startDate), str(endDate))
		cursor.callproc("sp_setStartAndEndDateByWorkshopId",params)
		MysqlCnx.commit()
	return ResponseMessages.sus200

def fnUpdateDates(idWorkShop, arrayOfDates):
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	params = (idWorkShop)
	cursor.callproc("sp_DeleteDatesByWorkshopID",[params])
	MysqlCnx.commit()
	fnCreateDates(idWorkShop, arrayOfDates)
	return ResponseMessages.sus200

def fngetDateData(strIdWorkshop):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (strIdWorkshop)
		#print("antes llamar procedure:strIdWorkshop:",strIdWorkshop)
		cursor.callproc("sp_getDatesByWorkshopID",[params])
		jsonRows = cursor.fetchall()
		for row in jsonRows:
			row['DateStartTimeUTC'] = str(row['DateStartTimeUTC'])
			row['DateEndTimeUTC'] = str(row['DateEndTimeUTC'])
		return ({'intResponse': '200', 'data': jsonRows})
	except Exception as exception:
		print('fngetDateData: ', exception)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}

def fnExecuteCreateUpdateSchedule(idWorkShop, scheduleday, scheduletextDay,deleteRegisters, existsschedules):
	#print("entra execute schedule:",idWorkShop, scheduleday, scheduletextDay, deleteRegisters, existsschedules)
	#conexion a la bd y creacion del usuario
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	params = (idWorkShop, scheduleday, scheduletextDay, deleteRegisters,existsschedules)
	cursor.callproc("sp_CreateUpdateSchedule",params)
	MysqlCnx.commit()
	return ResponseMessages.sus200

def fnCreateUpdateTimes(idWorkShop, arrayOfTimes):
	#print("fnCreateUpdateTimes",arrayOfTimes)
	deleteRegisters=0
	for times in arrayOfTimes:
		deleteRegisters = deleteRegisters +1
		jsonResponse = fnExecuteCreateUpdateTimes(idWorkShop, times['dayofWeek'], times['descTime'], times['dateUTC'], deleteRegisters,1)
	if(len(arrayOfTimes) == 0):
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (idWorkShop, 0, "", 0, 0)
		cursor.callproc("sp_CreateUpdateTimesWorkshop",params)
		MysqlCnx.commit()
	#falta crear el email que le llegara al team memeber      !!!!!!!!!!!!!!!!!!!!!!!
	#sendTeamMemberEmail(strEmail, strFirstName, strLastName)
	return ResponseMessages.sus200

def fnExecuteCreateUpdateTimes(idWorkShop,timesdayofWeek, timesdescTime, dateUTC, deleteRegisters, _existTimes):
	#print("entra execute times:",idWorkShop,timesdayofWeek, timesdescTime, dateUTC, deleteRegisters, _existTimes)
	#conexion a la bd y creacion del usuario
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	params = (idWorkShop, timesdayofWeek, timesdescTime, dateUTC, deleteRegisters,_existTimes)
	cursor.callproc("sp_CreateUpdateTimesWorkshop",params)
	MysqlCnx.commit()
	return ResponseMessages.sus200

'''****************************************************************************
   * Author: DCM
   * Date: 03/26/2021
   * Summary: <Regresar los datos del workshop>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fngetworkshopData(strIdWorkshop):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (strIdWorkshop)
		cursor.callproc("sp_getWorkshopbyID",[params])
		MysqlCnx.commit()
		jsonRows = cursor.fetchall()
		#print("WORKSOOOOOP", jsonRows)
		return ({'intResponse': '200', 'data': jsonRows})
	except Exception as exception:
		print('fngetworkshopData: ', exception)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}


'''****************************************************************************
   * Author: DCM
   * Date: 06/05/2021
   * Summary: <Funcion inicial de validacion de existencia y vigencia de BOARD (workshop)>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fngetExistsWorkshopBoard(intIdWorkshop, currentDateUser):
	try:
		#print("fngetExistsWorkshopBoard",intIdWorkshop, currentDateUser)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (intIdWorkshop, currentDateUser)
		cursor.callproc("sp_getExistsWorkshopBoard",params)
		MysqlCnx.commit()
		jsonRows = cursor.fetchall()
		#print("sp_getExistsWorkshopBoard:", jsonRows)
		return ({'intResponse': '200', 'data': jsonRows})
	except Exception as exception:
		print('fngetExistsWorkshopBoard: ', exception)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}


'''****************************************************************************
   * Author: DCM
   * Date: 19/07/2021
   * Summary: <Funcion que obtiene la timezone del workshop para sacar la relación de deferencias de zonas horarias>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnGetTimeZoneBoard(intIdWorkshop):
	try:
		#print("fngetExistsWorkshopBoard",intIdWorkshop, currentDateUser)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (intIdWorkshop)
		cursor.callproc("sp_getTimeZoneBoard",[params])
		MysqlCnx.commit()
		jsonRows = cursor.fetchone()
		#print("sp_getExistsWorkshopBoard:", jsonRows)
		return ({'intResponse': '200', 'data': jsonRows})
	except Exception as exception:
		print('fngetExistsWorkshopBoard: ', exception)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}



'''****************************************************************************
   * Author: AJLL
   * Date: 19/07/2021
   * Summary: <Funcion que crea un backup de la bd>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnCreateBackupBD(workshopId, month):
	try:
		print("backup CREADO")
		return ({'intResponse': '200', 'strAnswer':'dumb created successfully'})
	except Exception as exception:
		print('fngetExistsWorkshopBoard: ', exception)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}
'''****************************************************************************
   * Author: DCM
   * Date: 29/06/2021
   * Summary: <Funcion para crear un mensaje del chat>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnCreateMessage(TeamId,UserId,avatar,message,isFaciltator,dateMessage,typeChat, workshopId):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (TeamId,UserId,avatar,message,isFaciltator,dateMessage,typeChat, workshopId)
		cursor.callproc("sp_createMessage",params)
		MysqlCnx.commit()
		#jsonRows = cursor.fetchone()
		#print("resp messagechat:", jsonRows)
		return ({'intResponse': '200'})
	except Exception as exception:
		print('error al crear un mensaje de chat: ', exception)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}




'''****************************************************************************
   * Author: DCM
   * Date: 03/26/2021
   * Summary: <Regresar los datos del schedule>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fngetschedulesData(strIdWorkshop):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (strIdWorkshop)
		#print("antes llamar procedure:strIdWorkshop:",strIdWorkshop)
		cursor.callproc("sp_getSchedulebyworkshopID",[params])
		MysqlCnx.commit()
		jsonRows = cursor.fetchall()
		return ({'intResponse': '200', 'data': jsonRows})
	except Exception as exception:
		print('fngetschedulesData: ', exception)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}

'''****************************************************************************
   * Author: DCM
   * Date: 03/28/2021
   * Summary: <Regresar los datos del Times del workshop>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fngTimesData(strIdWorkshop):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (strIdWorkshop)
		#print("antes llamar procedure:strIdWorkshop:",strIdWorkshop)
		cursor.callproc("sp_getTimesbyworkshopID",[params])
		MysqlCnx.commit()
		jsonRows = cursor.fetchall()
		return ({'intResponse': '200', 'data': jsonRows})
	except Exception as exception:
		print('fngTimesData: ', exception)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}

'''****************************************************************************
   * Author: DCM
   * Date: 03/31/2021
   * Summary: <Regresar los facilitadores por id workshop>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnfacilitatorsgetData(strIdWorkshop):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (strIdWorkshop)
		#print("antes llamar procedure:strIdWorkshop:",strIdWorkshop)
		cursor.callproc("sp_getFacilitorsbyworkshopID",[params])
		MysqlCnx.commit()
		jsonRows = cursor.fetchall()
		#print("jsonRowsFACI",jsonRows)
		return ({'intResponse': 200, 'data': jsonRows})
	except Exception as exception:
		print('fnfacilitatorsgetData: ', exception)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}

'''****************************************************************************
   * Author: DCM
   * Date: 08/04/2021
   * Summary: <Regresar contador de observers y members por id workshop>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fngetcountMembersObservers(strIdWorkshop):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (strIdWorkshop)
		# print("antes llamar procedure:strIdWorkshop:",strIdWorkshop)
		cursor.callproc("sp_getcountMembersObservers",[params])
		MysqlCnx.commit()
		jsonRows = cursor.fetchall()
		# print("regresa la bd:",jsonRows)
		return ({'intResponse': '200', 'countObservers': jsonRows[0]["countObservers"], 'countMembers': jsonRows[0]["countMembers"]})
	except Exception as exception:
		print('fngetcountMembersObservers: ', exception)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}

'''****************************************************************************
   * Author: DCM
   * Date: 03/29/2021
   * Summary: <Regresar los contactos  del workshop>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fngetcontactsbyworkshopId(strIdWorkshop):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (strIdWorkshop)
		print("antes llamar procedure:strIdWorkshop:",strIdWorkshop)
		cursor.callproc("sp_getContactsbyworkshopID",[params])
		MysqlCnx.commit()
		jsonRows = cursor.fetchall()
		return ({'intResponse': '200', 'data': jsonRows})
	except Exception as exception:
		print('fngetcontactsbyworkshopId: ', exception)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}


'''****************************************************************************
   * Author: DCM
   * Date: 03/26/2021
   * Summary: <Regresar todos los workshops que le correspondan>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fngetAllworkshopData(_type, idUser,idDistributor):
	i=0
	j=0
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (_type, idUser,idDistributor)
		cursor.callproc("sp_getAllWorkshopsNew",params)
		MysqlCnx.commit()
		jsonRows = cursor.fetchall()
		for workshop in jsonRows:
			workshop['StartDate'] = workshop['StartDate'].strftime('%Y-%m-%d') if workshop['StartDate'] != None else workshop['StartDate']
		# cursor.callproc("sp_getAllWorkshopStartDateByUserType",params)
		# jsonRowsStartDate = cursor.fetchall()
		# # print(jsonRowsStartDate)
		# for workShop in jsonRows:
		# 	# print("Comparando", workShop['WorkshopId'],jsonRowsStartDate[j]['WorkshopId'] )
		# 	if(j < len(jsonRowsStartDate)):
		# 		print(j)
		# 		if workShop['WorkshopId'] == jsonRowsStartDate[j]['WorkshopId']:
		# 			print(jsonRowsStartDate[j]['StartDate'])
		# 			workShop['StartDate'] = jsonRowsStartDate[j]['StartDate']
		# 			print(workShop['StartDate'])
		# 			j+=1
		# 	jsonResponse = fnGetTeamsByWorkShopId(workShop['WorkshopId'])
		# 	if(jsonResponse['intResponse'] == 200):
		# 		workShop['Teams'] = jsonResponse['Teams']
		# 	else:
		# 		workShop['Teams'] = 0
		# print(jsonRows)
		return ({'intResponse': '200', 'data': jsonRows})
	except Exception as exception:
		print('getallworkshops: ', exception)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}

'''****************************************************************************
   * Author: BPR
   * Date: 04/05/2021
   * Summary: <Valida que no exista un workShop con la misma fecha y facilitator>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnValidDateFacilitator(dates, facilitators):
	try:
		#print("dates",dates)
		#print("facilitators",facilitators)
		arrResponse = []
		for facilitator in facilitators:
			for date in dates:
				jsonResponse = fnExistDateFacilitator(date['dateUTC'],facilitator['UserId'])
				#print("JSON DENTRO DE FOR",jsonResponse)
				if(jsonResponse != None):
					if(jsonResponse['intResponse'] == 200):
						#print("data",jsonResponse['data'])
						arrResponse.append(jsonResponse['data'])
		#print("arrResponse",arrResponse)
		return ({'intResponse': '200', 'data': arrResponse})
	except Exception as exception:
		print('fnValidDateFacilitator: ', exception)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}


def fnExistDateFacilitator(date, facilitatorId):
	try:
		print("date",date)
		#print("facilitatorId",facilitatorId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (date, facilitatorId)
		cursor.callproc("sp_validDateFacilitator",params)
		MysqlCnx.commit()
		jsonRows = cursor.fetchall()
		#print("jsonRows",jsonRows)
		return ({'intResponse': 200, 'data': jsonRows[0]})
	except Exception as exception:
		print('fnValidDateFacilitator: ', exception)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}
'''****************************************************************************
   * Author: DCM
   * Date: 03/03/2021
   * Summary: <Eliminar teams y teamMembers>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fndeleteTeamsAndMembersWorkshop1(workshopID):
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	params = (workshopID)
	cursor.callproc("sp_DeleteMembersAndTeams",[params])
	MysqlCnx.commit()
	return ResponseMessages.sus200

#########################################START EMAILS##############################################33

'''****************************************************************************
   * Author: BPR
   * Date: 22/04/2021
   * Summary: <Obtener todos los emails>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnGetAllEmailUsers(workShopId):
	try:
		jsnWorkShop = fngetworkshopData(workShopId)
		print('jsnWorkShop', jsnWorkShop)
		arrWelcomeUsers = fnGetAllEmailUsersByType(workShopId,1,0)
		arrWelcomeData = fnGetDataEmailByWorkShopID(workShopId,1,0)
		#arrWelcomeData["MailDeliveryDate"] = arrWelcomeData["MailDeliveryDate"].strftime("%Y-%m-%dT00:00:00")

		arrReminderPUsers = fnGetAllEmailUsersByType(workShopId,2,1)
		arrReminderPData = fnGetDataEmailByWorkShopID(workShopId,2,1)
		arrReminderOCUsers = fnGetAllEmailUsersByType(workShopId,2,2)
		arrReminderOCData = fnGetDataEmailByWorkShopID(workShopId,2,2)

		arrUpcomingUsers = fnGetAllEmailUsersByType(workShopId,3,0)
		arrUpcomingData = fnGetDataEmailByWorkShopID(workShopId,3,0)

		jsnWel = fndeleteTeamsAndMembersWorkshop(arrWelcomeUsers,arrWelcomeData)
		jsnOC = fndeleteTeamsAndMembersWorkshop(arrReminderOCUsers,arrReminderOCData)
		jsnP = fndeleteTeamsAndMembersWorkshop(arrReminderPUsers,arrReminderPData)
		jsnUp = fndeleteTeamsAndMembersWorkshop(arrUpcomingUsers,arrUpcomingData)

		return {
			"intResponse":200,"welcome": jsnWel, 
			"reminderOC": jsnOC, "reminderP": jsnP, 
			"upcoming": jsnUp,
			"workShop": {
				"Client": jsnWorkShop['data'][0]['Client'],
				"StartDate": jsnWorkShop['data'][0]['StartDate']
			}
		}
	except Exception as e:
		print(e)
		return ResponseMessages.err500

def fnGetAllEmailUsersByType(workShopId,intEmailType,intUserType):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (workShopId,intEmailType,intUserType)
		cursor.callproc("sp_getAllUsersOfEmailByWorkShopID",params)
		MysqlCnx.commit()
		jsnRows = cursor.fetchall()
		#print("fnGetAllEmailUsersByType:",jsnRows)
		return {"intResponse":200,"emailsUsers":jsnRows}
	except Exception as e:
		print(e)
		return ResponseMessages.err500

def fnGetDataEmailByWorkShopID(workShopId,intEmailType,intUserType):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (workShopId,intEmailType,intUserType)
		cursor.callproc("sp_getDataEmailByWorkshopID",params)
		MysqlCnx.commit()
		jsnRows = cursor.fetchall()
		if (jsnRows[0]['Active'] == 0):
			jsnRows[0]['Active'] = False
		else:
			jsnRows[0]['Active'] = True
		#print("fnGetDataEmailByWorkShopID:",jsnRows)
		return {"intResponse":200,"emailsData":jsnRows[0]}
	except Exception as e:
		print(e)
		return ResponseMessages.err500

def fndeleteTeamsAndMembersWorkshop(arrUsers,arrData):
	if(arrUsers['intResponse'] == 200):
		arrUsersAux =  arrUsers['emailsUsers']
	else:
		arrUsersAux=[]

	if(arrData['intResponse'] == 200):
		arrDataAux =  arrData['emailsData']
	else:
		arrDataAux=[]
	return {"Users": arrUsersAux, "Data": arrDataAux }


def fnGetEmailById(emailId):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = ([emailId])
		cursor.callproc("sp_getEmailByID",params)
		MysqlCnx.commit()
		jsnRows = cursor.fetchall()
		#print("info mail:", jsnRows[0])
		jsnRows[0]["MailDeliveryDate"] = jsnRows[0]["MailDeliveryDate"].strftime("%Y-%m-%dT00:00:00")
		#print("jsnRows[0]formateado:",jsnRows[0]["MailDeliveryDate"])
		if (jsnRows[0]['Active'] == 0):
			jsnRows[0]['Active'] = False
		else:
			jsnRows[0]['Active'] = True
		print("*****************************************************")
		jsnWorkShop = fngetworkshopData(jsnRows[0]['WorkShopId'])
		print('info jsnWorkShop:', jsnWorkShop)
		jsnWorkShopDates = fngetDateData(jsnRows[0]['WorkShopId'])
		#print('info jsnWorkShopDates:', jsnWorkShopDates)
		jsnWorkShop["data"][0]['dates'] = jsnWorkShopDates["data"]
		#comezamos con los replaces para la info de body y subject del mail
		#strMonthStart = datetime.strptime(jsnWorkShop["data"][0]["StartDate"],"%m/%d/%Y")
		strmonth = fnGetMonthString(jsnWorkShop["data"][0]["StartDate"].strftime("%m"))
		#print("jsnWorkShop[fsd", jsnWorkShop["data"][0]['dates'][0]["DateStartTime"])
		strStarDateTime = jsnWorkShop["data"][0]['dates'][0]["DateStartTime"].strftime("%m-%d-%Y at %H:%M")
		strGeneralLink= "https://app.income-outcome.com/play/board/"+str(jsnRows[0]['WorkShopId'])+"/general"
		objContacts= fnGetAllContactsByWorkshopID(jsnRows[0]['WorkShopId'])
		strContacts= ""
		objContacts['contacts'] = [] if objContacts['contacts'] == None else objContacts['contacts'] 
		for contact in objContacts['contacts']:
			strContacts = strContacts + contact["FirstName"] + " " + contact["LastName"]+ "\n"
		jsnRows[0]["subject"] = jsnRows[0]["subject"].replace("<br>", "\n")
		jsnRows[0]["body"] = jsnRows[0]["body"].replace("<br>", "\n")
		jsnRows[0]["subject"] = jsnRows[0]["subject"].replace("@_workshopClient", jsnWorkShop["data"][0]["Client"])
		jsnRows[0]["body"] = jsnRows[0]["body"].replace("@_workshopClient", jsnWorkShop["data"][0]["Client"])
		jsnRows[0]["subject"] = jsnRows[0]["subject"].replace("@_monthStart", strmonth)
		jsnRows[0]["body"] = jsnRows[0]["body"].replace("@_monthStart", strmonth)
		jsnRows[0]["subject"] = jsnRows[0]["subject"].replace("@_datetimeWorkshopStart", strStarDateTime)
		jsnRows[0]["body"] = jsnRows[0]["body"].replace("@_datetimeWorkshopStart", strStarDateTime)
		jsnRows[0]["subject"] = jsnRows[0]["subject"].replace("@_generalLinktoPlay", strGeneralLink)
		jsnRows[0]["body"] = jsnRows[0]["body"].replace("@_generalLinktoPlay", strGeneralLink)
		jsnRows[0]["subject"] = jsnRows[0]["subject"].replace("@_contactsList", strContacts)
		jsnRows[0]["body"] = jsnRows[0]["body"].replace("@_contactsList", strContacts)
		#print("strSubject", strSubject)
		#print("strbody", strbody)
		return {
			"intResponse":200, 
			"email":jsnRows[0], 
			"workShop": jsnWorkShop["data"][0]
			}
	except Exception as e:
		print(e)
		return ResponseMessages.err500

def fnGetMonthString(strMonthof2Digits):
	if strMonthof2Digits == "01":
		return "January"
	elif strMonthof2Digits == "02":
		return "February"
	elif strMonthof2Digits == "03":
		return "March"
	elif strMonthof2Digits == "04":
		return "April"
	elif strMonthof2Digits == "05":
		return "May"
	elif strMonthof2Digits == "06":
		return "June"
	elif strMonthof2Digits == "07":
		return "July"
	elif strMonthof2Digits == "08":
		return "August"
	elif strMonthof2Digits == "09":
		return "September "
	elif strMonthof2Digits == "10":
		return "Octuber"
	elif strMonthof2Digits == "11":
		return "November"
	else:
		return "December"

def fnGetTemplateById(templateId):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = ([templateId])
		cursor.callproc("sp_getTemplateByID",params)
		MysqlCnx.commit()
		jsnRows = cursor.fetchone()
		return {
			"intResponse":200, 
			"template":jsnRows
			}
	except Exception as e:
		print(e)
		return ResponseMessages.err500


def fnGetTemplates():
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		cursor.callproc("sp_getTemplates")
		jsonRows = cursor.fetchall()
		print(jsonRows)
		return {'intResponse': 200, 'strAnwser': 'Success', 'templates': jsonRows}
	except Exception as e:
		print(e)
		return ResponseMessages.err500

def fnUpdateTemplateById(TemplateId, body, subject):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (TemplateId, body, subject)
		cursor.callproc("sp_UpdateTemplate",params)
		MysqlCnx.commit()
		return ResponseMessages.sus200	
	except Exception as exception:
		print(exception)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

def fnUpdateEmail(emailId, active, mailDeliveryDate, body, subject):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (emailId, active, mailDeliveryDate, body, subject)
		cursor.callproc("sp_updateEmail",params)
		MysqlCnx.commit()
		return ResponseMessages.sus200	
	except Exception as exception:
		print(exception)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

def fnresendEmailToArrayUsers(workshopId, lstUsers, emailId):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (emailId)
		cursor.callproc("sp_getEmailByID",[params])
		jsonEmailRow = cursor.fetchone()
		for user in lstUsers:
			jsonEmailRow['subject'] = jsonEmailRow['subject'].replace("\n", "<br>")
			jsonEmailRow['body'] = jsonEmailRow['body'].replace("\n", "<br>")
			print("replaceok",jsonEmailRow['body'])
			jsonRespones = sendWorkshopEmail(user['Email'],jsonEmailRow['subject'], jsonEmailRow['body'])
			if(jsonRespones['intResponse']!=200):
				return jsonRespones
		return ResponseMessages.sus200	
	except Exception as exception:
		print(exception)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

def fnresendEmailToArrayUsersNew(workshopId, lstUsers, emailId):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = ([emailId])
		cursor.callproc("sp_getEmailByID",params)
		MysqlCnx.commit()
		jsnRows = cursor.fetchall()
		jsnRows[0]["MailDeliveryDate"] = jsnRows[0]["MailDeliveryDate"].strftime("%Y-%m-%dT00:00:00")
		if (jsnRows[0]['Active'] == 0):
			jsnRows[0]['Active'] = False
		else:
			jsnRows[0]['Active'] = True
		print("*****************************************************")
		jsnWorkShop = fngetworkshopData(jsnRows[0]['WorkShopId'])
		print('info jsnWorkShop:', jsnWorkShop)
		jsnWorkShopDates = fngetDateData(jsnRows[0]['WorkShopId'])
		jsnWorkShop["data"][0]['dates'] = jsnWorkShopDates["data"]
		#comezamos con los replaces para la info de body y subject del mail
		strmonth = fnGetMonthString(jsnWorkShop["data"][0]["StartDate"].strftime("%m"))
		strStarDateTime = jsnWorkShop["data"][0]['dates'][0]["DateStartTime"].strftime("%m-%d-%Y at %H:%M")
		strGeneralLink= "https://app.income-outcome.com/play/board/"+str(jsnRows[0]['WorkShopId'])+"/general"
		objContacts= fnGetAllContactsByWorkshopID(jsnRows[0]['WorkShopId'])
		strContacts= ""
		objContacts['contacts'] = [] if objContacts['contacts'] == None else objContacts['contacts'] 
		for contact in objContacts['contacts']:
			strContacts = strContacts + contact["FirstName"] + " " + contact["LastName"]+ "\n"
		jsnRows[0]["subject"] = jsnRows[0]["subject"].replace("<br>", "\n")
		jsnRows[0]["body"] = jsnRows[0]["body"].replace("<br>", "\n")
		jsnRows[0]["subject"] = jsnRows[0]["subject"].replace("@_workshopClient", jsnWorkShop["data"][0]["Client"])
		jsnRows[0]["body"] = jsnRows[0]["body"].replace("@_workshopClient", jsnWorkShop["data"][0]["Client"])
		jsnRows[0]["subject"] = jsnRows[0]["subject"].replace("@_monthStart", strmonth)
		jsnRows[0]["body"] = jsnRows[0]["body"].replace("@_monthStart", strmonth)
		jsnRows[0]["subject"] = jsnRows[0]["subject"].replace("@_datetimeWorkshopStart", strStarDateTime)
		jsnRows[0]["body"] = jsnRows[0]["body"].replace("@_datetimeWorkshopStart", strStarDateTime)
		jsnRows[0]["subject"] = jsnRows[0]["subject"].replace("@_generalLinktoPlay", strGeneralLink)
		jsnRows[0]["body"] = jsnRows[0]["body"].replace("@_generalLinktoPlay", strGeneralLink)
		jsnRows[0]["subject"] = jsnRows[0]["subject"].replace("@_contactsList", strContacts)
		jsnRows[0]["body"] = jsnRows[0]["body"].replace("@_contactsList", strContacts)
		jsnRows[0]["subject"] = jsnRows[0]["subject"].replace("\n", "<br>")
		jsnRows[0]["body"] = jsnRows[0]["body"].replace("\n", "<br>")

		for user in lstUsers:
			strPersonalLink = "https://app.income-outcome.com/play/board/"+str(jsnRows[0]['WorkShopId']) + "/"+str(user['Email'])
			jsnRows[0]["subject"] = jsnRows[0]["subject"].replace("@_PersonalLink", strPersonalLink)
			jsnRows[0]["body"] = jsnRows[0]["body"].replace("@_PersonalLink", strPersonalLink)
			print("jsnRows[0]['subject']::",jsnRows[0]['subject'])
			print("replaceok::",jsnRows[0]['body'])
			jsonRespones = sendWorkshopEmail(user['Email'],jsnRows[0]['subject'], jsnRows[0]['body'])
			if(jsonRespones['intResponse']!=200):
				return jsonRespones
		return ResponseMessages.sus200
		return {
			"intResponse":200, 
			"email":jsnRows[0], 
			"workShop": jsnWorkShop["data"][0]
			}
	except Exception as e:
		print(e)
		return ResponseMessages.err500

def sendEmailJob():
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		cursor.callproc("sp_getWorkshopsDeliverEmailJob",[])
		jsonWorkshops = cursor.fetchall()

		for workshop in jsonWorkshops:
			#send email for each workshop
			arrWelcomeUsers = fnGetAllEmailUsersByType(workshop['WorkShopId'],workshop['EmailType'],workshop['UserType'])
			for user in arrWelcomeUsers['emailsUsers']:
				jsonRespones = sendWorkshopEmail(user['Email'],workshop['subject'], workshop['body'])
				if(jsonRespones['intResponse']!=200):
					return jsonRespones

		return {'intResponse': 200, 'strAsnwer':'emails delivered successfully'}
		# arrWelcomeUsers = fnGetAllEmailUsersByType(workShopId,1,0)
		# arrWelcomeData = fnGetDataEmailByWorkShopID(workShopId,1,0)

		# arrReminderOCUsers = fnGetAllEmailUsersByType(workShopId,2,1)
		# arrReminderOCData = fnGetDataEmailByWorkShopID(workShopId,2,1)

		# arrReminderPUsers = fnGetAllEmailUsersByType(workShopId,2,2)
		# arrReminderPData = fnGetDataEmailByWorkShopID(workShopId,2,2)

		# arrUpcomingUsers = fnGetAllEmailUsersByType(workShopId,3,0)
		# arrUpcomingData = fnGetDataEmailByWorkShopID(workShopId,3,0)

		# jsnWel = fndeleteTeamsAndMembersWorkshop(arrWelcomeUsers,arrWelcomeData)
		# jsnOC = fndeleteTeamsAndMembersWorkshop(arrReminderOCUsers,arrReminderOCData)
		# jsnP = fndeleteTeamsAndMembersWorkshop(arrReminderPUsers,arrReminderPData)
		# jsnUp = fndeleteTeamsAndMembersWorkshop(arrUpcomingUsers,arrUpcomingData)

		# return {
		# 	"intResponse":200,"welcome": jsnWel, 
		# 	"reminderOC": jsnOC, "reminderP": jsnP, 
		# 	"upcoming": jsnUp,
		# 	"workShop": {
		# 		"Client": jsnWorkShop['data'][0]['Client'],
		# 		"StartDate": jsnWorkShop['data'][0]['StartDate']
		# 	}
		# }

		
		return ResponseMessages.sus200	
	except Exception as exception:
		print(exception)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})


def sendWorkshopEmail(email, subject, body):
	try:
		strBody = '''
		<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
		<html>

		<head>
			<meta http-equiv="CONTENT-TYPE" content="text/html; charset=utf-8" />
			<title></title>
			<meta name="GENERATOR" content="LibreOffice 4.1.6.2 (Linux)" />
			<meta name="AUTHOR" content="Linkthinks SAPI de CV" />
			<meta name="CREATED" content="20210305;172800000000000" />
			<meta name="CHANGED" content="0;0" />
			<meta name="KSOProductBuildVer" content="2058-11.2.0.10017" />
			<style type="text/css">
				<!--
				@page {
					margin-left: 1.25in;
					margin-right: 1.25in;
					margin-top: 1in;
					margin-bottom: 1in
				}

				P {
					margin-bottom: 0.08in;
					direction: ltr;
					widows: 2;
					orphans: 2
				}

				P.western {
					font-family: "Calibri", serif;
					so-language: en-US
				}

				P.cjk {
					so-language: zh-CN
				}

				P.ctl {
					font-family: ;
					so-language: ar-SA
				}

				A:link {
					color: #0000ff;
					so-language: zxx
				}
				-->
			</style>
		</head>

		<body lang="es-MX" link="#0000ff" dir="LTR">
			<p lang="en-US" class="western" align="JUSTIFY" style="text-align: center;">
				<img src="https://app.income-outcome.com/IOlogo_linear21.png" name="graphics1" align="CENTER" hspace="12"
					width="305" height="77" border="0" /><br />
			</p>
			<p>
				''' + body + '''
			</p>
			<p lang="en-US" class="western" align="JUSTIFY" style="margin-bottom: 0in">
				<font face="Arial, serif">
					<font size="3">If you have any problems please contact </font>
				</font><a href="http://mailto@petra@income-outcome.com">
					<font color="#1155cc">
						<font face="Arial, serif">
							<font size="3"><u>Petra Andrews</u></font>
						</font>
					</font>
				</a>
				<font face="Arial, serif">
					<font size="3">.</font>
				</font>
			</p>
			<p lang="en-US" class="western" align="JUSTIFY" style="margin-bottom: 0in">
				<font face="Arial, serif">
					<font size="3"><b>Have a great day!</b></font>
				</font>
			</p>
			<p lang="en-US" class="western" align="JUSTIFY" style="margin-bottom: 0in">
				<font face="Arial, serif">
					<font size="3"><b>Geoff, Nikolai, Ana &amp; Petra</b></font>
				</font>
			</p>
			<p lang="en-US" class="western" align="JUSTIFY" style="margin-bottom: 0in">
				<img src="https://app.income-outcome.com/IOlogo_linear21.png" name="image2.png" align="LEFT" hspace="12"
					width="608" height="1" border="0" /><br />
			</p>
		</body>

		</html>
		'''
		# Enviar Correo

		# lmcs_4@hotmail.com
		blnMtrReportSent = fnSendEmailPassword(subject, strBody, email)
		if(blnMtrReportSent):
			return {'intResponse': 200, 'strAnswer': 'Mail send successfully'}
		else:
			return {'intResponse': 202, 'strAnswer': 'Something wrong on send email'}
	except Exception as exception:
		print('Error', exception)
		return ResponseMessages.err500
#####################################################END EMAILS##################################################

######################################################CLIENTS####################################################

'''****************************************************************************
   * Author: BPR
   * Date: 03/03/2021
   * Summary: <Obtener todos los distribuidores y el contador de todos sus contactos>
   * Edited: BPR
   * 
   * Summary change: <Obtencion del Last login mas reciente entre sus usuarios >
   *
   ****************************************************************************'''
def fnGetAllClients():
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		cursor.callproc("sp_getallClients")
		jsonRows = cursor.fetchall()
		#print(jsonRows)
		for client in jsonRows:
			jsonResponse = fnGetLastLoginFromClientUser(client['ClientID'])
			if(jsonResponse['intResponse'] == 200):
				client['LastLogin'] = jsonResponse['LastLogin']
			else:
				client['LastLogin'] = None
		return {'intResponse': 200, 'strAnwser': 'Success', 'clients': jsonRows}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
   * Author: BPR
   * Date: 05/05/2021
   * Summary: <Obtener todos contactos asociados a un cliente>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnGetContactsByClientID(strID):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (strID)
		cursor.callproc("sp_getallUsersByClientID", [params])
		jsonRows = cursor.fetchall()
		#print(jsonRows)
		return {'intResponse': 200, 'strAnwser': 'Success', 'contacts': jsonRows}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})


'''****************************************************************************
   * Author: BPR
   * Date: 05/05/2021
   * Summary: <Dar de alta un cliente y sus contactos>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnCreateClientAndContacts(clientName, arrayOfContacts, isResponseErrorEmailAlreadyRegister):
	i = 0
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (clientName)
		if isResponseErrorEmailAlreadyRegister:
			cursor.callproc("sp_getClientByName",[params])
			jsonResponseClient = cursor.fetchone()
			if(jsonResponseClient != None):
				idOfClient = jsonResponseClient['ClientID']
		else:
			cursor.callproc("sp_createClientAndReturnID",[params])
			MysqlCnx.commit()
			jsonRow = cursor.fetchone()
			#print(jsonRow)
			if jsonRow['intResponse'] == 203:
				return ({'intResponse': 203, 'strAnswer': 'Client already exists!','remainingEmails': arrayOfContacts })
			idOfClient = jsonRow['ClientID']
	
		#print(arrayOfContacts)
		#print(idOfDistributor)
		for contact in arrayOfContacts:
			print(contact)
			isFacilitator = 0
			jsonResponse = fnCreateUser(contact['FirstName'],contact['LastName'], contact['Email'],6,None,idOfClient, isFacilitator, contact['Country'], contact['City'], contact['Notes'], contact['Languages'],contact['Phone'], contact['AlternatePhone'] )
			print("JSON DENTRO DE FOR",jsonResponse)
			if(jsonResponse != None):
				if(jsonResponse['intResponse'] == 203):
					remainingEmails = arrayOfContacts[i:]
					return(
						{'intResponse': 203, 
						'strAnswer': 'User already exists!', 
						'emailInvalid': arrayOfContacts[i]['Email'], 
						'remainingEmails': remainingEmails
						})
			i+=1
		return ResponseMessages.sus200
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
   * Author: BPR
   * Date: 05/05/2021
   * Summary: <Actualizar la informacion de un cliente y sus contactos>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnUpdateClient(clientID, clientName, arrayOfContacts, arrayOfNewContacts):
	i = 0
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		#------
		params = (clientID, clientName)
		cursor.callproc("sp_updateNameClient",params)
		MysqlCnx.commit()
		jsonRow = cursor.fetchone()
		#print(jsonRow)
		if jsonRow['intResponse'] == 203:
			return ({'intResponse': 203, 'strAnswer': 'Client already exists!','remainingEmails': arrayOfContacts + arrayOfNewContacts })
		#------
		for contact in arrayOfContacts:
			#print(contact)
			isFacilitator = 0
			isChange = False
			if('isChangeEmail' in contact):
				#print("CAMBIO DE EMAIL? ",contact['isChangeEmail'])
				if(contact['isChangeEmail']):
					isChange = True
			jsonResponse = fnUpdateUser(contact['UserID'],contact['FirstName'],contact['LastName'], contact['Email'],6, None, contact['ClientID'], isFacilitator, contact['Country'], contact['City'], contact['Notes'], contact['Languages'],contact['Phone'], isChange, contact['AlternatePhone'] )
			#print("JSON DENTRO DE FOR",jsonResponse)
			if(jsonResponse['intResponse'] == 203):
				remainingEmails = arrayOfContacts[i:]
				remainingEmails = remainingEmails + arrayOfNewContacts
				return(
					{'intResponse': 203, 
					'strAnswer': 'User already exists!', 
					'emailInvalid': arrayOfContacts[i]['Email'], 
					'remainingEmails': remainingEmails
					})
			else: 
				if(isChange):
					resp = changeEmailSendPassword(contact['Email'],contact['UserID'],contact['FirstName'],contact['LastName'])
					#print(resp)
					if resp['intResponse']!=200:
						return resp
			i+=1
		i=0
		for contact in arrayOfNewContacts:
			print(contact)
			isFacilitator = 0
			jsonResponse = fnCreateUser(contact['FirstName'],contact['LastName'], contact['Email'],6, None,  clientID, isFacilitator, contact['Country'], contact['City'], contact['Notes'], contact['Languages'],contact['Phone'],contact['AlternatePhone'])
			#print("JSON DENTRO DE FOR New CONTACTS",jsonResponse)
			if(jsonResponse != None):
				if(jsonResponse['intResponse'] == 203):
					remainingEmails = arrayOfNewContacts[i:]
					return(
						{'intResponse': 203, 
						'strAnswer': 'User already exists!', 
						'emailInvalid': arrayOfNewContacts[i]['Email'], 
						'remainingEmails': remainingEmails
						})
			i+=1
		return ResponseMessages.sus200
	except Exception as exception:
		print("fnupdateClient", exception)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})


'''****************************************************************************
   * Author: BPR
   * Date: 03/03/2021
   * Summary: <Obtener el ingreso mas reciente entre todos sus usuarios>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnGetLastLoginFromClientUser(ClientID):
	try:
		print("ClientID",ClientID)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (ClientID)
		cursor.callproc("sp_getLastLoginClientUser", [params])
		jsonRows = cursor.fetchall()
		#print("LASTLOGIN",jsonRows)
		return {'intResponse': 200, 'LastLogin': jsonRows[0]['LastLogin']}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
   * Author: BPR
   * Date: 03/03/2021
   * Summary: <Obtener el contacto de un cliente(Usuario)>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnGetClientUserById(strId):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (strId)
		cursor.callproc("sp_getClientUserbyID",[params])
		MysqlCnx.commit()
		jsnRow = cursor.fetchone()
		if jsnRow == None:
			return {'intResponse': 404, 'strAnswer': 'User not found'}
		#print("objResult::",jsnRow)
		return {'intResponse': 200, 'data':jsnRow}
	except Exception as exception:
		print('fnGetClientUserById: ', exception)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}

'''****************************************************************************
   * Author: BPR
   * Date: 07/05/2021
   * Summary: <Obtener los contacto de un cliente(Usuario)>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''

def fnGetOnlyContactsByClientID(strID):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (strID)
		cursor.callproc("sp_getOnlyallContactsByClientID", [params])
		jsonRows = cursor.fetchall()
		#print(jsonRows)
		return {'intResponse': 200, 'strAnwser': 'Success', 'contacts': jsonRows}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

#def fnAssociateClientContactsToWs(workShopId, arrayIdOfContacts):
#	try:
#		#conexion a la bd y creacion del usuario
#		MysqlCnx = getConectionMYSQL()
#		cursor = MysqlCnx.cursor()
#		paramsD = (workShopId)
#		cursor.callproc("desAssociateAllContactsWs",[paramsD])
#		MysqlCnx.commit()
#		for contactId in arrayIdOfContacts:
#			params = (workShopId, contactId)
#			cursor.callproc("sp_associateClientContactsToWs",params)
#			MysqlCnx.commit()
#		return {'intResponse': 200, 'strAnwser': 'Success', 'contacts': jsonRows}
#	except Exception as exception:
#		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

###################################################END CLIENTS###############################################



#####################################################START RULES##################################################
'''****************************************************************************
   * Author: LJGF
   * Date: 10/05/2021
   * Summary: <Obtener los contacto de un cliente(Usuario)>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''

def fnGetRules(languagesId):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (languagesId)
		cursor.callproc("sp_getRulesbyId",[params])
		MysqlCnx.commit()
		jsnRow = cursor.fetchall()
		if jsnRow == None:
			return {'intResponse': 404, 'strAnswer': 'User not found'}
		#print("objResult::",jsnRow)
		return {'data':jsnRow}
	except Exception as exception:
		print('fnGetUserInfo: ', exception)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}

######################################################END RULES####################################################

#####################################################START BALANCE SHEET##################################################
'''****************************************************************************
   * Author: LJGF
   * Date: 18/05/2021
   * Summary: <Obtener los contacto de un cliente(Usuario)>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnDeleteMesBalance(teamId, cantidad):
	print("fnDeleteMesBalance datos", teamId, cantidad)
	try:
		for x in range(1, cantidad+1):
			print("cantidad de meses delete",teamId, x)
			fnDeleteMesxMesBalance(teamId)
		return ResponseMessages.sus200
	except Exception as exception:
		print("fnDeleteMesBalanceError", exception)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

def fnDeleteMesxMesBalance(teamId):
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	params = (teamId)
	cursor.callproc("sp_DeleteQuantitiesBalanceSheet",[params])
	MysqlCnx.commit()
	return ResponseMessages.sus200

def fnGetCountRegistros(teamId):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId)
		cursor.callproc("sp_GetCountQuantitiesBalanceSheet",[params])
		MysqlCnx.commit()
		jsnRow = cursor.fetchone()
		if jsnRow == None:
			return {'intResponse': 404, 'data':jsnRow}
		#print("objResult::",jsnRow)
		return {'data':jsnRow}
	except Exception as exception:
		print('fnGetUserInfo: ', exception)
		return {'intResponse': 500, 'strAnswer': exception.args[1]}


def fnGetStep(teamId):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId)
		cursor.callproc("sp_getSimpleAndIncomeSteps",[params])
		MysqlCnx.commit()
		jsnRow = cursor.fetchone()
		if jsnRow == None:
			return {'intResponse': 404, 'strAnswer': 'Data not found', 'data':jsnRow}
		#print("objResult::",jsnRow)
		return {'data':jsnRow}
	except Exception as exception:
		print('fnGetUserInfo: ', exception)
		return {'intResponse': 500, 'strAnswer': exception.args[1]}


def fnCreateUpdateStep(workShopId, teamId, step):
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	params = (workShopId, teamId,step)
	#print('params fnCreateUpdateStep',params)
	cursor.callproc("sp_UpdateSimpleb_step",params)
	params = (workShopId)
	cursor.callproc("sp_getFacilitTeamIdByWorkshopId", [params])
	jsonFacilitator = cursor.fetchone()
	MysqlCnx.commit()
	#print("ACTUALIZADA pasos")
	return ({'intResponse': 200, 'strAnswer': 'update status successfully', 'facilitatorTeamId': jsonFacilitator['TeamId']})


def fnUpdateMonthBalance(workShopId, teamId, month):
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	params = (workShopId, teamId, month)
	#print('params fnCreateUpdateStep',params)
	cursor.callproc("sp_UpdateStandardBalanceMonth",params)
	MysqlCnx.commit()
	#print("ACTUALIZADA pasos")
	return ({'intResponse': 200, 'strAnswer': 'update status successfully'})

def fnCreateRecord(WokshopId, teamId):
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	params = (WokshopId, teamId)
	#print('params fnCreateRecord',params)
	cursor.callproc("sp_InsertRecordSimplebalancesheet",params)
	MysqlCnx.commit()
	#print("ACTUALIZADA pasos")
	return ({'intResponse': 200, 'strAnswer': 'update status successfully'})	

def fnGetLabelsBalance(languagesId):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (languagesId)
		cursor.callproc("sp_getLabelsBalance",[params])
		MysqlCnx.commit()
		jsnRow = cursor.fetchall()
		if jsnRow == None:
			return {'intResponse': 404, 'strAnswer': 'User not found'}
		#print("objResult::",jsnRow)
		return {'data':jsnRow}
	except Exception as exception:
		print('fnGetLabelsBalance: ', exception)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}

def fnGetCountBoardBalance(teamId):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId)
		cursor.callproc("sp_getCountBoardBalance",[params])
		MysqlCnx.commit()
		jsnRow = cursor.fetchall()
		if jsnRow == None:
			return {'intResponse': 404, 'strAnswer': 'User not found'}
		for row in jsnRow:
			row['cantidad'] = int(row['cantidad'])
		#print("objResult::",jsnRow)
		return {'data':jsnRow}
	except Exception as exception:
		print('fnGetCountBoardBalance: ', exception)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}

def fnUpdateQuantitiesbalance(WokshopId, teamId, month, cash,receivables,finishGood,workProcess,rawMaterials,totalCurrent1,machine,land,totalFixed,totalCurrent2,payables,loans,taxes,totalLiabilities,capital,retained,totalShareholder,totalLiabilitiesAndEquity):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (WokshopId, teamId, month, cash,receivables,finishGood,workProcess,rawMaterials,totalCurrent1,machine,land,totalFixed,totalCurrent2,payables,loans,taxes,totalLiabilities,capital,retained,totalShareholder,totalLiabilitiesAndEquity)
		print('params fnUpdateRecord',params)
		cursor.callproc("sp_UpdateCountBoardBalanceSheet",params)
		MysqlCnx.commit()
		print("ACTUALIZADA fnUpdateRecord")
		return ({'intResponse': 200, 'strAnswer': 'fnUpdateQuantitiesIncome'})	
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args})	


def fnCreateQuantitiesbalanceCicle(WokshopId, teamId, month):
	try:
		for x in range(1, month+1):
			print("month",x ,month)
			fnCreateQuantitiesbalance(WokshopId, teamId, x)
		return ResponseMessages.sus200
	except Exception as exception:
		print("fnupdateClient", exception)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})


def fnCreateQuantitiesbalance(WokshopId, teamId, month):
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	params = (WokshopId, teamId, month)
	print('params fnCreateRecord',params)
	cursor.callproc("sp_InsertQuantitiesBalanceSheet",params)
	MysqlCnx.commit()
	print("ACTUALIZADA fnCreateQuantitiesIncome")
	return ({'intResponse': 200, 'strAnswer': 'update status successfully'})		


def fnGetQuantitiesbalance(teamId):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId)
		cursor.callproc("sp_getQuantitiesBalance",[params])
		MysqlCnx.commit()
		jsnRow = cursor.fetchall()
		if jsnRow == None:
			return {'intResponse': 404, 'strAnswer': 'User not found'}
		#print("objResult:",jsnRow)
		return {'data':jsnRow}
	except Exception as exception:
		print('fnGetLabelsIncom: ', exception)
		return ({'intResponse': 203, 'strAnswer': exception.args})


def fnGetQuantitiesbalancebyMonth(workshopId, month):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (workshopId, month)
		cursor.callproc("sp_getQuantitiesBalancebyMonth",params)
		MysqlCnx.commit()
		jsnRow = cursor.fetchall()
		if jsnRow == None:
			return {'intResponse': 404, 'strAnswer': 'User not found'}
		#print("objResult:",jsnRow)
		return {'data':jsnRow}
	except Exception as exception:
		print('fnGetLabelsIncom: ', exception)
		return ({'intResponse': 203, 'strAnswer': exception.args})

def fngetBidsbyMonth(workshopId, month):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (workshopId, month)
		cursor.callproc("sp_getBidsofTeamsbymontandWorkshop",params)
		MysqlCnx.commit()
		jsnRow = cursor.fetchall()
		if jsnRow == None:
			return {'intResponse': 404, 'strAnswer': 'User not found'}
		#print("objResult:",jsnRow)
		return {'data':jsnRow}
	except Exception as exception:
		print('fnGetLabelsIncom: ', exception)
		return ({'intResponse': 203, 'strAnswer': exception.args})



def fnGetQuantitiesAllTeamsBalance(workshopId, month):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (workshopId, month)
		cursor.callproc("sp_getAllTeamsBalancesheetQuantities",params)
		jsonRows = cursor.fetchall()
		if jsonRows == None:
			return {'intResponse': 404, 'strAnswer': 'quanities not found'}
		return ({'intResponse': 200, 'strAnswer': 'get succsesfully balancesheet quantities', 'info': jsonRows})	
	except Exception as exception:
		print('fnGetLabelsIncom: ', exception)
		return ({'intResponse': 203, 'strAnswer': exception.args})

def fnUpdateInputBalance(WokshopId, teamId, month, quantitie, column):
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	params = (WokshopId, teamId, month, quantitie, column)
	cursor.callproc("sp_insertQuantitiesBalanceSheetTemp",params)
	MysqlCnx.commit()
	return ({'intResponse': 200, 'strAnswer': 'update input successfully'})


def fnGetQuantitiesBalanceTemp(teamId, month):
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	params = (teamId, month)
	cursor.callproc("sp_getQuantitiesBalanceSheetTemp",params)
	return ({'intResponse': 200, 'strAnswer': 'get income temporal successfully', 'data': cursor.fetchone()})
######################################################END BALANCE SHEET##################################################

#####################################################START Income Statement##################################################
'''****************************************************************************
   * Author: LJGF
   * Date: 20/05/2021
   * Summary: <Obtener los contacto de un cliente(Usuario)>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnDeleteMesBalanceIncome(teamId, cantidad):
	print("fnDeleteMesBalanceIncome datos", teamId, cantidad)
	try:
		for x in range(1, cantidad+1):
			print("cantidad de meses delete",teamId, x)
			fnDeleteMesxMesBalanceIncome(teamId)
		return ResponseMessages.sus200
	except Exception as exception:
		print("fnDeleteMesBalanceIncomeError", exception)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

def fnDeleteMesxMesBalanceIncome(teamId):
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	params = (teamId)
	cursor.callproc("sp_DeleteQuantitiesIncome",[params])
	MysqlCnx.commit()
	return ResponseMessages.sus200

def fnGetCountRegistrosIncome(teamId):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId)
		cursor.callproc("sp_GetCountQuantitiesIncome",[params])
		MysqlCnx.commit()
		jsnRow = cursor.fetchone()
		if jsnRow == None:
			return {'intResponse': 404, 'data':jsnRow}
		print("objResult::",jsnRow)
		return {'data':jsnRow}
	except Exception as exception:
		print('fnGetUserInfo: ', exception)
		return {'intResponse': 500, 'strAnswer': exception.args[1]}


def fnGetLabelsIncom(languagesId):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (languagesId)
		cursor.callproc("sp_getLabelsIncomeStatement",[params])
		MysqlCnx.commit()
		jsnRow = cursor.fetchall()
		if jsnRow == None:
			return {'intResponse': 404, 'strAnswer': 'User not found'}
		print("objResult::",jsnRow)
		return {'data':jsnRow}
	except Exception as exception:
		print('fnGetLabelsIncom: ', exception)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}


def fnUpdateMonthIncomestatement(workShopId, teamId, month):
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	params = (workShopId, teamId, month)
	print('params fnCreateUpdateStep',params)
	cursor.callproc("sp_UpdateIncomeMonth",params)
	MysqlCnx.commit()
	print("ACTUALIZADA pasos")
	return ({'intResponse': 200, 'strAnswer': 'update status successfully'})

def fnGetCountBoard(teamId):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId)
		cursor.callproc("sp_getCountBoardIncomeStatement",[params])
		MysqlCnx.commit()
		jsnRow = cursor.fetchall()
		if jsnRow == None:
			return {'intResponse': 404, 'strAnswer': 'User not found'}
		print("objResult::",jsnRow)
		for row in jsnRow:
			row['cantidad'] = int(row['cantidad'])
		return {'data':jsnRow}
	except Exception as exception:
		print('fnGetCountBoard: ', exception)
		return {'intResponse': 500, 'strAnswer': 'Error en el servidor'}


def fnUpdateQuantitiesIncome(WokshopId, teamId, month, total, costGood, contribution, factory, gross, selling, operating, interest, income, taxes, netIncome):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (WokshopId, teamId, month, total, costGood, contribution, factory, gross, selling, operating, interest, income, taxes, netIncome)
		print('params fnUpdateRecord',params)
		cursor.callproc("sp_UpdateCountBoardIncome",params)
		MysqlCnx.commit()
		print("ACTUALIZADA fnUpdateRecord")
		return ({'intResponse': 200, 'strAnswer': 'fnUpdateQuantitiesIncome'})	
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args})	

def fnGetQuantitiesAllTeamsIncomestatement(WokshopId, month):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (WokshopId, month)
		print('params fnUpdateRecord',params)
		cursor.callproc("sp_getAllTeamsIncomestatementQuantities",params)
		jsonRows = cursor.fetchall()
		return ({'intResponse': 200, 'strAnswer': 'get succsesfully incomestatement quantities', 'info': jsonRows})	
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args})	


def fnCreateQuantitiesIncomeCicle(WokshopId, teamId, month):
	try:
		for x in range(1, month+1):
			print("month",x ,month)
			fnCreateQuantitiesIncome(WokshopId, teamId, x)
		return ResponseMessages.sus200
	except Exception as exception:
		print("fnupdateClient", exception)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})



def fnCreateQuantitiesIncome(WokshopId, teamId, month):
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	params = (WokshopId, teamId, month)
	print('params fnCreateRecord',params)
	cursor.callproc("sp_InsertQuantitiesIncome",params)
	MysqlCnx.commit()
	print("ACTUALIZADA fnCreateQuantitiesIncome")
	return ({'intResponse': 200, 'strAnswer': 'update status successfully'})		


def getQuantitiesbyMonth(workshop, month):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (workshop, month)
		cursor.callproc("sp_getQuantitiesIncomebyMonth",params)
		MysqlCnx.commit()
		jsnRow = cursor.fetchall()
		if jsnRow == None:
			return {'intResponse': 404, 'strAnswer': 'User not found'}
		print("objResult:",jsnRow)
		return {'data':jsnRow}
	except Exception as exception:
		print('fnGetLabelsIncom: ', exception)
		return ({'intResponse': 203, 'strAnswer': exception.args})

def fnGetQuantitiesIncome(teamId):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId)
		cursor.callproc("sp_getQuantitiesIncome",[params])
		MysqlCnx.commit()
		jsnRow = cursor.fetchall()
		if jsnRow == None:
			return {'intResponse': 404, 'strAnswer': 'User not found'}
		print("objResult:",jsnRow)
		return {'data':jsnRow}
	except Exception as exception:
		print('fnGetLabelsIncom: ', exception)
		return ({'intResponse': 203, 'strAnswer': exception.args})

def fnUpdateInputIncome(WokshopId, teamId, month, quantitie, column):
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	params = (WokshopId, teamId, month, quantitie, column)
	cursor.callproc("sp_insertQuantitiesIncomeTemp",params)
	MysqlCnx.commit()
	return ({'intResponse': 200, 'strAnswer': 'update input successfully'})


def fnGetQuantitiesIncomeTemp(teamId, month):
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	params = (teamId, month)
	cursor.callproc("sp_getQuantitiesIncomeTemp",params)
	return ({'intResponse': 200, 'strAnswer': 'get income temporal successfully', 'data': cursor.fetchone()})

######################################################END Income Statement####################################################


###################################################START BOARD and sockets###############################################

'''****************************************************************************
   * Author: AJLL
   * Date: 06/05/2021
   * Summary: <Obtener las fichas iniciales del board de un team>
   ****************************************************************************'''

def fnGetInitBoard(teamId):
	try:
		print("TeamID1",teamId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId)
		cursor.callproc("sp_getBoardByTeamId", [params])
		jsonRows = cursor.fetchall()
		for piece in jsonRows:
			if(piece['AreaDrag'] == 15 or piece['AreaDrag'] == 16 or piece['AreaDrag'] == 17 or piece['AreaDrag'] == 30):
				params = (piece['StatusBoardId'], teamId)
				cursor.callproc("sp_getOrderByPieceId", params)
				order = cursor.fetchone()
				if(order != None):
					piece['order'] = order
					strTerms =""
					if(order['Terms'] == 0):
						strTerms = " (Cash)"
					else:
						strTerms = " ("+str(order['Terms'])+" days)"

					piece['strDescription'] = str(order['OrderNum']) + ": " + str(order['Quantity']) + " Royals for " + str(order['bid'])+strTerms
			elif (piece['AreaDrag'] == 12 or piece['AreaDrag'] == 13 or piece['AreaDrag'] == 14):
				params = (piece['StatusBoardId'])
				cursor.callproc("sp_getInfPieceLoan", [params])
				info = cursor.fetchone()
				if(info != None):
					piece['infoLoan'] = info
					piece['strDescription'] = 'Bank Loan: 20, Month: ' + str(info['Month'])			
		return {'intResponse': 200, 'board': jsonRows}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
   * Author: AJLL
   * Date: 06/05/2021
   * Summary: <Obtener las fichas iniciales de los boards de todos los teams de un workshop>
   ****************************************************************************'''

def fnGetTeamsBoardByWorkshopId(workshopId):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (workshopId)
		cursor.callproc("sp_getAllTeamsByWorkShopId", [params])
		jsonTeams = cursor.fetchall()
		for team in jsonTeams:
			params = (team['TeamId'])
			cursor.callproc("sp_getBoardByTeamId", [params])
			jsonRows = cursor.fetchall()
			team['board'] = jsonRows;	
			params = (team['TeamId'])
			cursor.callproc("sp_getCheckListByTeamId", [params])
			jsonRows = cursor.fetchall()
			team['checkList'] = jsonRows;	
		return {'intResponse': 200, 'board': jsonTeams}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
   * Author: AJLL
   * Date: 06/05/2021
   * Summary: <Obtener el checklist del board de un team>
   ****************************************************************************'''

def fnGetCheckListByTeamId(teamId):
	try:
		print("TeamID1",teamId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId)
		cursor.callproc("sp_getCheckListByTeamId", [params])
		jsonRows = cursor.fetchall()
		# print("Fichas: ",jsonRows)
		return {'intResponse': 200, 'response': jsonRows}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
  * Author: AJLL
  * Date: 06/05/2021
  * Summary: <setear la variable que nos ayuda a las acciones del board>
****************************************************************************'''

def fnsetBlnControlModeOpen(idBln, value, teamId):
	try:
		print("TeamID1",teamId)
		print("checkList",idBln, value)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		if(value == 1):
			params = (teamId, idBln, value)
			cursor.callproc("sp_createActionBoard", params)
			jsonRows = cursor.fetchall()
			MysqlCnx.commit()
			return {'intResponse': 200, 'response': jsonRows}
		else:
			params = (idBln, teamId)
			cursor.callproc("sp_deleteActionBoard", params)
			MysqlCnx.commit()
			return {'intResponse': 200}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

def fnsetBlnControlModeOpenArray(idBlns, value, teamId):
	try:
		print("TeamID1",teamId)
		print("checkList",idBlns, value)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		for idBln in idBlns:
			if(value == 1):
				params = (teamId, idBln, value)
				cursor.callproc("sp_createActionBoard", params)
				jsonRows = cursor.fetchall()
				MysqlCnx.commit()
				idBln['response'] = jsonRows
				# return {'intResponse': 200, 'response': jsonRows}
			else:
				params = (idBln, teamId)
				cursor.callproc("sp_deleteActionBoard", params)
				MysqlCnx.commit()
				# return {'intResponse': 200}
			return {'intResponse': 200}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
  * Author: AJLL
  * Date: 06/05/2021
  * Summary: <obtener las variables que nos ayuda a las acciones del board>
****************************************************************************'''

def fngetActionsBoardByTeamId(teamId):
	try:
		print("TeamID1",teamId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId)
		cursor.callproc("sp_getActionsBoardByTeamId", [params])
		jsonRows = cursor.fetchall()
		return {'intResponse': 200, 'response': jsonRows}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
  * Author: AJLL
  * Date: 06/05/2021
  * Summary: <Actualizar el checklist del board de un team>
****************************************************************************'''

def fnUpdateCheckList(checkList, teamId):
	try:
		print("TeamID1",teamId)
		print("checkList",checkList)
		list = json.loads(checkList)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		for check in list:
			print(check)
			print(check['blnCheck'])
			valor = check['blnCheck']
			params = (check['idBd'], valor)
			cursor.callproc("sp_updateCheckListByCheckListId", params)
		jsonRows = cursor.fetchall()
		MysqlCnx.commit()
		
		return {'intResponse': 200, 'response': jsonRows}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

def fnUpdateCheckListByFacilitatorInfo(checkList):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		for check in checkList:
			valor = check['valor']
			params = (check['CheckListId'], valor)
			cursor.callproc("sp_updateCheckListByCheckListId", params)
		jsonRows = cursor.fetchall()
		MysqlCnx.commit()
		
		return {'intResponse': 200, 'response': jsonRows}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
  * Author: AJLL
  * Date: 06/05/2021
  * Summary: <limpiar el checklist del board de un team>
****************************************************************************'''

def fnClearCheckList(teamId):
	try:
		print("TeamID1",teamId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId)
		cursor.callproc("sp_clearCheckListByTeamId", [params])
		MysqlCnx.commit()
		
		return {'intResponse': 200, 'response': 'clear checklist successfully'}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})


'''****************************************************************************
   * Author: DCM
   * Date: 20/05/2021
   * Summary: <Validar si un usuario facilitador envia su password correctamente>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnisvalidFacilitator(idUser, strPassword):
	md5 = hashlib.md5()
	aux = bytes(strPassword, encoding='utf-8')
	md5.update(aux)
	pswEncriptada =  md5.hexdigest()
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	params = (idUser,pswEncriptada)
	cursor.callproc("sp_validateFacilitatorToBoard",params) 
	MysqlCnx.commit()
	jsnRow = cursor.fetchone()
	print("jsrow respuesta facilitatorID::",jsnRow)
	return {'intResponse': '200', 'UserID':jsnRow['varExistUsuario']}
	


'''****************************************************************************
   * Author: AJLL
   * Date: 06/05/2021
   * Summary: <actualizar el mes del board jugado por 1 equipo>
   ****************************************************************************'''

def fnUpdateMonth(teamId, month, status):
	try:
		print("TeamID1",teamId, "mes", month)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId, month)
		cursor.callproc("sp_setMonthByTeamId", params)
		params = (teamId, status)
		cursor.callproc("sp_updateStatusByTeamId", params)
		MysqlCnx.commit()
		responseClearCheck = fnClearCheckList(teamId)
		print(responseClearCheck)
		# print("Fichas: ",jsonRows)
		return {'intResponse': 200, 'strAnswer': 'month update succsessfully'}
	except Exception as exception:
		print("exception fnUpdateMonth::",exception.args)
		return ({'intResponse': 203, 'strAnswer': exception.args})


'''****************************************************************************
   * Author: AJLL
   * Date: 06/05/2021
   * Summary: <obtener las bids de un equipo>
   ****************************************************************************'''

def getOrdersByTeamId(teamId, month):
	try:
		# print("TeamID1",teamId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId, month)
		cursor.callproc("sp_getOrdersByIdTeam", params)
		jsonRows = cursor.fetchall()
		for bid in jsonRows:
			responseOrder = getOrderId(bid['OrderId'])
			if(responseOrder['intResponse']):
				bid['OrderNum'] = responseOrder['order']['OrderNum']
			else:
				bid['OrderNum'] = None
		# print("ORDERS: ",jsonRows)
		return {'intResponse': 200, 'strAnswer': 'get orders succsessfully', 'orders': jsonRows}
	except Exception as exception:
		print("exception fnUpdateMonth::",exception.args)
		return ({'intResponse': 203, 'strAnswer': exception.args})

'''****************************************************************************
   * Author: AJLL
   * Date: 06/05/2021
   * Summary: <obtener las acciones que nos ayudan al board>
   ****************************************************************************'''

def fnGetActionsBoard(teamId):
	try:
		print("TeamID1",teamId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId)
		cursor.callproc("sp_getActionsBoardByTeamId", [params])
		jsonRows = cursor.fetchall()
		for bid in jsonRows:
			responseOrder = getOrderId(bid['OrderId'])
			if(responseOrder['intResponse']):
				bid['OrderNum'] = responseOrder['order']['OrderNum']
			else:
				bid['OrderNum'] = None
		print("ORDERS: ",jsonRows)
		return {'intResponse': 200, 'strAnswer': 'get orders succsessfully', 'orders': jsonRows}
	except Exception as exception:
		print("exception fnUpdateMonth::",exception.args)
		return ({'intResponse': 203, 'strAnswer': exception.args})

'''****************************************************************************
   * Author: AJLL
   * Date: 06/05/2021
   * Summary: <deliver orden>
   ****************************************************************************'''

def fnDeliverOrderById(orderId):
	try:
		print("orderId",orderId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (orderId)
		cursor.callproc("sp_deliverOrderById", [params])
		MysqlCnx.commit()
		return {'intResponse': 200, 'strAnswer': 'get orders succsessfully'}
	except Exception as exception:
		print("exception fnDeliverOrderById::",exception.args)
		return ({'intResponse': 203, 'strAnswer': exception.args})


'''****************************************************************************
   * Author: BPR
   * Date: 08/06/2021
   * Summary: <obtener order by Id>
   ****************************************************************************'''

def getOrderId(orderId):
	try:
		print("getOrderId",orderId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (orderId)
		cursor.callproc("sp_getOrderById", [params])
		jsonOrder = cursor.fetchone()
		print("jsonOrder: ",jsonOrder)
		return {'intResponse': 200, 'strAnswer': 'get orders succsessfully', 'order': jsonOrder}
	except Exception as exception:
		print("exception getOrderId:",exception.args)
		return ({'intResponse': 203, 'strAnswer': exception.args})

'''****************************************************************************
   * Author: AJLL
   * Date: 06/05/2021
   * Summary: <actualizar el mes del board jugado por 1 equipo>
   ****************************************************************************'''

def fnUpdateBoardMode(teamId, mode):
	try:
		print("TeamID1",teamId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId, mode)
		cursor.callproc("sp_setBoardModeByTeamId", params)
		MysqlCnx.commit()
		# print("Fichas: ",jsonRows)
		return {'intResponse': 200, 'strAnswer': 'board mode update succsessfully'}
	except Exception as exception:
		print("exception fnUpdateBoardMode::",exception.args)
		return ({'intResponse': 203, 'strAnswer': exception.args})

'''****************************************************************************
   * Author: AJLL
   * Date: 06/05/2021
   * Summary: <actualizar checklist del board de 1 equipo>
   ****************************************************************************'''

def fnCreateUpdCheckList(teamId, checkList):
	try:
		print("TeamID1",teamId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId)
		cursor.callproc("sp_deleteChecklistByTeamId", [params])
		MysqlCnx.commit()

		for checkBox in checkList:
			params = (teamId, checkBox['id'], checkBox['title'])
			cursor.callproc("sp_createCheckBox", params)
			jsonRow = cursor.fetchone()
			MysqlCnx.commit()
			checkBox['idBd'] = jsonRow['id']
		# print("Fichas: ",jsonRows)
		return {'intResponse': 200, 'strAnswer': 'checkBox update succsessfully', 'checkList': checkList}
	except Exception as exception:
		print("exception fnUpdateBoardMode::",exception.args)
		return ({'intResponse': 203, 'strAnswer': exception.args})

'''****************************************************************************
   * Author: AJLL
   * Date: 06/05/2021
   * Summary: <obtener el improvement del board de 1 equipo>
   ****************************************************************************'''

def fnGetImprovements(teamId):
	try:
		print("TeamID1",teamId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId)
		cursor.callproc("sp_getImprovementsByTeamId", [params])
		jsonRow = cursor.fetchall()
		return {'intResponse': 200, 'improvements': jsonRow}
	except Exception as exception:
		print("exception fnUpdateBoardMode::",exception.args)
		return ({'intResponse': 203, 'strAnswer': exception.args})

'''****************************************************************************
   * Author: AJLL
   * Date: 06/05/2021
   * Summary: <actualizar el board y el mes a un equipo>
   ****************************************************************************'''

def fnUpdateMonthBoard(teamId, month):
	try:
		print("TeamID1",teamId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId, month)
		cursor.callproc("sp_updateMonthByTeamId", params)
		MysqlCnx.commit()
		return {'intResponse': 200, 'strResponse': 'Update month and board succesfully'}
	except Exception as exception:
		print("exception fnUpdateBoardMode::",exception.args)
		return ({'intResponse': 203, 'strAnswer': exception.args})

	
'''****************************************************************************
   * Author: AJLL
   * Date: 06/05/2021
   * Summary: <actualizar el numero de royals al final del mes de un equipo>
   ****************************************************************************'''

def fnUpdateHistoryRoyal(workshop, teamId, numberRoyal, month):
	try:
		print("TeamID1",teamId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (workshop, teamId, numberRoyal, month)
		cursor.callproc("sp_updateHistoryRoyal", params)
		MysqlCnx.commit()
		return {'intResponse': 200, 'strResponse': 'Update history succesfully', 'history': cursor.fetchone()}
	except Exception as exception:
		print("exception fnUpdateBoardMode::",exception.args)
		return ({'intResponse': 203, 'strAnswer': exception.args})

'''****************************************************************************
   * Author: AJLL
   * Date: 06/05/2021
   * Summary: <controlar la bandera de lock target column>
   ****************************************************************************'''

def fnUpdateBudgetLockStatus(workshop, status):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (workshop, status)
		cursor.callproc("sp_updateBudgetLockStatus", params)
		MysqlCnx.commit()
		return {'intResponse': 200, 'strResponse': 'Update Budget Lock status succesffully', 'status': status}
	except Exception as exception:
		print("exception fnUpdateBoardMode::",exception.args)
		return ({'intResponse': 203, 'strAnswer': exception.args})

'''****************************************************************************
   * Author: AJLL
   * Date: 06/05/2021
   * Summary: <adelantar el board con magic button hasta el paso antes del mercado en el mes 1>
   ****************************************************************************'''

def fnGoToMarketMonth1(teamId, workshopId):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId, workshopId)
		cursor.callproc("sp_setBoardBeforeMarket", params)
		MysqlCnx.commit()
		return {'intResponse': 200, 'strResponse': 'Update board succesffully'}
	except Exception as exception:
		print("exception fnGoToMarketMonth1::",exception.args)
		return ({'intResponse': 203, 'strAnswer': exception.args})

'''****************************************************************************
   * Author: AJLL
   * Date: 06/05/2021
   * Summary: <adelantar el board con magic button hasta el mes principio del mes 2>
   ****************************************************************************'''

def fnGoToFinishMonth1(teamId, workshopId):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId,workshopId)
		cursor.callproc("sp_setBoardFinishMonth",params)
		MysqlCnx.commit()
		return {'intResponse': 200, 'strResponse': 'Update board succesffully'}
	except Exception as exception:
		print("exception fnUpdateBoardMode::",exception.args)
		return ({'intResponse': 203, 'strAnswer': exception.args})

'''****************************************************************************
   * Author: AJLL
   * Date: 06/05/2021
   * Summary: <inserta los datos de cada uno de los atributos en la tabla budgetsavequantities>
   ****************************************************************************'''

def fnUpdateBudgetTargetColumn(teamId, priceRoyal, numRoyals, totalSales, costRoyal, totalCOGS, contribution, factoryOverhead,
            SGA, Finance, totalFiexed, netIncome):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId, priceRoyal, numRoyals, totalSales, costRoyal, totalCOGS, contribution, factoryOverhead,
            SGA, Finance, totalFiexed, netIncome)
		cursor.callproc("sp_updateSaveQuantitiesBudgetByTeamId", params)
		MysqlCnx.commit()
		return {'intResponse': 200, 'strResponse': 'Update Budget target column values succesffully'}
	except Exception as exception:
		print("exception fnUpdateBoardMode::",exception.args)
		return ({'intResponse': 203, 'strAnswer': exception.args})

	
'''****************************************************************************
   * Author: AJLL
   * Date: 06/05/2021
   * Summary: <obterer los datos de la tabla budgetsavequantities>
   ****************************************************************************'''

def fnGetBudgetTargetColumn(teamId):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId)
		cursor.callproc("sp_getSaveQuantitiesBudgetByTeamId", [params])
		return {'intResponse': 200, 'strResponse': 'Update Budget target column values succesffully', 'data': cursor.fetchone()}
	except Exception as exception:
		print("exception fnUpdateBoardMode::",exception.args)
		return ({'intResponse': 203, 'strAnswer': exception.args})


'''****************************************************************************
   * Author: AJLL
   * Date: 06/05/2021
   * Summary: <obtener de todos los equipos la cantidad de royal del mes anterior>
   ****************************************************************************'''

def fnGetHistoryRoyals(workshop):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (workshop)
		cursor.callproc("sp_getHistoryRoyalByWorkshopId", [params])
		return {'intResponse': 200, 'lstHistory': cursor.fetchall()}
	except Exception as exception:
		print("exception fnUpdateBoardMode::",exception.args)
		return ({'intResponse': 203, 'strAnswer': exception.args})

'''****************************************************************************
   * Author: AJLL
   * Date: 06/05/2021
   * Summary: <asignar a 0 el approved improvement de todos los equipos>
   ****************************************************************************'''

def fnSetAllTeamsUnapprovedImprovement(workshopId):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (workshopId)
		cursor.callproc("sp_setAllTeamsUnapprovedImprovement", [params])
		MysqlCnx.commit()
		return {'intResponse': 200, 'strResponse': 'Update approved succesfully'}
	except Exception as exception:
		print("exception fnUpdateBoardMode::",exception.args)
		return ({'intResponse': 203, 'strAnswer': exception.args})
'''****************************************************************************
   * Author: AJLL
   * Date: 06/05/2021
   * Summary: <obtener informacion de un team>
   ****************************************************************************'''

def fnGetTeamById(teamId):
	try:
		print("TeamID2",teamId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId)
		cursor.callproc("sp_getTeamByID", [params])
		jsonRows = cursor.fetchone()
		# print("Fichas: ",jsonRows)
		return {'intResponse': 200, 'team': jsonRows}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
   * Author: AJLL
   * Date: 06/05/2021
   * Summary: <actualizar bd asignando la ficha al area que se solto>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnUpdatePiece(idPiece, areaDrop, tipo, valor):
	try:

		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		print("actualiando piezaaaaaaaaaaaaaa",idPiece, "areaDrop", areaDrop, 'tipo',tipo)

		if areaDrop == 1001 or areaDrop == 1002 or areaDrop == 1003:
			print("BORRANDO MONEDA")
			params = (idPiece)
			cursor.callproc("sp_deletePieceById", [params])
			MysqlCnx.commit()
			return ({'intResponse': 200, 'strAnswer': 'delete piece successfully'})
		
		params = (idPiece, areaDrop, tipo, valor)
		cursor.callproc("sp_updPieceByID", params)
		MysqlCnx.commit()
		print("ACTUALIZADA PIECE")
		return ({'intResponse': 200, 'strAnswer': 'update piece successfully'})
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

def fnUpdateTeamStatus(teamId, status):
	try:
		print("teamId",teamId, "status", status)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId, status)
		cursor.callproc("sp_updateStatusByTeamId", params)
		MysqlCnx.commit()
		print("ACTUALIZADA STATUS")
		return ({'intResponse': 200, 'strAnswer': 'update status successfully'})
	except Exception as exception:
		print("excepcion update team status", exception.args)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

def fnGetFacilitatorIdTeamByTeamId(teamId):
	try:
		print("workshopId",teamId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId)
		cursor.callproc("sp_getFacilitTeamIdByTeamId", [params])
		jsonRow = cursor.fetchone()
		return ({'intResponse': 200, 'strAnswer': 'update status successfully', 'teamId':jsonRow} )
	except Exception as exception:
		print("excepcion update team status", exception.args)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

def fnSplitCoin(teamId, newList ,idAreaDrag):
	try:
		print("split coiiiin___________________________________")
		print("teamId",teamId, "newList", newList)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId, idAreaDrag)
		cursor.callproc("sp_deletePiecesByTeamIdAreaId", params)
		MysqlCnx.commit()
		
		jsonReponse = {
			'cdkLstAdministration': {'idPiece': -1},
			'cdkLstChangeI': {'idPiece': -1},
			'cdkLstMarketingS': {'idPiece': -1},
			'cdkLstAdminOver': {'idPiece': -1}
		}

		if idAreaDrag == 1004:
			print("vamos a pagar a los acumaaaaaaan")
			params = (teamId, 25, 1, 1)
			cursor.callproc("sp_createPiece", params)
			jsonRow = cursor.fetchone()
			print(jsonRow)
			jsonReponse['cdkLstAdministration']['idPiece'] = jsonRow['idPiece']
			MysqlCnx.commit()
			params = (teamId, 26, 1, 1)
			cursor.callproc("sp_createPiece", params)
			jsonRow = cursor.fetchone()
			print(jsonRow)
			jsonReponse['cdkLstChangeI']['idPiece'] = jsonRow['idPiece']
			MysqlCnx.commit()
			params = (teamId, 22, 1, 1)
			cursor.callproc("sp_createPiece", params)
			jsonRow = cursor.fetchone()
			print(jsonRow)
			jsonReponse['cdkLstMarketingS']['idPiece'] = jsonRow['idPiece']
			MysqlCnx.commit()
			params = (teamId, 23, 1, 1)
			cursor.callproc("sp_createPiece", params)
			jsonRow = cursor.fetchone()
			print(jsonRow)
			jsonReponse['cdkLstAdminOver']['idPiece'] = jsonRow['idPiece']
			MysqlCnx.commit()
			return ({'intResponse': 200, 'strAnswer': 'pay acuman succssesfully', 'idPieces': jsonReponse})
		elif idAreaDrag == 5 or idAreaDrag == 6:
			print("vamos a juntar materials")
			for piece in newList:
				params = (teamId, idAreaDrag, piece['valor'], piece['type'])
				cursor.callproc("sp_createPiece", params)
				jsonRow = cursor.fetchone()
				print(jsonRow)
				piece['id'] = jsonRow['idPiece']
				MysqlCnx.commit()
			print("ACTUALIZADA lista cash separacion piezas", newList)
			return ({'intResponse': 200, 'strAnswer': 'update lista cash successfully', 'newList': newList})
		elif idAreaDrag == 11 or idAreaDrag == 9 or idAreaDrag == 49:
			print("vamos a juntar royals")
			for piece in newList:
				params = (teamId, idAreaDrag, piece['valor'], piece['type'])
				cursor.callproc("sp_createPiece", params)
				jsonRow = cursor.fetchone()
				print(jsonRow)
				piece['id'] = jsonRow['idPiece']
				MysqlCnx.commit()
			print("ACTUALIZADA lista cash separacion piezas", newList)
			return ({'intResponse': 200, 'strAnswer': 'update lista cash successfully', 'newList': newList})
		
		if idAreaDrag == 3 or idAreaDrag == 4:
			for piece in newList:
				params = (teamId, idAreaDrag, piece['valor'], piece['type'])
				cursor.callproc("sp_createPiece", params)
				jsonRow = cursor.fetchone()
				print(jsonRow)
				piece['id'] = jsonRow['idPiece']
				MysqlCnx.commit()
			return ({'intResponse': 200, 'strAnswer': 'update lista cash successfully', 'newList': newList})

		if(idAreaDrag == 7 or idAreaDrag == 47 or idAreaDrag == 31):
			for piece in newList:
				params = (teamId, idAreaDrag, piece['valor'], piece['type'])
				cursor.callproc("sp_createPiece", params)
				jsonRow = cursor.fetchone()
				print(jsonRow)
				piece['id'] = jsonRow['idPiece']
				MysqlCnx.commit()
			return ({'intResponse': 200, 'strAnswer': 'update lista cash successfully', 'newList': newList})

		tipo = 1 if(idAreaDrag == 30 or idAreaDrag == 24 or idAreaDrag == 15 or idAreaDrag == 16 or idAreaDrag == 17) else  2 if(idAreaDrag == 19 or idAreaDrag == 35) else 0
		for piece in newList:
			params = (teamId, idAreaDrag, piece['valor'], tipo)
			cursor.callproc("sp_createPiece", params)
			jsonRow = cursor.fetchone()
			print(jsonRow)
			piece['id'] = jsonRow['idPiece']
			MysqlCnx.commit()
		print("ACTUALIZADA lista cash separacion piezas")
		return ({'intResponse': 200, 'strAnswer': 'update lista cash successfully', 'newList': newList})
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

def fnSetListOrder(teamId,newList, areaDragContainer, areaDragPreviousContainer, orderId):
	try:
		if(areaDragPreviousContainer == 31):
			MysqlCnx = getConectionMYSQL()
			cursor = MysqlCnx.cursor()
			params = (teamId, areaDragContainer)
			# cursor.callproc("sp_deletePiecesByTeamIdAreaId", params)
			MysqlCnx.commit()
			params = (orderId)
			# cursor.callproc("sp_getOrderById", [params])
			# order = cursor.fetchone()
			for piece in newList:
				params = (teamId, areaDragContainer, piece['valor'], 1, orderId)
				piece['tipo'] = 1
				piece['type'] = 1
				cursor.callproc("sp_createPieceOfOrder", params)
				jsonRow = cursor.fetchone()
				print(jsonRow)
				piece['id'] = jsonRow['idPiece']
				params = (piece['id'], teamId)
				cursor.callproc("sp_getOrderByPieceId", params)
				order = cursor.fetchone()
				piece['order'] = order
				strTerms =""
				if(order != None):
					if(order['Terms'] == 0):
						strTerms = " (Cash)"
					else:
						strTerms = " ("+str(order['Terms'])+" days)"

					piece['strDescription'] = str(order['OrderNum']) + ": " + str(order['Quantity']) + " Royals for " + str(order['bid'])+strTerms
				MysqlCnx.commit()
			return ({'intResponse': 200, 'strAnswer': 'update lista cash successfully', 'newList': newList})
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

def fnSetList(teamId,newList, areaDragContainer, areaDragPreviousContainer, oldItem):
	try:

		if(areaDragPreviousContainer == 31):
			print("teamId",teamId, "newList", newList)
			print("vamos a liberar una ordeeeen")
			MysqlCnx = getConectionMYSQL()
			cursor = MysqlCnx.cursor()
			params = (teamId, areaDragContainer)
			cursor.callproc("sp_deletePiecesByTeamIdAreaId", params)
			MysqlCnx.commit()
			for piece in newList:
				params = (teamId, areaDragContainer, piece['valor'], 1)
				piece['tipo'] = 1
				piece['type'] = 1
				cursor.callproc("sp_createPiece", params)
				jsonRow = cursor.fetchone()
				print(jsonRow)
				piece['id'] = jsonRow['idPiece']
				MysqlCnx.commit()
			print("ACTUALIZADA lista cash separacion piezas", newList)
			return ({'intResponse': 200, 'strAnswer': 'update lista cash successfully', 'newList': newList})
		

		print("teamId",teamId, "newList", newList)
		print("areaDragContainer: ",areaDragContainer,"areaDragPreviousContainer:",areaDragPreviousContainer, "oldItem: ", oldItem)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (oldItem['id'])
		cursor.callproc("sp_deletePieceById", [params])
		MysqlCnx.commit()
		

		if areaDragContainer == 5 or areaDragContainer == 6:
			print("vamos a juntar materials")
			for piece in newList:
				params = (teamId, areaDragContainer, piece['valor'], 7)
				piece['tipo'] = 7
				cursor.callproc("sp_createPiece", params)
				jsonRow = cursor.fetchone()
				print(jsonRow)
				piece['id'] = jsonRow['idPiece']
				MysqlCnx.commit()
			print("ACTUALIZADA lista cash separacion piezas", newList)
			return ({'intResponse': 200, 'strAnswer': 'update lista cash successfully', 'newList': newList})

		return ({'intResponse': 666, 'strAnswer': 'no entro if ', 'newList': newList})
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

def fnBorrowFromBank(teamId, areaDragContainer, areaDragPreviousContainer, item, month, idBlns, values):
	try:
		print("teamId",teamId, "borrow From Bank")
		print("areaDragContainer: ",areaDragContainer,"areaDragPreviousContainer:",areaDragPreviousContainer, "oldItem: ", item, 'month',month)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (item['id'])
		cursor.callproc("sp_deletePieceById", [params])
		MysqlCnx.commit()
		
		params = (teamId, 30, 20, 1)
		cursor.callproc("sp_createPiece", params)
		jsonRow = cursor.fetchone()
		pieceCash = {
			'valor': 20,
          	'id': jsonRow['idPiece'],
          	'draggable': False,
          	'type': 1,

		}
		print(jsonRow)
		print("vamos a agregar 1 a bd")
		MysqlCnx.commit()
		
		
		print("vamos a agregar 2 a bd")
		params = (teamId, areaDragContainer, 20, 3, month)
		cursor.callproc("sp_createPieceOfBorrow", params)
		jsonRow = cursor.fetchone()
		print(jsonRow)
		pieceLoans = {
			'valor': 20,
          	'id': jsonRow['idPiece'],
          	'draggable': False,
          	'type': 3,
			'strDescription': 'Bank Loan: 20, Month: ' + str(month)

		}
		MysqlCnx.commit()
		# si es despues del mes 2 agragamos las actiones de control del board
		if month >= 2:
			for num, value in enumerate(values, start=0):
				if(value == 1):
					params = (teamId, idBlns[num], value)
					cursor.callproc("sp_createActionBoard", params)
					jsonRows = cursor.fetchall()
					MysqlCnx.commit()
					# return {'intResponse': 200, 'response': jsonRows}
				else:
					params = (idBlns[num], teamId)
					cursor.callproc("sp_deleteActionBoard", params)
					MysqlCnx.commit()
					# return {'intResponse': 200}
		print("ACTUALIZADA lista cash separacion piezas", pieceCash, pieceLoans)
		return ({'intResponse': 200, 'strAnswer': 'update lista cash successfully', 'pieceCash': pieceCash, 'pieceLoans':pieceLoans})
	except Exception as exception:
		print("Exception fnBorrowBank", exception.args)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

def fnCreateCoin(teamId, areaDragContainer, item):
	try:
		print("teamId",teamId, "borrow From Bank")
		print("areaDragContainer: ",areaDragContainer, "Item: ", item)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		valor = item['Valor'] if 'Valor' in item else item['valor']
		typeI = item['tipo'] if 'tipo' in item else item['type']
		params = (teamId, areaDragContainer, valor, typeI)
		cursor.callproc("sp_createPiece", params)
		jsonRow = cursor.fetchone()
		item['id'] = jsonRow['idPiece']
		print(jsonRow)
		
		MysqlCnx.commit()
		print("ACTUALIZADA lista cash separacion piezas", item)
		return ({'intResponse': 200, 'strAnswer': 'update lista cash successfully', 'newCoin': item})
	except Exception as exception:
		print("Exception fnBorrowBank", exception.args)


def fnDeleteCoinByID(teamId, areaDragContainer, item):
	try:
		print("teamId",teamId, "delete coin by id")
		print("areaDragContainer: ",areaDragContainer, "Item: ", item)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		id = item['StatusBoardId'] if 'StatusBoardId' in item else item['id']
		params = (id)
		cursor.callproc("sp_deletePieceById", [params])
		
		MysqlCnx.commit()
		print("BORRADA pieza borrada", item)
		return ({'intResponse': 200, 'strAnswer': 'delete coin successfully'})
	except Exception as exception:
		print("Exception deleteCoinByID", exception.args)

def fnPayLoan(teamId, areaDragContainer, item):
	try:
		print("teamId",teamId, "pay Loan$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
		print("areaDragContainer: ",areaDragContainer, "Item: ", item)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		if(item['valor'] == 0):
			params = (item['id'])
			cursor.callproc("sp_deletePieceById", [params])
			print("Se pago el loan por completo")
			MysqlCnx.commit()
			return({'intResponse': 200, 'strAnswer': 'Delete loan because paid complete it'})

		params = (item['id'], areaDragContainer, item['type'], item['valor'])
		print(params, "paraaaaaaaaaaaaaaaaams")
		cursor.callproc("sp_updPieceByID", params)
		MysqlCnx.commit()
		print(cursor.fetchall())
		print("ACTUALIZADA PIECE$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$", item)
		return ({'intResponse': 200, 'strAnswer': 'pay loan successfully'})
	except Exception as exception:
		print("Exception deleteCoinByID", exception.args)

def fnPayGrossProfit(teamId, areasDrag, listValoresToPay, item):
	try:
		jsonResponse ={}
		areas = {
			22:'cdkLstChangeI',
			23:'cdkLstMarketingS',
			25:'cdkLstAdministration',
			26:'cdkLstAdminOver'
		}
		print("teamId",teamId, "pay Loan$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
		print("areaDragContainer: ",areasDrag, "Item: ", item)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (item['id'] )
		cursor.callproc("sp_deletePieceById", [params])
		print("se borra la moneda de cash")
		MysqlCnx.commit()

		for i, idList in enumerate(areasDrag, start=0):
			print(listValoresToPay[i], idList)
			params = (teamId, idList, listValoresToPay[i], 1)
			cursor.callproc("sp_createPiece", params)
			jsonRow = cursor.fetchone()
			print(jsonRow)
			jsonResponse[areas[idList]] = {}
			jsonResponse[areas[idList]]['idPiece'] = jsonRow['idPiece']
			jsonResponse[areas[idList]]['valor'] = listValoresToPay[i]
		MysqlCnx.commit()
		print("ACTUALIZADA PIECE$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$", jsonResponse)
		return ({'intResponse': 200, 'strAnswer': 'pay gross profitt successfully', 'info': jsonResponse})
	except Exception as exception:
		print("Exception payGrossProfit", exception.args)

'''****************************************************************************
   * Author: BPR
   * Date: 24/05/2021
   * Summary: <Obtiene los Supplies por TeamId>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnGetSuppliesByTeamId(teamId):
	try:
		print("fnGetSuppliesByTeamId",teamId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		cursor.callproc("sp_getSumSuppliesByTeamId", [teamId])
		supplies = cursor.fetchone()
		print("Supplies",supplies)
		totalSupplies = float( 0 if supplies['Supplies'] == None else supplies['Supplies'])
		return {'intResponse': 200, 'Supplies': totalSupplies}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
   * Author: BPR
   * Date: 17/06/2021
   * Summary: <Obtiene los Advertising por TeamId>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnGetAdvertising(teamId):
	try:
		print("fnGetAdvertising",teamId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		cursor.callproc("sp_getAdvertisingByTeamId", [teamId])
		advertising = cursor.fetchone()
		print("Advertising",advertising)
		totalAdvertising = float( 0 if advertising['Advertising'] == None else advertising['Advertising'])
		return {'intResponse': 200, 'Advertising': totalAdvertising}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

def fnGetRetainedEarningsAllTeams(WokshopId):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (WokshopId)
		cursor.callproc("sp_getAllTeamsRetainedEarnings",[params])
		jsonRows = cursor.fetchall()
		for row in jsonRows:
			row['retained'] = int(row['retained'])
		return ({'intResponse': 200, 'strAnswer': 'get succsesfully retained Earnings', 'info': jsonRows})	
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args})	

###################################################END BOARD#################################################

def fnGetTextAreasByWorkshopId(workshopId, typeReport):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (workshopId, typeReport)
		cursor.callproc("sp_getTextAreaReporst",params)
		jsonRows = cursor.fetchall()
		return ({'intResponse': 200, 'strAnswer': 'get succsesfully text areas', 'info': jsonRows})	
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args})	

def fncreateUpdateTextAreaReports(workshopId, lstTextArea):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		for textArea in lstTextArea:
			params = (textArea['idtextAreaReports'], textArea['text'], textArea['typeReport'], workshopId)
			cursor.callproc("sp_createUpdateTextAreaReports", params)
			jsonRow = cursor.fetchone()
			if jsonRow != None:
				textArea['idtextAreaReports'] = jsonRow['idText']		
		MysqlCnx.commit()
		return ({'intResponse': 200, 'strAnswer': 'update lista text areas', 'newLst': lstTextArea})
	except Exception as exception:
		print("Exception fncreateUpdateTextAreaReports", exception.args)

###################################################START TEAM################################################

'''****************************************************************************
   * Author: BPR
   * Date: 11/05/2021
   * Summary: <Obtener team by id con sus team members>
   ****************************************************************************'''

def fnGetTeamAndMembersByID(teamId):
	try:
		print("fnGetTeamAndMembersByID",teamId)
		jsonResponseTeam = fnGetTeamByID(teamId)
		jsnResponseFacilitators = fnfacilitatorsgetData(jsonResponseTeam['team']['WokshopId'])
		print("jsonResponseTeam",jsonResponseTeam)
		jsnResponseObservers = fnGetAllObserversByWorkshopID(jsonResponseTeam['team']['WokshopId'])
		print("jsnResponseObservers",jsnResponseObservers)
		jsonResponseMembers = fnGetTeamMembersByID(teamId)
		print("jsonResponseMembers",jsonResponseMembers)
		jsnResponseColors = fnGetTeamColorsByID(teamId)
		if(jsonResponseTeam['intResponse'] == 200 and jsonResponseMembers['intResponse'] == 200):
			return {
				'intResponse': 200, 
				'team': jsonResponseTeam['team'], 
				'members': jsonResponseMembers['members'],
				'colors': jsnResponseColors['colors'],
				'facilitators': jsnResponseFacilitators['data'],
				'observers': jsnResponseObservers['observers']
			}
		else:
			return ({'intResponse': 203, 'strAnswer': "There was an exception"})
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})


'''****************************************************************************
   * Author: BPR
   * Date: 11/05/2021
   * Summary: <Obtener team by id con sus team members>
   ****************************************************************************'''

def fnGetTeamByID(teamId):
	try:
		print("fnGetTeamByID",teamId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId)
		cursor.callproc("sp_getTeamById", [params])
		jsonRows = cursor.fetchone()
		print("fnGetTeamByID2",jsonRows)
		return {'intResponse': 200, 'team': jsonRows}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})


'''****************************************************************************
   * Author: BPR
   * Date: 11/05/2021
   * Summary: <Obtener team members by id>
   ****************************************************************************'''

def fnGetTeamMembersByID(teamId):
	try:
		print("fnGetTeamMembersByID",teamId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId)
		cursor.callproc("sp_getAllTeamMembersByTeamID", [params])
		jsonRows = cursor.fetchall()
		arrMembers = []
		for member in jsonRows:
			print("member",member)
			arrMembers.append({'UserID':member['UserID'], 'nameComplete':member['nameComplete'], 'Role':"" })
			jsonResponseRoles = fnGetTeamMemberRolesByID(member['UserID'])
			for role in jsonResponseRoles['roles']:
				arrMembers.append({'UserID':member['UserID'], 'nameComplete':member['nameComplete'], 'Role':role['Role']})
		return {'intResponse': 200, 'members': arrMembers}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
   * Author: BPR
   * Date: 11/05/2021
   * Summary: <Obtener los roles de los team members by id>
   ****************************************************************************'''

def fnGetTeamMemberRolesByID(userId):
	try:
		print("fnGetTeamMemberRolesByID",userId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (userId)
		cursor.callproc("sp_getAllTeamMemberRolesByID", [params])
		jsonRows = cursor.fetchall()
		return {'intResponse': 200, 'roles': jsonRows}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
   * Author: BPR
   * Date: 11/05/2021
   * Summary: <Obtener el ingreso mas reciente entre todos sus usuarios>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnSetUpTeamByID(teamId, workShopId, teamAvatar, teamColor, arrayOfMembers):
	try:
		arrResponse = []
		strAnswer = ""
		print("fnSetUpTeamByID",teamId, workShopId, teamAvatar, teamColor, arrayOfMembers)
		jsonResponseTeamAvatar = fnSetTeamAvatarByID(teamId, workShopId, teamAvatar) 
		print("jsonResponseTeamAvatar",jsonResponseTeamAvatar)
		jsonResponseTeamColor = fnSetTeamColorByID(teamId, workShopId, teamColor)
		print("jsonResponseTeamColor",jsonResponseTeamColor)
		jsonResponseDelete = fnDeleteUserRolesByID(teamId)
		print("jsonResponseDelete",jsonResponseDelete)
		for member in arrayOfMembers:
			print("member",member)
			jsonResponseMemberRol = fnSetMemberRolByID(teamId, member['UserID'], member['Role'])
			print("jsonResponseMemberRol",jsonResponseMemberRol)
		if(jsonResponseTeamAvatar['intResponse']==203):
			strAnswer+=jsonResponseTeamAvatar['strAnswer']
		if(jsonResponseTeamColor['intResponse']==203):
			strAnswer+=jsonResponseTeamColor['strAnswer']
		if(strAnswer != ""):
			return {'intResponse': 203, 'strAnswer': strAnswer}
		else:
			return {'intResponse': 200, 'strAnswer': 'The Team was edited successfully!'}
	except Exception as exception:
		return ({'intResponse': 400, 'strAnswer': exception.args[1]})


'''****************************************************************************
   * Author: BPR
   * Date: 19/05/2021
   * Summary: <Elimina los registros de los roles de usuarios>
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnDeleteUserRolesByID(teamId):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId)
		cursor.callproc("sp_DeleteUserRolesByTeamID",[params])
		MysqlCnx.commit()
		return {'intResponse': 200, 'strAnswer': 'successful'}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
   * Author: BPR
   * Date: 11/05/2021
   * Summary: <Actualizar el avatar del equipo>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnSetTeamAvatarByID(teamId, workShopId, teamAvatar):
	try:
		print("fnSetTeamAvatarByID",teamId, workShopId, teamAvatar)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId, workShopId, teamAvatar)
		cursor.callproc("sp_setTeamAvatar", params)
		MysqlCnx.commit()
		jsnRow = cursor.fetchone()
		return jsnRow
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
   * Author: BPR
   * Date: 11/05/2021
   * Summary: <Actualizar el color del equipo>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnSetTeamColorByID(teamId, workShopId, teamColor):
	try:
		print("fnSetTeamColorByID",teamId, workShopId, teamColor)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId, workShopId, teamColor)
		cursor.callproc("sp_setTeamColor", params)
		MysqlCnx.commit()
		jsnRow = cursor.fetchone()
		return jsnRow
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
   * Author: BPR
   * Date: 11/05/2021
   * Summary: <Actualizar el rol del miembro del equipo>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnSetMemberRolByID(teamId, userId, rol):
	try:
		print("fnSetTeamColorByID",teamId, userId, rol)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId, userId, rol)
		cursor.callproc("sp_setMemberRol", params)
		MysqlCnx.commit()
		return {'intResponse': 200, 'strAnswer': 'successful'}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})


'''****************************************************************************
   * Author: BPR
   * Date: 11/05/2021
   * Summary: <Obtener colores distintos al propio>
   ****************************************************************************'''

def fnGetTeamColorsByID(teamId):
	try:
		print("fnGetTeamColorsByID",teamId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId)
		cursor.callproc("sp_getTeamColorsById", [params])
		jsonRows = cursor.fetchall()
		print("fnGetTeamColorsByID",jsonRows)
		arrColors = []
		for color in jsonRows:
			arrColors.append(color['Color'])
		return {'intResponse': 200, 'colors': arrColors}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})


'''****************************************************************************
   * Author: BPR
   * Date: 11/05/2021
   * Summary: <Obtener team members by id>
   ****************************************************************************'''

def fnGetAllTeamsAndMembersByWorkShopID(workShopId):
	try:
		print("fnGetAllTeamsAndMembersByWorkShopID",workShopId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (workShopId)
		cursor.callproc("sp_getAllTeamsByWorkShopId", [workShopId])
		jsontTeams = cursor.fetchall()
		print("jsontTeams",jsontTeams)
		arrAllTeams = []
		for team in jsontTeams:
			arrMembers = fnGetTeamMembersByID(team['TeamId'])
			arrRoleMembers = fnSetTeamMemberByRol(arrMembers['members'])
			arrAllTeams.append({
				'team':team,
				'members': arrRoleMembers['members']
			})
		jsnResponseFacilitators = fnfacilitatorsgetData(workShopId)
		cursor.callproc("sp_getFacilitTeamIdByWorkshopId", [workShopId])
		facilitatorTeamId = cursor.fetchone()
		for facil in jsnResponseFacilitators['data']:
			facil['TeamId'] = facilitatorTeamId['TeamId']
		print("jsnResponseFacilitators",jsnResponseFacilitators)
		jsnResponseObservers = fnGetAllObserversByWorkshopID(workShopId)
		print("jsnResponseObservers",jsnResponseObservers)
		return {
			'intResponse': 200, 
			'teams': arrAllTeams, 
			'facilitators': jsnResponseFacilitators['data'],
			'observers': jsnResponseObservers['observers']
		}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})


def fnGetAllTeamsByWorkShopID(workShopId):
	try:
		print("fnGetAllTeamsByWorkShopID",workShopId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		cursor.callproc("sp_getAllTeamsByWorkShopId", [workShopId])
		jsontTeams = cursor.fetchall()
		print("jsontTeams",jsontTeams)
		for team in jsontTeams:
			jsnSupplies = fnGetSuppliesByTeamId(team['TeamId'])
			jsnAdvertising = fnGetAdvertising(team['TeamId'])
			team['Supplies'] = jsnSupplies['Supplies']
			team['TotAdvertising'] = jsnAdvertising['Advertising']
			cursor.callproc("sp_getImprovementsByTeamId", [team['TeamId']])
			team['improvements'] = cursor.fetchall()
		print("jsontTeams2222",jsontTeams)
		return {'intResponse': 200, 'teams': jsontTeams}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})


def fnSetTeamMemberByRol(arrAllMembers):
	try:
		arrCeo = []
		arrCfo = []
		arrCmo = []
		arrCoo = []
		arrCto = []
		arrMembers = []
		for member in arrAllMembers:
			if member['Role'] == 'CEO':
				arrCeo.append(member)
			elif member['Role'] == 'CFO':
				arrCfo.append(member)
			elif member['Role'] == 'CMO':
				arrCmo.append(member)
			elif member['Role'] == 'COO':
				arrCoo.append(member)
			elif member['Role'] == 'CTO':
				arrCto.append(member)
			else:
				arrMembers.append(member)
		return {'intResponse': 200, 'members': {
			'CEO':arrCeo,
			'CFO':arrCfo,
			'CMO':arrCmo,
			'COO':arrCoo,
			'CTO':arrCto,
			'members':arrMembers,
		}}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

def fnGetValidTeamsSetUp(workshopId):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		cursor.callproc("sp_validateSetUpTeams", [workshopId])
		jsonValidTeams = cursor.fetchone()
		if(jsonValidTeams['validTeamSetUp'] == 0):
			return ({'validSetUpTeams':False})
		else: 
			return ({'validSetUpTeams':True})
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

#EFA 2
def fnAssignDefaultTeamNames(workshopId, teamId, facilitator):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		cursor.callproc("sp_getTeamById", [teamId])
		team = cursor.fetchone()
		facilitatorsDefaultName = 'ACME'
		defaultTeamNames = ['ABC','DEF','GHI','JKL','MNO','PQR']
		defaultTeamColors = ['#1b3f89','#b5dde5','#bf7b16','#243454','#2c146c','#943484','#e4e4ec','#accbfc','#e4c484']
		random.shuffle(defaultTeamColors)
		socketInfo={}
		if not team['Avatar']:
			if facilitator == 'false':
				for name in defaultTeamNames:
					response = fnSetTeamAvatarByID(teamId, workshopId, name)
					if response['intResponse'] == 200:
						socketInfo['teamId'] = teamId
						socketInfo['name'] = name
						break
			else:
				response = fnSetTeamAvatarByID(teamId, workshopId, facilitatorsDefaultName)				
				socketInfo['teamId'] = teamId
				socketInfo['name'] = facilitatorsDefaultName
		if not team['Color']:
			for color in defaultTeamColors:
				response = fnSetTeamColorByID(teamId, workshopId, color)
				if response['intResponse'] == 200:
					socketInfo['teamId'] = teamId
					socketInfo['color'] = color
					if color == '#1b3f89':
						socketInfo['strBackground'] = "./../../../assets/MIDTHEME3.jpg";
						socketInfo['blnBackground'] = None
					elif color == '#b5dde5':
						socketInfo['strBackground'] = "./../../../assets/MIDTHEME2.jpg";
						socketInfo['blnBackground'] = 'blnBackground2'
					elif color == '#bf7b16':
						socketInfo['strBackground'] = "./../../../assets/MIDTHEME1.jpg";
						socketInfo['blnBackground'] = None
					elif color == '#243454':
						socketInfo['strBackground'] = "./../../../assets/DARKTHEME3.jpg";
						socketInfo['blnBackground'] = 'blnBackground4'
					elif color == '#2c146c':
						socketInfo['strBackground'] = "./../../../assets/DARKTHEME2.jpg";
						socketInfo['blnBackground'] = 'blnBackground5'
					elif color == '#943484':
						socketInfo['strBackground'] = "./../../../assets/DARKTHEME1.jpg";
						socketInfo['blnBackground'] = 'blnBackground6'
					elif color == '#e4e4ec':
						socketInfo['strBackground'] = "./../../../assets/LIGHTTHEME3.jpg";
						socketInfo['blnBackground'] = 'blnBackground7_8'
					elif color == '#accbfc':
						socketInfo['strBackground'] = "./../../../assets/LIGHTTHEME2.jpg";
						socketInfo['blnBackground'] = 'blnBackground7_8'
					elif color == '#e4c484':
						socketInfo['strBackground'] = "./../../../assets/LIGHTTHEME1.jpg";
						socketInfo['blnBackground'] = 'blnBackground9'
					else:
						socketInfo['strBackground'] = "./../../../assets/DARKTHEME2.jpg";
						socketInfo['blnBackground'] = 'blnBackgroundBlue'
					break
		return {'intResponse': 200, 'socketInfo': socketInfo}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})
#EFA 2 f
###################################################END TEAM##################################################

###################################################START ORDER##################################################


'''****************************************************************************
   * Author: BPR
   * Date: 21/05/2021
   * Summary: <Obtiene las Ordenes por workShopId>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnGetOrdersByWorkShopId(workShopId):
	try:
		# print("fnGetOrdersByWorkShopId",workShopId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		cursor.callproc("sp_getOrdersByWorkShopId", [workShopId])
		arrOrders = cursor.fetchall()
		for order in arrOrders:
			if(order['Customizing'] == 0):
				order['Customizing'] = False
			else:	
				order['Customizing'] = True
			jsonBids = fnGetBidsByOrderId(order['OrderId'])
			if(jsonBids['intResponse'] == 200):
				order['Bids'] = jsonBids['Bids']
			else:
				order['Bids'] =[]
		# print("jsonOrders",arrOrders)
		return {'intResponse': 200, 'orders': arrOrders}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
   * Author: DCM
   * Date: 17/08/2021
   * Summary: <Obtiene datos de las Ordenes por workShopId y mes>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnGetOrdersByWSandMonth(workShopId, month):
	try:
		print("entro fn getOrderdata", workShopId,month )
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (workShopId, month)
		cursor.callproc("sp_getDataOrdersbyWSandMonth", params)
		arrOrders = cursor.fetchall()
		print("resultados getOrders::", arrOrders)
		return {'intResponse': 200, 'orders': arrOrders}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
   * Author: BPR
   * Date: 04/06/2021
   * Summary: <Obtiene las Bids por orderId>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnGetBidsByOrderId(orderId):
	try:
		# print("fnGetOrdersByWorkShopId",orderId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		cursor.callproc("sp_getBidsByOrderId", [orderId])
		arrBids = cursor.fetchall()
		# print("arrBids",arrBids)
		return {'intResponse': 200, 'Bids': arrBids}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
   * Author: BPR
   * Date: 21/05/2021
   * Summary: <Crea Ordenes>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnCreateOrders(workshopId, arrTeamsId, month, BoardMode):
	print("fnCreateOrders - wsId:",workshopId," arrTeamsId: ", arrTeamsId," month:", month)
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	r = len(arrTeamsId)
	print("r: ", r)
	if(month == 1 and (BoardMode == "NM" or (BoardMode == "DM" and r>=5))):
		print("entra if mes 1 modo NORMAL -------------")
		if(r<4):
			r=4
		print("en if r - ",r)
		for x in range(r):
			print("for x:",x)
			params = (workshopId, (101+x),3,60,1,0)
			cursor.callproc("sp_createOrders",params)			
			MysqlCnx.commit()
			orderId = cursor.fetchone()
			print("orderId",orderId)
			for x in range(2):
				print("segundo for x:",x)
				fnCreateBid(orderId['OrderId'], (x-2))
	if(month == 1 and (BoardMode == "DM" and r<=4)):
		print("entra if mes 1 modo modo DEMO -------------")
		jsonMarket = fnInfoOrders(arrTeamsId, month)
		for x in range(len(jsonMarket['arrInfo'])):
			params = (workshopId, ((month*100)+1+x),jsonMarket['arrInfo'][x]['q'],jsonMarket['arrInfo'][x]['t'],month,jsonMarket['arrInfo'][x]['c'])
			cursor.callproc("sp_createOrders",params)			
			MysqlCnx.commit()
			orderId = cursor.fetchone()
			print("orderId",orderId)
			for x in arrTeamsId:
				fnCreateBid(orderId['OrderId'], x)
	if(month >= 2):
		print("entra if mes >=2 modo modo DEMO -------------")
		r = 0
		jsonMarket = fnInfoOrders(arrTeamsId, month)
		print("jsonMarket",jsonMarket)
		for x in range(len(jsonMarket['arrInfo'])):
			params = (workshopId, ((month*100)+1+x),jsonMarket['arrInfo'][x]['q'],jsonMarket['arrInfo'][x]['t'],month,jsonMarket['arrInfo'][x]['c'])
			cursor.callproc("sp_createOrders",params)			
			MysqlCnx.commit()
			orderId = cursor.fetchone()
			print("orderId",orderId)
			for x in arrTeamsId:
				fnCreateBid(orderId['OrderId'], x)
	print("fnCreateOrders FIN")
	return ResponseMessages.sus200

'''****************************************************************************
   * Author: BPR
   * Date: 09/06/2021
   * Summary: <Obtiene los quantity y terms para las ordenes>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnInfoOrders(arrTeamsId, month):
	r = 0
	jsonMarket = {}

	arrMarket =[
		# para el mes 1 en modo demo
		{"month":1, "teams":2, "arrInfo":[{"q":3,"t":90,"c":0},{"q":2,"t":30,"c":0},{"q":1,"t":0,"c":0},{"q":1,"t":0,"c":0}]},
		{"month":1, "teams":3, "arrInfo":[{"q":4,"t":90,"c":0},{"q":3,"t":30,"c":0},{"q":2,"t":0,"c":0},{"q":1,"t":30,"c":0},{"q":1,"t":0,"c":0}]},
		{"month":1, "teams":4, "arrInfo":[{"q":4,"t":90,"c":0},{"q":3,"t":0,"c":0},{"q":2,"t":30,"c":0},{"q":2,"t":60,"c":0},{"q":2,"t":0,"c":0},{"q":1,"t":30,"c":0},{"q":1,"t":90,"c":0}]},
		# fin para el mes 1 en modo demo

		{"month":2, "teams":2, "arrInfo":[{"q":3,"t":90,"c":0},{"q":2,"t":0,"c":0},{"q":2,"t":30,"c":0},{"q":1,"t":60,"c":0},{"q":1,"t":30,"c":0}]},
		{"month":2, "teams":3, "arrInfo":[{"q":4,"t":90,"c":0},{"q":3,"t":0,"c":0},{"q":2,"t":30,"c":0},{"q":2,"t":60,"c":0},{"q":2,"t":0,"c":0},{"q":1,"t":30,"c":0}]},
		# cambio del mercado por eliza
		# {"month":2, "teams":4, "arrInfo":[{"q":5,"t":60,"c":0},{"q":3,"t":30,"c":0},{"q":3,"t":90,"c":0},{"q":2,"t":90,"c":0},{"q":2,"t":60,"c":0},{"q":2,"t":30,"c":0},{"q":2,"t":0,"c":0}]},
		{"month":2, "teams":4, "arrInfo":[{"q":4,"t":90,"c":0},{"q":3,"t":0,"c":0},{"q":2,"t":30,"c":0},{"q":2,"t":60,"c":0},{"q":2,"t":30,"c":0},{"q":2,"t":0,"c":0},{"q":1,"t":30,"c":0},{"q":1,"t":90,"c":0}]},
		{"month":2, "teams":5, "arrInfo":[{"q":5,"t":60,"c":0},{"q":4,"t":0,"c":0},{"q":3,"t":30,"c":0},{"q":3,"t":90,"c":0},{"q":2,"t":60,"c":0},{"q":2,"t":30,"c":0},{"q":1,"t":90,"c":0},{"q":1,"t":60,"c":0},{"q":1,"t":0,"c":0}]},
		{"month":2, "teams":6, "arrInfo":[{"q":5,"t":30,"c":0},{"q":4,"t":30,"c":0},{"q":4,"t":60,"c":0},{"q":3,"t":0,"c":0},{"q":3,"t":90,"c":0},{"q":2,"t":60,"c":0},{"q":2,"t":30,"c":0},{"q":2,"t":0,"c":0},{"q":1,"t":30,"c":0},{"q":1,"t":0,"c":0}]},

		{"month":3, "teams":2, "arrInfo":[{"q":5,"t":90,"c":0},{"q":3,"t":0,"c":1},{"q":2,"t":30,"c":0},{"q":1,"t":30,"c":0},{"q":1,"t":0,"c":0},{"q":1,"t":30,"c":0}]},
		{"month":3, "teams":3, "arrInfo":[{"q":5,"t":90,"c":0},{"q":4,"t":0,"c":0},{"q":3,"t":30,"c":1},{"q":2,"t":30,"c":0},{"q":2,"t":0,"c":0},{"q":2,"t":30,"c":0},{"q":1,"t":0,"c":0},{"q":1,"t":30,"c":0}]},
		# cambio del mercado por eliza
		# {"month":3, "teams":4, "arrInfo":[{"q":5,"t":0,"c":0},{"q":4,"t":30,"c":1},{"q":3,"t":30,"c":0},{"q":3,"t":90,"c":0},{"q":2,"t":0,"c":0},{"q":2,"t":60,"c":0},{"q":2,"t":90,"c":0},{"q":1,"t":0,"c":0},{"q":1,"t":30,"c":0}]},
		{"month":3, "teams":4, "arrInfo":[{"q":5,"t":90,"c":0},{"q":4,"t":0,"c":0},{"q":3,"t":30,"c":0},{"q":3,"t":60,"c":1},{"q":2,"t":30,"c":0},{"q":2,"t":0,"c":0},{"q":2,"t":30,"c":0},{"q":2,"t":90,"c":0},{"q":1,"t":0,"c":0},{"q":1,"t":30,"c":0},{"q":1,"t":30,"c":0}]},
		{"month":3, "teams":5, "arrInfo":[{"q":6,"t":60,"c":0},{"q":4,"t":30,"c":1},{"q":4,"t":0,"c":0},{"q":4,"t":30,"c":0},{"q":4,"t":60,"c":0},{"q":3,"t":0,"c":0},{"q":2,"t":30,"c":0},{"q":2,"t":60,"c":0},{"q":1,"t":90,"c":0}]},
		{"month":3, "teams":6, "arrInfo":[{"q":6,"t":60,"c":0},{"q":6,"t":90,"c":0},{"q":4,"t":30,"c":1},{"q":4,"t":0,"c":0},{"q":4,"t":60,"c":0},{"q":4,"t":90,"c":0},{"q":3,"t":60,"c":0},{"q":2,"t":60,"c":0},{"q":2,"t":30,"c":0},{"q":1,"t":0,"c":0}]},

		{"month":4, "teams":2, "arrInfo":[{"q":8,"t":90,"c":0},{"q":4,"t":0,"c":0},{"q":3,"t":30,"c":0},{"q":2,"t":60,"c":1},{"q":1,"t":30,"c":0},{"q":1,"t":30,"c":0}]},
		{"month":4, "teams":3, "arrInfo":[{"q":8,"t":90,"c":0},{"q":6,"t":0,"c":0},{"q":5,"t":30,"c":0},{"q":4,"t":60,"c":0},{"q":3,"t":30,"c":1},{"q":2,"t":0,"c":0},{"q":2,"t":30,"c":0},{"q":1,"t":90,"c":0},{"q":1,"t":0,"c":0}]},
		# cambio del mercado por eliza
		# {"month":4, "teams":4, "arrInfo":[{"q":6,"t":30,"c":0},{"q":5,"t":60,"c":0},{"q":4,"t":30,"c":1},{"q":4,"t":90,"c":0},{"q":3,"t":30,"c":0},{"q":2,"t":60,"c":0},{"q":2,"t":0,"c":0},{"q":1,"t":90,"c":0}]},
		{"month":4, "teams":4, "arrInfo":[{"q":8,"t":90,"c":0},{"q":6,"t":0,"c":0},{"q":5,"t":30,"c":0},{"q":4,"t":60,"c":0},{"q":3,"t":30,"c":1},{"q":3,"t":0,"c":0},{"q":2,"t":30,"c":0},{"q":2,"t":90,"c":0},{"q":2,"t":0,"c":0},{"q":2,"t":30,"c":0},{"q":1,"t":90,"c":0},{"q":1,"t":0,"c":0}]},
		{"month":4, "teams":5, "arrInfo":[{"q":8,"t":60,"c":0},{"q":6,"t":60,"c":0},{"q":4,"t":30,"c":1},{"q":4,"t":0,"c":0},{"q":4,"t":30,"c":0},{"q":4,"t":60,"c":0},{"q":3,"t":90,"c":0},{"q":2,"t":60,"c":0},{"q":2,"t":30,"c":0},{"q":1,"t":0,"c":0}]},
		{"month":4, "teams":6, "arrInfo":[{"q":6,"t":60,"c":0},{"q":5,"t":30,"c":0},{"q":4,"t":30,"c":1},{"q":4,"t":0,"c":0},{"q":4,"t":90,"c":0},{"q":4,"t":30,"c":0},{"q":3,"t":90,"c":0},{"q":3,"t":0,"c":0},{"q":2,"t":30,"c":0},{"q":2,"t":60,"c":0},{"q":2,"t":90,"c":0},{"q":1,"t":30,"c":0},{"q":1,"t":60,"c":0}]},

		{"month":5, "teams":4, "arrInfo":[{"q":6,"t":90,"c":0},{"q":4,"t":0,"c":0},{"q":4,"t":30,"c":1},{"q":4,"t":30,"c":0},{"q":3,"t":30,"c":0},{"q":3,"t":60,"c":0},{"q":2,"t":30,"c":1},{"q":2,"t":60,"c":0},{"q":1,"t":0,"c":0}]},
		{"month":5, "teams":5, "arrInfo":[{"q":8,"t":30,"c":0},{"q":6,"t":60,"c":0},{"q":6,"t":90,"c":0},{"q":4,"t":30,"c":1},{"q":4,"t":0,"c":0},{"q":4,"t":30,"c":0},{"q":4,"t":60,"c":0},{"q":3,"t":90,"c":0},{"q":2,"t":30,"c":0},{"q":1,"t":30,"c":0}]},
		{"month":5, "teams":6, "arrInfo":[{"q":8,"t":30,"c":0},{"q":6,"t":60,"c":0},{"q":5,"t":90,"c":0},{"q":5,"t":60,"c":0},{"q":4,"t":0,"c":0},{"q":4,"t":30,"c":1},{"q":3,"t":0,"c":0},{"q":3,"t":90,"c":0},{"q":3,"t":30,"c":0},{"q":2,"t":30,"c":1},{"q":2,"t":60,"c":0},{"q":2,"t":0,"c":0},{"q":1,"t":30,"c":0}]},

		{"month":6, "teams":4, "arrInfo":[{"q":6,"t":90,"c":0},{"q":4,"t":0,"c":0},{"q":4,"t":30,"c":1},{"q":4,"t":30,"c":0},{"q":3,"t":30,"c":0},{"q":3,"t":90,"c":0},{"q":2,"t":30,"c":0},{"q":2,"t":60,"c":0},{"q":1,"t":0,"c":0},{"q":1,"t":0,"c":0}]},
		{"month":6, "teams":5, "arrInfo":[{"q":8,"t":30,"c":0},{"q":6,"t":60,"c":0},{"q":5,"t":90,"c":0},{"q":4,"t":30,"c":1},{"q":4,"t":0,"c":0},{"q":4,"t":30,"c":0},{"q":3,"t":90,"c":0},{"q":2,"t":30,"c":0},{"q":2,"t":30,"c":1},{"q":1,"t":0,"c":0},{"q":1,"t":60,"c":0}]},
		{"month":6, "teams":6, "arrInfo":[{"q":8,"t":30,"c":0},{"q":6,"t":60,"c":0},{"q":5,"t":90,"c":0},{"q":4,"t":60,"c":0},{"q":4,"t":0,"c":0},{"q":4,"t":30,"c":1},{"q":3,"t":0,"c":0},{"q":3,"t":90,"c":0},{"q":2,"t":30,"c":0},{"q":2,"t":30,"c":1},{"q":1,"t":0,"c":0},{"q":1,"t":0,"c":0}]}
	]

	for json in arrMarket:
		# if(json['month'] == month and (len(arrTeamsId) == json['teams'] or (len(arrTeamsId) < 4 and json['teams'] == 4) )):
		if(json['month'] == month and (len(arrTeamsId) == json['teams'] or (len(arrTeamsId) < 4 and json['teams'] == 4 and month >= 5) )):
			jsonMarket = json
			break
	return (jsonMarket)
#BACKUP Antes modify market
"""arrMarket =[
		# para el mes 1 en modo demo
		{"month":1, "teams":2, "arrInfo":[{"q":3,"t":90,"c":0},{"q":2,"t":30,"c":0},{"q":1,"t":0,"c":0},{"q":1,"t":0,"c":0}]},
		{"month":1, "teams":3, "arrInfo":[{"q":4,"t":90,"c":0},{"q":3,"t":30,"c":0},{"q":2,"t":0,"c":0},{"q":1,"t":30,"c":0},{"q":1,"t":0,"c":0}]},
		{"month":1, "teams":4, "arrInfo":[{"q":4,"t":90,"c":0},{"q":3,"t":0,"c":0},{"q":2,"t":30,"c":0},{"q":2,"t":60,"c":0},{"q":2,"t":0,"c":0},{"q":1,"t":30,"c":0},{"q":1,"t":90,"c":0}]},
		# fin para el mes 1 en modo demo

		{"month":2, "teams":2, "arrInfo":[{"q":3,"t":90,"c":0},{"q":2,"t":0,"c":0},{"q":2,"t":30,"c":0},{"q":1,"t":60,"c":0},{"q":1,"t":30,"c":0}]},
		{"month":2, "teams":3, "arrInfo":[{"q":4,"t":90,"c":0},{"q":3,"t":0,"c":0},{"q":2,"t":30,"c":0},{"q":2,"t":60,"c":0},{"q":2,"t":0,"c":0},{"q":1,"t":30,"c":0}]},
		# cambio del mercado por eliza
		# {"month":2, "teams":4, "arrInfo":[{"q":5,"t":60,"c":0},{"q":3,"t":30,"c":0},{"q":3,"t":90,"c":0},{"q":2,"t":90,"c":0},{"q":2,"t":60,"c":0},{"q":2,"t":30,"c":0},{"q":2,"t":0,"c":0}]},
		{"month":2, "teams":4, "arrInfo":[{"q":4,"t":90,"c":0},{"q":3,"t":0,"c":0},{"q":2,"t":30,"c":0},{"q":2,"t":60,"c":0},{"q":2,"t":30,"c":0},{"q":2,"t":0,"c":0},{"q":1,"t":30,"c":0},{"q":1,"t":90,"c":0}]},
		{"month":2, "teams":5, "arrInfo":[{"q":5,"t":60,"c":0},{"q":4,"t":0,"c":0},{"q":3,"t":30,"c":0},{"q":3,"t":90,"c":0},{"q":2,"t":60,"c":0},{"q":2,"t":30,"c":0},{"q":1,"t":90,"c":0},{"q":1,"t":60,"c":0},{"q":1,"t":0,"c":0}]},
		{"month":2, "teams":6, "arrInfo":[{"q":5,"t":30,"c":0},{"q":4,"t":30,"c":0},{"q":4,"t":60,"c":0},{"q":3,"t":0,"c":0},{"q":3,"t":90,"c":0},{"q":2,"t":60,"c":0},{"q":2,"t":30,"c":0},{"q":2,"t":0,"c":0},{"q":1,"t":30,"c":0},{"q":1,"t":0,"c":0}]},

		{"month":3, "teams":2, "arrInfo":[{"q":5,"t":90,"c":0},{"q":3,"t":0,"c":1},{"q":2,"t":30,"c":0},{"q":1,"t":30,"c":0},{"q":1,"t":0,"c":0},{"q":1,"t":30,"c":0}]},
		{"month":3, "teams":3, "arrInfo":[{"q":5,"t":90,"c":0},{"q":4,"t":0,"c":0},{"q":3,"t":30,"c":1},{"q":2,"t":30,"c":0},{"q":2,"t":0,"c":0},{"q":2,"t":30,"c":0},{"q":1,"t":0,"c":0},{"q":1,"t":30,"c":0}]},
		# cambio del mercado por eliza
		# {"month":3, "teams":4, "arrInfo":[{"q":5,"t":0,"c":0},{"q":4,"t":30,"c":1},{"q":3,"t":30,"c":0},{"q":3,"t":90,"c":0},{"q":2,"t":0,"c":0},{"q":2,"t":60,"c":0},{"q":2,"t":90,"c":0},{"q":1,"t":0,"c":0},{"q":1,"t":30,"c":0}]},
		{"month":3, "teams":4, "arrInfo":[{"q":5,"t":90,"c":0},{"q":4,"t":0,"c":0},{"q":3,"t":30,"c":0},{"q":3,"t":60,"c":1},{"q":2,"t":30,"c":0},{"q":2,"t":0,"c":0},{"q":2,"t":30,"c":0},{"q":2,"t":90,"c":0},{"q":1,"t":0,"c":0},{"q":1,"t":30,"c":0},{"q":1,"t":30,"c":0}]},
		{"month":3, "teams":5, "arrInfo":[{"q":6,"t":60,"c":0},{"q":4,"t":30,"c":1},{"q":4,"t":0,"c":0},{"q":4,"t":30,"c":0},{"q":4,"t":60,"c":0},{"q":3,"t":0,"c":0},{"q":2,"t":30,"c":0},{"q":2,"t":60,"c":0},{"q":1,"t":90,"c":0}]},
		{"month":3, "teams":6, "arrInfo":[{"q":6,"t":60,"c":0},{"q":6,"t":90,"c":0},{"q":4,"t":30,"c":1},{"q":4,"t":0,"c":0},{"q":4,"t":60,"c":0},{"q":4,"t":90,"c":0},{"q":3,"t":60,"c":0},{"q":2,"t":60,"c":0},{"q":2,"t":30,"c":0},{"q":1,"t":0,"c":0}]},

		{"month":4, "teams":2, "arrInfo":[{"q":8,"t":90,"c":0},{"q":4,"t":0,"c":0},{"q":3,"t":30,"c":0},{"q":2,"t":60,"c":1},{"q":1,"t":30,"c":0},{"q":1,"t":30,"c":0}]},
		{"month":4, "teams":3, "arrInfo":[{"q":8,"t":90,"c":0},{"q":6,"t":0,"c":0},{"q":5,"t":30,"c":0},{"q":4,"t":60,"c":0},{"q":3,"t":30,"c":1},{"q":2,"t":0,"c":0},{"q":2,"t":30,"c":0},{"q":1,"t":90,"c":0},{"q":1,"t":0,"c":0}]},
		# cambio del mercado por eliza
		# {"month":4, "teams":4, "arrInfo":[{"q":6,"t":30,"c":0},{"q":5,"t":60,"c":0},{"q":4,"t":30,"c":1},{"q":4,"t":90,"c":0},{"q":3,"t":30,"c":0},{"q":2,"t":60,"c":0},{"q":2,"t":0,"c":0},{"q":1,"t":90,"c":0}]},
		{"month":4, "teams":4, "arrInfo":[{"q":8,"t":90,"c":0},{"q":6,"t":0,"c":0},{"q":5,"t":30,"c":0},{"q":4,"t":60,"c":0},{"q":3,"t":30,"c":1},{"q":3,"t":0,"c":0},{"q":2,"t":30,"c":0},{"q":2,"t":90,"c":0},{"q":2,"t":0,"c":0},{"q":2,"t":30,"c":0},{"q":1,"t":90,"c":0},{"q":1,"t":0,"c":0}]},
		{"month":4, "teams":5, "arrInfo":[{"q":8,"t":60,"c":0},{"q":6,"t":60,"c":0},{"q":4,"t":30,"c":1},{"q":4,"t":0,"c":0},{"q":4,"t":30,"c":0},{"q":4,"t":60,"c":0},{"q":3,"t":90,"c":0},{"q":2,"t":60,"c":0},{"q":2,"t":30,"c":0},{"q":1,"t":0,"c":0}]},
		{"month":4, "teams":6, "arrInfo":[{"q":6,"t":60,"c":0},{"q":5,"t":30,"c":0},{"q":4,"t":30,"c":1},{"q":4,"t":0,"c":0},{"q":4,"t":90,"c":0},{"q":4,"t":30,"c":0},{"q":3,"t":90,"c":0},{"q":3,"t":0,"c":0},{"q":2,"t":30,"c":0},{"q":2,"t":60,"c":0},{"q":2,"t":90,"c":0},{"q":1,"t":30,"c":0},{"q":1,"t":60,"c":0}]},

		{"month":5, "teams":4, "arrInfo":[{"q":6,"t":90,"c":0},{"q":4,"t":0,"c":0},{"q":4,"t":30,"c":1},{"q":4,"t":30,"c":0},{"q":3,"t":30,"c":0},{"q":3,"t":60,"c":0},{"q":2,"t":30,"c":1},{"q":2,"t":60,"c":0},{"q":1,"t":0,"c":0}]},
		{"month":5, "teams":5, "arrInfo":[{"q":8,"t":30,"c":0},{"q":6,"t":60,"c":0},{"q":6,"t":90,"c":0},{"q":4,"t":30,"c":1},{"q":4,"t":0,"c":0},{"q":4,"t":30,"c":0},{"q":4,"t":60,"c":0},{"q":3,"t":90,"c":0},{"q":2,"t":30,"c":0},{"q":1,"t":30,"c":0}]},
		{"month":5, "teams":6, "arrInfo":[{"q":8,"t":30,"c":0},{"q":6,"t":60,"c":0},{"q":5,"t":90,"c":0},{"q":5,"t":60,"c":0},{"q":4,"t":0,"c":0},{"q":4,"t":30,"c":1},{"q":3,"t":0,"c":0},{"q":3,"t":90,"c":0},{"q":3,"t":30,"c":0},{"q":2,"t":30,"c":1},{"q":2,"t":60,"c":0},{"q":2,"t":0,"c":0},{"q":1,"t":30,"c":0}]},

		{"month":6, "teams":4, "arrInfo":[{"q":6,"t":90,"c":0},{"q":4,"t":0,"c":0},{"q":4,"t":30,"c":1},{"q":4,"t":30,"c":0},{"q":3,"t":30,"c":0},{"q":3,"t":90,"c":0},{"q":2,"t":30,"c":0},{"q":2,"t":60,"c":0},{"q":1,"t":0,"c":0},{"q":1,"t":0,"c":0}]},
		{"month":6, "teams":5, "arrInfo":[{"q":8,"t":30,"c":0},{"q":6,"t":60,"c":0},{"q":5,"t":90,"c":0},{"q":4,"t":30,"c":1},{"q":4,"t":0,"c":0},{"q":4,"t":30,"c":0},{"q":3,"t":90,"c":0},{"q":2,"t":30,"c":0},{"q":2,"t":30,"c":1},{"q":1,"t":0,"c":0},{"q":1,"t":60,"c":0}]},
		{"month":6, "teams":6, "arrInfo":[{"q":8,"t":30,"c":0},{"q":6,"t":60,"c":0},{"q":5,"t":90,"c":0},{"q":4,"t":60,"c":0},{"q":4,"t":0,"c":0},{"q":4,"t":30,"c":1},{"q":3,"t":0,"c":0},{"q":3,"t":90,"c":0},{"q":2,"t":30,"c":0},{"q":2,"t":30,"c":1},{"q":1,"t":0,"c":0},{"q":1,"t":0,"c":0}]}
	]
"""

'''****************************************************************************
   * Author: BPR
   * Date: 21/05/2021
   * Summary: <Crea bid de una order>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnCreateBid(orderId, teamId):
	print("fnCreateBid orderId:",orderId," teamId:", teamId)
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	params = (orderId, teamId)
	cursor.callproc("sp_createBid",params)			
	MysqlCnx.commit()
	return ResponseMessages.sus200

'''****************************************************************************
   * Author: BPR
   * Date: 21/05/2021
   * Summary: <Actualizar los teams de las Ordenes>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnUpdateOrdersTeams(arrayOfOrders):
	try:
		for order in arrayOfOrders:
			print("order",order)
			for bid in order['Bids']:
				if(bid['BidId'] > 0):
					fnUpdateOrderTeams(bid['BidId'],bid['TeamId'])
		return ResponseMessages.sus200
	except Exception as exception:
		print("fnUpdateOrdersTeams", exception)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
   * Author: BPR
   * Date: 21/05/2021
   * Summary: <Actualizar los teams de una Orden>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnUpdateOrderTeams(biId, teamId):
	try:
		print("fnUpdateOrderTeams",biId, teamId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (biId, teamId)
		cursor.callproc("sp_updateOrderTeams", params)
		MysqlCnx.commit()
		print("fnUpdateOrderTeams")
		return ({'intResponse': 200, 'strAnswer': 'update order successfully'})
	except Exception as exception:
		print("excepcion update order", exception.args)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
   * Author: BPR
   * Date: 21/05/2021
   * Summary: <Actualizar los Wining Teams de las Ordenes>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnUpdateOrdersWiningTeam(workshopId, arrayOfOrders):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		for order in arrayOfOrders:
			fnUpdateOrderWiningTeam(workshopId, order['OrderId'], order['WiningTeam'])
			for bid in order['Bids']:
				params = (bid['BidId'], bid['blnNotSupplies'])
				cursor.callproc("sp_updateBidIsWithdrawn", params)
		MysqlCnx.commit()
		return ResponseMessages.sus200
	except Exception as exception:
		print("fnUpdateOrdersWiningTeam", exception)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})


'''****************************************************************************
   * Author: BPR
   * Date: 22/07/2021
   * Summary: <Actualiza el slogan del team>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnUpdateTeamSlogan(teamId, slogan):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId, slogan)
		cursor.callproc("sp_updateTeamSlogan",params)
		MysqlCnx.commit()
		return ResponseMessages.sus200
	except Exception as exception:
		print("fnUpdateTeamSlogan", exception)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

###################################################END TEAM##################################################

###################################################BILLS STATUS##################################################

'''****************************************************************************
   * Author: CVA
   * Date: 14/06/2021
   * Summary: <Actualizar el status de las bills>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnUpdateBillStatus(billId, teamId, status, value):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (billId, teamId, status, value)
		cursor.callproc("sp_updateBillStatus",params)
		MysqlCnx.commit()
		return ResponseMessages.sus200
	except Exception as exception:
		print("fnUpdateBillStatus", exception)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
   * Author: AJLL
   * Date: 20/07/2021
   * Summary: <obtener el advertising>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnGetAdvertisingBill(teamId, month):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId, month)
		print('fnGetAdvertisingBill', params)
		cursor.callproc("sp_getAdvertisingByTeamIdAndMonth",params)
		jsonRow = cursor.fetchone()
		return {'intResponse': 200, 'Advertising': jsonRow['Advertising']}
	except Exception as exception:
		print("fnUpdateBillStatus", exception)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
   * Author: CVA
   * Date: 14/06/2021
   * Summary: <Obtiene el status de las bills>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnGetBillStatus(teamId):
	try:
		print("fnGetBillStatus",teamId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		cursor.callproc("sp_getBillStatus", [teamId])
		bill = cursor.fetchone()
		return {'intResponse': 200, 'StatusBill': bill}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
   * Author: BPR
   * Date: 21/05/2021
   * Summary: <Actualizar el Wining Team de una Orden>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnUpdateOrderWiningTeam(workshopId, orderId, winingTeam):
	try:
		print("workshopId",workshopId, orderId, winingTeam)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (workshopId, orderId, winingTeam)
		cursor.callproc("sp_updateOrderWiningTeam", params)
		MysqlCnx.commit()
		print("fnUpdateOrderWiningTeam")
		return ({'intResponse': 200, 'strAnswer': 'update order successfully'})
	except Exception as exception:
		print("excepcion update order", exception.args)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})



'''****************************************************************************
   * Author: BPR
   * Date: 24/05/2021
   * Summary: <Actualizar los bid de una Orden>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnUpdateBidById(bidId,bid):
	try:
		print("bidId",bidId, "bid", bid)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (bidId, bid)
		cursor.callproc("sp_updateBidById", params)
		MysqlCnx.commit()
		print("ACTUALIZADA BID")
		return ({'intResponse': 200, 'strAnswer': 'update status successfully'})
	except Exception as exception:
		print("excepcion update team status", exception.args)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})


'''****************************************************************************
   * Author: BPR
   * Date: 26/05/2021
   * Summary: <Eliminar Orders del WorkShop>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnDeleteOrders(workshopID):
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	params = (workshopID)
	cursor.callproc("sp_deleteOrders",[params])
	MysqlCnx.commit()
	return ResponseMessages.sus200


'''****************************************************************************
   * Author: BPR
   * Date: 14/06/2021
   * Summary: <Actualizar el status del open market>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnUpdateOpenMarketByWorkShopId(workshopId,blnOpen):
	try:
		print("fnUpdateOpenMarketByWorkShopId",workshopId,blnOpen)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (workshopId,blnOpen)
		cursor.callproc("sp_updateOpenMarketByWorkShopId", params)
		MysqlCnx.commit()
		print("ACTUALIZADA OPEN MARKET")
		return ({'intResponse': 200, 'strAnswer': 'update status successfully'})
	except Exception as exception:
		print("excepcion update openMarket status", exception.args)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})



'''****************************************************************************
   * Author: BPR
   * Date: 14/06/2021
   * Summary: <Obtiene el status de open market>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnGetOpenMarketByWorkShopId(workShopId):
	try:
		print("fnGetOpenMarketByWorkShopId",workShopId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		cursor.callproc("sp_getOpenMarket", [workShopId])
		jsonOpenMarket = cursor.fetchone()
		print("jsonOpenMarket",jsonOpenMarket)
		blnOpen = False
		if(jsonOpenMarket['OpenMarket'] == 1):
			blnOpen = True
		return {'intResponse': 200, 'openMarket': jsonOpenMarket['OpenMarket']}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
   * Author: DCM
   * Date: 26/07/2021
   * Summary: <Obtiene el rol valida si es CFO>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def getValidationControlRol(userId, TeamId):
	try:
		print("entre getValidationRol ",userId, TeamId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (userId, TeamId)
		cursor.callproc("sp_getValidationControlRol", params)
		jsonResult = cursor.fetchone()
		print("jsonValidarOL",jsonResult)
		r = range(6)
		isFacilitatorAccount = False
		for i in r:
			idAccount = getFacilitatorsUsersId(i)
			isFacilitatorAccount = idAccount == userId
			if(isFacilitatorAccount):
				break
		return {'intResponse': 200, 'IsCFO': jsonResult['IsCFO'], 'memberCount': jsonResult['memberCount'], 'isFacilitatorAccount': isFacilitatorAccount}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})


###################################################END ORDER##################################################

###################################################START IMPROVEMENT##########################################

'''****************************************************************************
   * Author: BPR
   * Date: 25/06/2021
   * Summary: <Obtiene el improvement del team>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnGetImprovementByTeamId(teamId):
	try:
		print("fnGetImprovementByTeamId",teamId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		cursor.callproc("sp_getImprovementById", [teamId])
		jsonImprovement = cursor.fetchone()
		jsonResponse = fnGetImprovementOptionsById(jsonImprovement['ImproveId'])
		if(jsonResponse['intResponse'] == 200):
			jsonImprovement['options'] = jsonResponse['options']
		else:
			jsonImprovement['options'] = []
		print("jsonImprovement",jsonImprovement)
		return {'intResponse': 200, 'improvement': jsonImprovement}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})



'''****************************************************************************
   * Author: BPR
   * Date: 25/06/2021
   * Summary: <Obtiene los improvements del work shop>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnGetImprovementsByWorkShopId(workshopId):
	try:
		print("fnGetImprovementsByWorkShopId",workshopId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		cursor.callproc("sp_getImprovementsById", [workshopId])
		arrImprovement = cursor.fetchall()
		for jsonImprovement in arrImprovement:
			jsonResponse = fnGetImprovementOptionsById(jsonImprovement['ImproveId'])
			if(jsonResponse['intResponse'] == 200):
				jsonImprovement['options'] = jsonResponse['options']
			else:
				jsonImprovement['options'] = []
		print("arrImprovement",arrImprovement)
		return {'intResponse': 200, 'improvements': arrImprovement}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})


'''****************************************************************************
   * Author: DCM
   * Date: 18/08/2021
   * Summary: <Obtiene los improvements de todos los meses 3, 4, 5, 6 del workshop>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnGetgetAllmonthsImprovementsByWorkShopId(workshopId):
	try:
		print("sp_getAllmonthsImprovementsByworkshopsId",workshopId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		cursor.callproc("sp_getAlmonthsImprovementsByworkshopsId", [workshopId])
		arrImprovement = cursor.fetchall()
		return {'intResponse': 200, 'improvements': arrImprovement}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
   * Author: BPR
   * Date: 25/06/2021
   * Summary: <Obtiene los options del improvement>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnGetImprovementOptionsById(ImproveId):
	try:
		print("fnGetImprovementOptionsById",ImproveId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		cursor.callproc("sp_getImproveOptionsById", [ImproveId])
		jsonOptions = cursor.fetchall()
		print("jsonOptions",jsonOptions)
		return {'intResponse': 200, 'options': jsonOptions}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
   * Author: BPR
   * Date: 30/06/2021
   * Summary: <obtener las opciones del improvement de un equipo>
   ****************************************************************************'''

def fnGetImprovementOptionsByTeamId(teamId):
	try:
		print("fnGetImprovementOptionsByTeamId",teamId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (teamId)
		cursor.callproc("sp_getImprovementOptionsByTeamId", [params])
		jsonRow = cursor.fetchall()
		return {'intResponse': 200, 'options': jsonRow}
	except Exception as exception:
		print("exception fnGetImprovementOptionsByTeamId::",exception.args)
		return ({'intResponse': 203, 'strAnswer': exception.args})
'''****************************************************************************
   * Author: BPR
   * Date: 14/06/2021
   * Summary: <Obtiene el status de improvement>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnGetImproveStatusByWorkShopId(workShopId):
	try:
		print("fnGetImproveStatusByWorkShopId",workShopId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		cursor.callproc("sp_getImproveStatus", [workShopId])
		jsonImproveStatus = cursor.fetchone()
		print("jsonImproveStatus",jsonImproveStatus)
		return {'intResponse': 200, 'improveStatus': jsonImproveStatus['ImproveOption']}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

'''****************************************************************************
   * Author: BPR
   * Date: 23/06/2021
   * Summary: <Actualizar el status de Improve en el WorkShop>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnUpdateImproveStatusByWorkShopId(workShopId,improveStatus):
	try:
		print("fnUpdateImproveStatusByWorkShopId",workShopId,improveStatus)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (workShopId,improveStatus)
		cursor.callproc("sp_updateImproveOptionByWorkShopId", params)
		MysqlCnx.commit()
		print("ACTUALIZA IMPROVE OPTION STATUS")
		return ({'intResponse': 200, 'strAnswer': 'update status successfully'})
	except Exception as exception:
		print("excepcion update openMarket status", exception.args)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})


'''****************************************************************************
   * Author: BPR
   * Date: 23/06/2021
   * Summary: <Actualizar el status y option del Improve option>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnUpdateImproveOptionByTeamId(workshopId, improveOptionId,improveOption,improveStatus, month):
	try:
		print("fnUpdateImproveOptionByTeamId",improveOptionId,improveOption,improveStatus, month)
		responseValid = fnValidImprovement(workshopId, improveOption, month)
		if(responseValid['Avalible'] == 0):
			if(responseValid['MaxPerImprove'] == 2):
				return({'intResponse': 203, 'strResponse': "Try again! Two other teams already chose this option before you!"})
			else:
				return({'intResponse': 203, 'strResponse': "Try again! Another team chose this first!"})
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (improveOptionId,improveOption,improveStatus)
		cursor.callproc("sp_updateImprovementOptionById", params)
		MysqlCnx.commit()
		print("before")
		jsonResponse = cursor.fetchone()
		print("jsonResponse",jsonResponse)
		print("ACTUALIZA IMPROVE OPTION STATUS")
		return (jsonResponse)
	except Exception as exception:
		print("excepcion update IMPROVE OPTION STATUS", exception.args)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})



'''****************************************************************************
   * Author: BPR
   * Date: 21/05/2021
   * Summary: <Crea Improvements>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnCreateImprovements(workshopId, arrTeamsId):
	print("fnCreateImprovements",workshopId, arrTeamsId)
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	for teamId in arrTeamsId:
		params = (workshopId, teamId)
		cursor.callproc("sp_createImprovement",params)			
		MysqlCnx.commit()
		jsonImprovement = cursor.fetchone()
		fnCreateImprovementOption(jsonImprovement['ImproveId'])
	print("fnCreateImprovements FIN")
	return ResponseMessages.sus200

'''****************************************************************************
   * Author: BPR
   * Date: 27/06/2021
   * Summary: <Crea Improvement options>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnCreateImprovementOption(improveId):
	print("fnCreateImprovements",improveId)
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	for month in range(3):
		params = (improveId,(month+3))
		cursor.callproc("sp_createImproveOption",params)			
		MysqlCnx.commit()
	print("fnCreateImprovementOption FIN")
	return ResponseMessages.sus200


'''****************************************************************************
   * Author: BPR
   * Date: 26/05/2021
   * Summary: <Eliminar Improvements del WorkShop>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnDeleteImprovements(workshopID):
	MysqlCnx = getConectionMYSQL()
	cursor = MysqlCnx.cursor()
	params = (workshopID)
	cursor.callproc("sp_deleteImprovements",[params])
	MysqlCnx.commit()
	return ResponseMessages.sus200


'''****************************************************************************
   * Author: BPR
   * Date: 28/06/2021
   * Summary: <Actualizar el status de Max Per Improve en el WorkShop>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnUpdateMaxPerImproveByWorkShopId(workShopId,maxPerImprove):
	try:
		print("fnUpdateMaxPerImproveByWorkShopId",workShopId,maxPerImprove)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (workShopId,maxPerImprove)
		cursor.callproc("sp_updateMaxPerImproveById", params)
		MysqlCnx.commit()
		print("ACTUALIZA MAX PER IMPROVE")
		return ({'intResponse': 200, 'strAnswer': 'update status successfully'})
	except Exception as exception:
		print("excepcion fnUpdateMaxPerImproveByWorkShopId", exception.args)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})


'''****************************************************************************
   * Author: BPR
   * Date: 28/06/2021
   * Summary: <Obtiene el max per improvement del workshop>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnGetMaxPerImproveByWorkShopId(workShopId):
	try:
		print("fnGetMaxPerImproveByWorkShopId",workShopId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		cursor.callproc("sp_getMaxPerImprove", [workShopId])
		jsonMaxPerImprove = cursor.fetchone()
		print("jsonMaxPerImprove",jsonMaxPerImprove)
		return {'intResponse': 200, 'MaxPerImprove': jsonMaxPerImprove['MaxPerImprove']}
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})



'''****************************************************************************
   * Author: BPR
   * Date: 23/06/2021
   * Summary: <Actualizar el status de Improve approved>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnUpdateImprovementApprovedById(improveOptionId,improveStatus,approved):
	try:
		print("fnUpdateImprovementApprovedById",improveOptionId,improveStatus,approved)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (improveOptionId,improveStatus,approved)
		cursor.callproc("sp_updateImprovementApproved", params)
		MysqlCnx.commit()
		return ResponseMessages.sus200
	except Exception as exception:
		print("excepcion update IMPROVE APPROVED", exception.args)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})



'''****************************************************************************
   * Author: BPR
   * Date: 28/06/2021
   * Summary: <Valida si se puede seleccionar el improvement>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnValidImprovement(workshopId, improveOption, month):
	try:
		print("fnValidImprovement",workshopId, improveOption, month)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (workshopId, improveOption, month)
		cursor.callproc("sp_validImproveSelection", params)
		jsonValidImprove = cursor.fetchone()
		print("jsonValidImprove",jsonValidImprove)
		aux = -1 if 'MaxPerImprove' not in jsonValidImprove else jsonValidImprove['MaxPerImprove']
		return {'intResponse': 200, 'Avalible': jsonValidImprove['Avalible'], 'MaxPerImprove': aux }
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})



'''****************************************************************************
   * Author: BPR
   * Date: 23/06/2021
   * Summary: <Actualizar el status de Improve option>
   * Edited: <persona que realizó un último cambio>
   * 
   * Summary change: <Descripción del último cambio>
   *
   ****************************************************************************'''
def fnUpdateImproveOptionStatusById(improveOptionId,improveStatus):
	try:
		print("fnUpdateImproveOptionStatusById",improveOptionId,improveStatus)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (improveOptionId,improveStatus)
		cursor.callproc("sp_updateImproveOStatusById", params)
		MysqlCnx.commit()
		return ResponseMessages.sus200
	except Exception as exception:
		print("excepcion fnUpdateImproveOptionStatusById", exception.args)
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})
###################################################END IMPROVEMENT############################################

def upload_file(foto, IdAndNameimg):
	#print("entra upload xd")
	'''image = open('/var/www/html/profiles/' + IdAndNameimg, "wb")
	image.write(foto) 
	image.close()'''

	with open('/var/www/html/profiles/' + IdAndNameimg, "wb") as fh:
		fh.write(base64.b64decode(foto.split(',')[1]))
	#print("termino de guardar photo")
	'''path = os.path.join("/var/www/html/profiles", IdAndNameimg)
	file1.save(path)
	#print("file ok saved")'''
	return ResponseMessages.sus200

def storeLiabilitiesReceivablesUpdates(workshopId, teamId):
	try:
		print("storeLiabilitiesReceivablesUpdates: ", workshopId, teamId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (workshopId, teamId)
		cursor.callproc("sp_storeLiabilitiesReceivablesUpdates", params)
		MysqlCnx.commit()
		jsonData = cursor.fetchone()
		print("jsonData: ", jsonData)
		return {'intResponse': 203 if jsonData is None else 200, 'jsonData': jsonData }
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

def getLiabilitiesReceivablesUpdates(workshopId, teamId):
	try:
		print("getliabilitiesReceivablesUpdates: ", workshopId, teamId)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (workshopId, teamId)
		cursor.callproc("sp_getLiabilitiesReceivablesUpdates", params)
		MysqlCnx.commit()
		jsonData = cursor.fetchone()
		print("jsonData: ", jsonData)
		return {'intResponse': 203 if jsonData is None else 200, 'jsonData': jsonData }
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

def clearLiabilitiesReceivablesUpdates(workshopId, teamId, area):
	try:
		print("clearLiabilitiesReceivablesUpdates: ", workshopId, teamId, area)
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (workshopId, teamId, area)
		cursor.callproc("sp_clearLiabilitiesReceivablesUpdates", params)
		MysqlCnx.commit()
		jsonData = cursor.fetchone()
		print("jsonData: ", jsonData)
		return {'intResponse': 203 if jsonData is None else 200, 'jsonData': jsonData }
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

def updateMarketStep(workshopId, marketStep):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = (workshopId, marketStep)
		cursor.callproc("sp_updateMarketStep", params)
		MysqlCnx.commit()
		jsonData = cursor.fetchone()
		return {'intResponse': 203 if jsonData is None else 200, 'jsonData': jsonData }
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

def getMarketStep(workshopId):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = tuple([workshopId])
		cursor.callproc("sp_getMarketStep", params)
		MysqlCnx.commit()
		jsonData = cursor.fetchone()
		return {'intResponse': 203 if jsonData is None else 200, 'jsonData': jsonData }
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

def storeHistoryMaxSupply(
    workshopId,
    mes,
    teamId,
    maxSupply,
	supply,
):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = tuple([teamId, workshopId, mes, maxSupply, supply])
		cursor.callproc("sp_storeHistoryMaxSupply", params)
		MysqlCnx.commit()
		jsonData = cursor.fetchone()
		return {'intResponse': 203 if jsonData is None else 200, 'jsonData': jsonData }
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})

def getHistoryMaxSupply(
    workshopId,
    mes,
    teamId,
):
	try:
		MysqlCnx = getConectionMYSQL()
		cursor = MysqlCnx.cursor()
		params = tuple([teamId, workshopId, mes])
		cursor.callproc("sp_getHistoryMaxSupply", params)
		jsonData = cursor.fetchone()
		MysqlCnx.commit()
		return {'intResponse': 203 if jsonData is None else 200, 'jsonData': jsonData }
	except Exception as exception:
		return ({'intResponse': 203, 'strAnswer': exception.args[1]})