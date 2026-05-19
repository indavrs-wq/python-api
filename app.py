from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Python API Working"


@app.route('/process', methods=['POST'])
def process():

    data = request.json

    name = data.get("name", "")

    result = {
        "success": True,
        "message": f"Hello {name} from Python"
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)