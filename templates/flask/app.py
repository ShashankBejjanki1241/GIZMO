from flask import Flask, jsonify, request

app = Flask(__name__)

@app.get('/')
def root():
    return jsonify({"message": "Hello World"})

# Intentionally missing /sum to make tests fail; agents should add it

if __name__ == '__main__':
    app.run(debug=True)
