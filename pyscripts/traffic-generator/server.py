import json
from random import randint
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

PORT = 8000

class SimpleServerHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type','text/html')
		self.end_headers()
		
		# generate random data to send
		data = {
			'name': 'server',
			'randomkey': str(randint(0,20)),
			'array': [i for i in range(randint(0, 1000))]
		}
		
		self.wfile.write(json.dumps(data))

if __name__ == "__main__":
	try:
		server = HTTPServer(('', PORT), SimpleServerHandler)
		print 'Started httpserver on port', PORT
		server.serve_forever()
	except KeyboardInterrupt:
		print ' received, shutting down...'
		server.socket.close()