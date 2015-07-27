#!flask/bin/python
from app import app
from app import config

@app.route("/")
def main():
    return "hello world!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=config.PORT, debug=config.DEBUG)
