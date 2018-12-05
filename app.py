from flask import Flask, jsonify, abort
from nltk.corpus import words
from enum import Enum
from sympy import *
from sympy.parsing.sympy_parser import parse_expr
from sympy.parsing.sympy_parser import standard_transformations, implicit_multiplication_application
from sympy.plotting import plot3d
from sympy.solvers import solve
from io import BytesIO
from re import finditer

import base64
import re

app = Flask(__name__)

transformations = (standard_transformations + (implicit_multiplication_application,))

class Action(Enum):
    INTEGRATE = 1
    DIFFERENTIATE = 2
    FACTORIZE = 3
    AREA = 4
    PLOT = 5
    THREED = 6
    SOLVE = 7
    SIMPLIFY = 8

possible_actions = {'integrate': Action.INTEGRATE, 'differentiate': Action.DIFFERENTIATE, 'factorize': Action.FACTORIZE, 'factor': Action.FACTORIZE, 'factors': Action.FACTORIZE, 'area': Action.AREA, 'plot': Action.PLOT, '3d': Action.THREED, '3D': Action.THREED, 'derivate': Action.DIFFERENTIATE, 'integral': Action.INTEGRATE, 'solve': Action.SOLVE, 'root': Action.SOLVE, 'roots': Action.SOLVE, 'simplify': Action.SIMPLIFY}

word_set = set(words.words())
to_remove = ['x','y','z']
to_add = ['3D', '3d']

for i in to_remove:
    word_set.remove(i)

for i in to_add:
    word_set.add(i)

@app.route('/api/v1.0/<path:command>', methods=['GET'])
def index(command):
    print("recieved " + command)
    #pattern = "(\d|([A-Z]|[a-z]))[a-z]"
    pattern = "(\d|([A-Z]|[a-z]))[a-z][\ \+\-\/\*\^]"
    tokenized_equation = command.split(" ")
    expression = ""
    for i in tokenized_equation:
        if i not in word_set:
            expression += i
    expression += " "
    print("expression is " + expression)
    mult_loc = []
    for match in finditer(pattern, expression):
        mult_loc.append(match.span()[1] - 2)

    offset = 0
    for i in mult_loc:
        i += offset # to account for the fact that one character is added to the array
        offset += 1
        expression = expression[:i] + "*" + expression[i:]
    expression = expression.replace("^", "**")
    print("cleaned expression is " + expression)

    s = parse_expr(expression)

    todo = []
    for i in tokenized_equation:
        print("scanning " + i)
        if i in possible_actions:
            print("yes " + i)
            todo.append(possible_actions[i])

    response = ""
    image = ""
    x = symbols('x')
    y = symbols('y')
    z = symbols('z')
    if Action.INTEGRATE in todo:
        response = latex(integrate(s, x))
    if Action.DIFFERENTIATE in todo:
        response = latex(diff(s,x))
    if Action.PLOT in todo:
        if Action.THREED in todo:
            print("doing 3d")
            graph = plot3d(s, show=False)
        else:
            graph = plot(s, show=False)
        ramfile = BytesIO()
        graph.save(ramfile)
        ramfile.seek(0)
        image = base64.b64encode(ramfile.getvalue()).decode('ascii')
    if Action.SOLVE in todo:
        response = latex(solve(expression))
    if Action.SIMPLIFY in todo:
        response = latex(simplify(expression))
    if Action.FACTORIZE in todo:
        response = latex(factor(expression))


    return jsonify({'expression': expression, 'solution': response, 'plot': image})

if __name__ == '__main__':
    app.run(debug=True)
