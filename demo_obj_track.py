
def run_demo():
	import numpy as np
	import cv2
	from tkinter import *
	import numpy.fft as fft
	master = Tk()
	w1 = Scale(master,from_=0,to=400)
	w1.set(100)
	w1.pack()
	w2 = Scale(master,from_=0,to=400,orient=HORIZONTAL)
	w2.set(200)
	w2.pack()
	cap = cv2.VideoCapture('/root/drop.avi')
	ret,frame = cap.read()
	frame2 = np.zeros((frame.shape),dtype=frame.dtype)


	while(True):
	    # Capture frame-by-frame
		ret, frame = cap.read()
	#	f2 = np.array(frame)
	#	f2 = f2.astype(np.float32)
	#	f2 = f2+1
	#	f2 = f2/f2.max()
	#	g1h = np.gradient(f2,np.arange(frame.shape[1]),axis=1)
	#	g1v = np.gradient(f2,np.arange(frame.shape[0]),axis=0)
		#g2 = cv2.Canny(frame,w1.get(),w2.get())
	#	g2 = abs(g1h + (1j)*g1v)
		#g2 = cv2.cvtColor(g,cv2.COLORMAP_SUMMER)
		try:
			g2 = abs(frame-frame2)
		except:
			break
	#	g2 = np.log(abs(fft.fftshift(fft.fft2(frame[500:800,500:800]))))
	    # Our operations on the frame come here
		#gray = cv2.cvtColor(g, cv2.COLOR_BGR2RGB)
	#	g2 = abs(frame-frame2)
	    # Display the resulting frame
		cv2.imshow('frame',g2)
		frame2=frame
		#cv2.imshow('f2',frame)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
		master.update_idletasks()
		master.update()

	# When everything done, release the capture
	cap.release()
	cv2.destroyAllWindows()
#mainloop()
run()