#pip install gunicorn gunicorn[gevent] gevent-websocket

#gunicorn
wsgi_app = 'DirectionsIO:app'
bind = ':6007'

#ssl
keyfile = '/etc/letsencrypt/live/app.income-outcome.com/privkey.pem'
certfile = '/etc/letsencrypt/live/app.income-outcome.com/cert.pem'
ca_certs = '/etc/letsencrypt/live/app.income-outcome.com/chain.pem'
#ssl_version = ''

#socket.io
workers = 1
worker_class = 'geventwebsocket.gunicorn.workers.GeventWebSocketWorker' 