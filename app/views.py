from app import app


@app.route("/")
def main():
    return "hello world!"
