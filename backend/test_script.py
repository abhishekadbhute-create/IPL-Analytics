import sys, os
sys.path.append(r'c:\Users\Abhishek Adbhute\OneDrive\Desktop\IPL analysis\IPL_ANALYTICS\backend')
from routes.search_routes import search_bp, get_gemini_client
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv(r'c:\Users\Abhishek Adbhute\OneDrive\Desktop\IPL analysis\IPL_ANALYTICS\backend\.env')

app = Flask(__name__)
app.register_blueprint(search_bp, url_prefix='/api')

with app.test_client() as c:
    rv = c.post('/api/chat', json={'query': 'What is the highest score of RCB?'})
    print('Status Code:', rv.status_code)
    print('Response:', rv.get_json())
