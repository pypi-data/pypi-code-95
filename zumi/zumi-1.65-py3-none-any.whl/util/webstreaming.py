from zumi.util.webcamutil import Webcamutil
from flask import Response
from flask import Flask
from flask import render_template
import threading
import argparse
import datetime
import imutils
import time
import cv2


# initialize a flask object
app = Flask(__name__, static_url_path="", static_folder="templates")

# initialize the video stream and allow the camera sensor to
# warmup
#vs = VideoStream(usePiCamera=1).start()
#vs = VideoStream(src=0).start()
camera = Webcamutil(auto_start=True)
time.sleep(2.0)

@app.route("/ml")
def index():
	# return the rendered template
	# return render_template("index.html")
        return app.send_static_file('index.html')
		
def generate(camera):
	# grab global references to the output frame and lock variables

	# loop over frames from the output stream
	while True:
		# wait until the lock is acquired
	
			# check if the output frame is available, otherwise skip
			# the iteration of the loop
		frame = camera.capture()
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		#frame = imutils.resize(frame, width=400)

			# encode the frame in JPEG format
		(flag, encodedImage) = cv2.imencode(".jpg", frame)

			# ensure the frame was successfully encoded
		if not flag:
			continue

		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	response = Response(generate(camera),
		mimetype = "multipart/x-mixed-replace; boundary=frame")
	response.headers.add("Access-Control-Allow-Origin", "*")
	return response

# check to see if this is the main thread of execution
if __name__ == '__main__':
	# construct the argument parser and parse command line arguments
	# ap = argparse.ArgumentParser()
	# ap.add_argument("-i", "--ip", type=str, required=True,
	# 	help="ip address of the device")
	# ap.add_argument("-o", "--port", type=int, required=True,
	# 	help="ephemeral port number of the server (1024 to 65535)")
	# ap.add_argument("-f", "--frame-count", type=int, default=32,
	# 	help="# of frames used to construct the background model")
	# args = vars(ap.parse_args())

	# start a thread that will perform motion detection
	#t = threading.Thread(target=detect_motion, args=(
	#	args["frame_count"],))
	#t.daemon = True
	#t.start()

	# start the flask app
	app.run(host='0.0.0.0', port=9696, debug=True, use_reloader=False)

# release the video stream pointer
camera.close()