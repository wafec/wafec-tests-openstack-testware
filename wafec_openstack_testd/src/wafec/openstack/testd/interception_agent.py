from flask import Flask, jsonify, request

from .interception_agent_model import Interception, new_session
from ._configuration import interception_config

__all__ = [
    'start_agent_server'
]

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return jsonify({'message': 'Hello World!'})


@app.route('/api/interception', methods=['POST'])
def interception_post():
    ps = request.json['ps']
    name = request.json['name']
    x = request.json['x']
    trace = request.json['trace']
    session = None
    try:
        session = new_session()
        interception = Interception.of(ps=ps, name=name, x=x, trace=trace)
        session.add(interception)
        session.commit()
        return jsonify({'message': 'Interception added successfully', 'id': interception.id})
    finally:
        if session:
            session.close()


def start_agent_server():
    app.run(host='0.0.0.0', port=interception_config.port)


if __name__ == '__main__':
    start_agent_server()
