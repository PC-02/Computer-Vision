from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=100, help="minimum area size")
args = vars(ap.parse_args())


if args.get("video", None) is None:
	vs = VideoStream(src=0).start()
	print("[INFO] Warming up...")
	time.sleep(2.5)

else:
	vs = cv2.VideoCapture(args["video"])

avg = None

while True:
	
	frame = vs.read()
	frame = frame if args.get("video", None) is None else frame[1]
	text = "Unoccpuied"

	if frame is None:
		break

	frame = imutils.resize(frame, width=500)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21,21), 0)

	if avg is None:
		print("[INFO] Starting background model...")
		avg = gray.copy().astype("float")
		continue

	cv2.accumulateWeighted(gray, avg, 0.5)
	currFrame = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

	thresh = cv2.threshold(currFrame, 10, 255, cv2.THRESH_BINARY)[1]
	thresh = cv2.dilate(thresh, None, iterations=2)

	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
	 cv2.CHAIN_APPROX_SIMPLE)

	cnts = imutils.grab_contours(cnts)

	for c in cnts:
		if cv2.contourArea(c) < args["min_area"]:
			continue

		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
		text = "Occupied"

	cv2.putText(frame, "Root Status: {}".format(text), (10,20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255),2)
	
	cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
		(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)	

	cv2.imshow("Security Feed", frame)
	cv2.imshow("Thresh", thresh)
	cv2.imshow("Current Frame", currFrame)

	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

vs.stop() if args.get("video", None) is None else vs.release()
cv2.destroyAllWindows()