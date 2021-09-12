from flask import Flask, render_template, request
from mypycustomcalculator.mycalculator import Calculator
import webbrowser
from threading import Timer

app = Flask(__name__)

EXPLAIN_TEMPLATE_LOADING = True

@app.route("/", methods=["GET", "POST"])  # To render Homepage
def home_page():
    return render_template("index.html")


@app.route("/math", methods=["POST"])  # This will be called from UI
def math_operation():
    if request.method == "POST":
        operation = request.form["operation"]
        num1 = int(request.form["num1"])
        num2 = int(request.form["num2"])
        calc = Calculator(num1, num2)
        result=""
        if operation == "add":
            r = calc.add()
            result = "the sum of " + str(num1) + " and " + str(num2) + " is " + str(r)
        if operation == "subtract":
            r = calc.subtract()
            result = (
                    "the difference of " + str(num1) + " and " + str(num2) + " is " + str(r)
            )
        if operation == "multiply":
            r = calc.multiply()
            result = (
                    "the product of " + str(num1) + " and " + str(num2) + " is " + str(r)
            )
        if operation == "divide":
            r = calc.divide()
            result = (
                    "the quotient when "
                    + str(num1)
                    + " is divided by "
                    + str(num2)
                    + " is "
                    + str(r)
            )
        return render_template("results.html", result=result)


def open_browser():
    webbrowser.open_new('http://127.0.0.1:8080/')


def start_app():
    Timer(1, open_browser).start()
    app.run(host="127.0.0.1", port=8080,debug=True)


if __name__ == "__main__":
    start_app()
