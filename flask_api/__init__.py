import json

from flask import Flask, request, jsonify, make_response

from flask_api import banana_vgg

app = Flask(__name__)


@app.route('/hello_world')  # test api
def hello_world():
    return 'Hello, World!'


@app.route('/echo_call/<param>')  # get echo api
def get_echo_call(param):
    return jsonify({"param": param})


@app.route('/echo_call', methods=['POST'])  # post echo api
def post_echo_call():
    param = request.get_json()
    return jsonify(param)


@app.route('/ai_smart_factory', methods=['POST'])
def ai_smart_factory():
    request_img = request.files['request_img']
    request_img_name = request_img.filename
    print(request_img_name)

    result = banana_vgg.predict(request_img, request_img_name)

    response = json.dumps(result, ensure_ascii=False, indent="\t")

    return response, 200


# if __name__ == "__main__":
#     app.run()
