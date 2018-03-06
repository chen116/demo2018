
import heartbeat


# for obj track
import numpy as np
import cv2
from tkinter import *
import numpy.fft as fft
from sys import argv

script, first, second, third, fourth= argv

trials = int(first)
rtds_or_credit = second
busy_or_idle = third
single_or_multi = fourth
print(trials,rtds_or_credit,busy_or_idle,single_or_multi)
# master = Tk()
# w1 = Scale(master,from_=0,to=400)
# w1.set(100)
# w1.pack()
# w2 = Scale(master,from_=0,to=400,orient=HORIZONTAL)
# w2.set(200)
# w2.pack()


for it in range(trials):



	hb = heartbeat.Heartbeat(1024,10,1000,"../logs_demo2018/"+rtds_or_credit+"_"+busy_or_idle+"_"+single_or_multi+"_"+str(it)+".log",10,100)
	monitoring_items = ["heart_rate","app_mode"]

	comm = heartbeat.DomU(monitoring_items)


	cap = cv2.VideoCapture('/root/jellyfish-25-mbps-hd-hevc.avi')
	cap = cv2.VideoCapture('/root/bird.avi')
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
		window_hr = hb.get_window_heartrate()
		if (hb.cnt%10==1):
			comm.write("heart_rate",window_hr)
			comm.write("app_mode","cat"+str(hb.cnt))








	# When everything done, release the capture
	cap.release()
	cv2.destroyAllWindows()
	hb.heartbeat_finish()
	comm.write("heart_rate","done")



 	



