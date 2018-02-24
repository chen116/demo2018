
def run_demo():

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
		ret, frame = cap.read()
		try:
			g2 = abs(frame-frame2)
		except:
			break

		cv2.imshow('frame',g2)
		frame2=frame
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
		master.update_idletasks()
		master.update()

	# When everything done, release the capture
	cap.release()
	cv2.destroyAllWindows()
#mainloop()
run_demo()