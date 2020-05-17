from client import Client
from flask import Flask, request

app = Flask(__name__,
            static_url_path='',
            static_folder='static')

client = Client(5, 10001)


@app.route('/')
def main():
    return app.send_static_file('index.html')


@app.route('/msg', methods=['post'])
def message():
    _, data = client.connectandsend(request.form['host'], request.form['port'], request.form['type'], request.form['data'])[0]

    return data


if __name__ == '__main__':
    app.run(debug=True)
