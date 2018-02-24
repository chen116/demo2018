
import heartbeat
import hostcomm

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
cap = cv2.VideoCapture('/root/bird.avi')
ret,frame = cap.read()
frame2 = np.zeros((frame.shape),dtype=frame.dtype)

hb = heartbeat.Heartbeat(1024, 10,1000,"vic.log",10,100)
hc = hostcomm.HostComm("10.1.1.3",5000)

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
	inst_hr = hb.get_instant_heartrate()
	hc.send2host(inst_hr,10000)







	# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
hb.heartbeat_finish()


 	



