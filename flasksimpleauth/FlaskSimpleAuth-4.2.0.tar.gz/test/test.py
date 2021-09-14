from flask import Flask, request
app = Flask(__name__)

@app.get("/test")
def get_test():
	res = f"args: {request.args}\nform: {request.form}\nvalues: {dict(request.values)}\n"
	return res, 200

@app.post("/test")
def post_test():
	res = f"args: {request.args}\nform: {request.form}\nvalues: {dict(request.values)}\n"
	return res, 200
