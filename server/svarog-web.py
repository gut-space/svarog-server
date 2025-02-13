#!/usr/bin/env python3
from app import app

app.config['SECRET_KEY'] = 'the earth is flat'

DEBUG = False

if __name__ == '__main__':
    app.run(debug=DEBUG, port=8080)
