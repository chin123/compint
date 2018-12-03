from flask import Flask, jsonify, abort
from nltk.corpus import words
from enum import Enum
from sympy import *
from sympy.parsing.sympy_parser import parse_expr
from sympy.parsing.sympy_parser import standard_transformations, implicit_multiplication_application
from io import BytesIO
import base64

app = Flask(__name__)

transformations = (standard_transformations + (implicit_multiplication_application,))

class Action(Enum):
    INTEGRATE = 1
    DIFFERENTIATE = 2
    FACTORIZE = 3
    AREA = 4
    PLOT = 5

possible_actions = {'integrate': Action.INTEGRATE, 'differentiate': Action.DIFFERENTIATE, 'factorize': Action.FACTORIZE, 'area': Action.AREA, 'plot': Action.PLOT}

@app.route('/api/v1.0/<string:command>', methods=['GET'])
def index(command):
    word_set = set(words.words())
    tokenized_equation = command.split(" ")
    expression = ""
    for i in tokenized_equation:
        if i not in word_set:
            expression += i

    s = parse_expr(expression)

    todo = Action.INTEGRATE
    for i in tokenized_equation:
        if i in possible_actions:
            todo = possible_actions[i]
            break

    response = ""
    image = ""
    x = symbols('x')
    y = symbols('y')
    z = symbols('z')
    if todo == Action.INTEGRATE:
        response = latex(integrate(s, x))
    if todo == Action.DIFFERENTIATE:
        response = latex(diff(s,x))
    if todo == Action.PLOT:
        graph = plot(s, show=False)
        ramfile = BytesIO()
        graph.save(ramfile)
        ramfile.seek(0)
        image = base64.b64encode(ramfile.getvalue()).decode('ascii')


    return jsonify({'expression': expression, 'solution': response, 'plot': image})

if __name__ == '__main__':
    app.run(debug=True)
