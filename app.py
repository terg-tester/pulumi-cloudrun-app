from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello_world():
    message = os.environ.get('MESSAGE', 'Hello from Cloud Run!')
    return f'<h1>{message}</h1>'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
