from http.server import BaseHTTPRequestHandler
from prisma import Prisma
import json

prisma = Prisma()

class handler(BaseHTTPRequestHandler):
    async def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))

        await prisma.connect()
        
        try:
            testresult = await prisma.testresult.create({
                "data": {
                    "username": data.get('username', ''),
                    "userId": data.get('userId', ''),
                    "score": data.get('score', 0),
                    "livesLeft": data.get('livesLeft', 0)
                }
            })
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"message": testresult}).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        finally:
            await prisma.disconnect()