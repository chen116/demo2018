
import heartbeat
import xencomm

# for obj track
import numpy as np
import cv2
from tkinter import *
import numpy.fft as fft



# master = Tk()
# w1 = Scale(master,from_=0,to=400)
# w1.set(100)
# w1.pack()
# w2 = Scale(master,from_=0,to=400,orient=HORIZONTAL)
# w2.set(200)
# w2.pack()

hb = heartbeat.Heartbeat(1024,10,1000,"vic.log",10,100)
comm = xencomm.DomU(["heart_rate"])


cap = cv2.VideoCapture('/root/jellyfish-25-mbps-hd-hevc.avi')
ret,frame = cap.read()
frame2 = np.zeros((frame.shape),dtype=frame.dtype)



while(True):
	ret, frame = cap.read()
	try:
		g2 = abs(frame-frame2)
	except:
		break
	# cv2.imshow('frame',g2)
	frame2=frame
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
	# master.update_idletasks()
	# master.update()
	hb.heartbeat_beat()
	hr = hb.get_instant_heartrate()
	comm.write("heart_rate",hr)








# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
hb.heartbeat_finish()
comm.write("heart_rate","q")



 	



