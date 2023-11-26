import jwt

import datetime
from datetime import date, timedelta
import time

def fnCreateSession(strIdUsuario, strIdOrganizacion, blnAsociado=False):
	try:
		dteToday = datetime.datetime.today()
		dteExpire = dteToday + datetime.timedelta(days=500)
		dteToday = time.mktime(dteToday.timetuple())
		dteExpire = time.mktime(dteExpire.timetuple())
		if(blnAsociado==True):
			jsnData = {'strIdAsociado':str(strIdUsuario), 'strIdEmpresa':strIdOrganizacion, 'iat': dteToday,'exp': dteExpire}	
		else:
			jsnData = {'strIdUsuario':str(strIdUsuario), 'strIdOrganizacion':strIdOrganizacion, 'iat': dteToday,'exp': dteExpire}
		encoded = jwt.encode(jsnData, 'secret', algorithm='HS256')
		strToken = encoded.decode("utf-8")
		return {'intResponse':200,'strAnswer':'Sesión Creada','strToken': strToken,'strIdUsuario':strIdUsuario}
	except Exception as e:
		return {"intResponse":500,"strAnswer":"Error en servidor"}

if __name__ == "__main__":
    print(fnCreateSession('master@hotmail.com', 'master'))
