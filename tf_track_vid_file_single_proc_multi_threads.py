import os
import cv2
import time
import argparse
import multiprocessing
import numpy as np
import tensorflow as tf
import imutils
from imutils.video import VideoStream
import heartbeat
hb = heartbeat.Heartbeat(1024,5,100,"vic.log",10,100)
monitoring_items = ["heart_rate","app_mode"]
comm = heartbeat.DomU(monitoring_items)




from imutils.video import FileVideoStream
from utils.app_utils import FPS, WebcamVideoStream
from multiprocessing import Queue, Pool
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

import threading
from queue import Queue

from tkinter import *
master = Tk()
checked = IntVar(value=0)
previous_checked = checked.get()
c = Checkbutton(master, text="anchors", variable=checked)
c.pack(side=LEFT)

FSIZEs = [
    ("300", 300),
    ("600", 600),
    ("800", 800),
    ("done",0)
]
w1 = IntVar()
w1.set(300) # initialize
previous_f_size = w1.get()
for text, mode in FSIZEs:
    b = Radiobutton(master, text=text,variable=w1, value=mode)
    b.pack(side=LEFT)



ml = Button(master, text="left",command= lambda: move_left(mycam))
ml.pack(side=LEFT)
mr = Button(master,text="right",command= lambda: move_right(mycam))
mr.pack(side=LEFT)


m1 = Scale(master,from_=1,to=20,orient=HORIZONTAL)
m1.set(5)
m1.pack(side=LEFT)

CWD_PATH = os.getcwd()

# Path to frozen detection graph. This is the actual model that is used for the object detection.
MODEL_NAME = 'ssd_mobilenet_v1_coco_11_06_2017'
PATH_TO_CKPT = os.path.join(CWD_PATH, 'object_detection', MODEL_NAME, 'frozen_inference_graph.pb')

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join(CWD_PATH, 'object_detection', 'data', 'mscoco_label_map.pbtxt')


NUM_CLASSES = 90


# Loading label map
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES,
                                                            use_display_name=True)
category_index = label_map_util.create_category_index(categories)




class Workers(threading.Thread):
    def __init__(self,threadLock,every_n_frame,boxes,PATH_TO_CKPT,thread_id,input_q,output_q):
        threading.Thread.__init__(self)
        self.detection_graph = tf.Graph()
        self.thread_id=thread_id
        self.input_q=input_q
        self.output_q=output_q
        self.every_n_frame=every_n_frame
        self.n = every_n_frame['n']
        self.threadLock=threadLock
        self.obj_track=0
        self.boxes=boxes
        t=time.time()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')
            config = tf.ConfigProto(intra_op_parallelism_threads=5, inter_op_parallelism_threads=5, 
                        allow_soft_placement=True, device_count = {'CPU': 1})
            self.sess = tf.Session(graph=self.detection_graph,config=config)
        print('thread create session:',self.thread_id,'[INFO] rate: {:.2f}'.format((time.time() - t)))
    def change_mode(self,num):
        t=time.time()
        config = tf.ConfigProto(intra_op_parallelism_threads=num, inter_op_parallelism_threads=num,allow_soft_placement=True, device_count = {'CPU': 1})
        self.sess = tf.Session(graph=self.detection_graph,config=config)
        print('thread: change session',self.thread_id,'[INFO] rate: {:.2f}'.format((time.time() - t)))

            # self.sess = tf.Session(graph=self.detection_graph)
    def run(self):
        # Acquire lock to synchronize thread
        # self.threadLock.acquire()
        self.work()
        # Release lock for the next thread
        # self.threadLock.release()
        print("Exiting thread" , self.thread_id)
    def work(self):
        def use_prev_boxes(image_np):
            self.threadLock.acquire()

            if len(self.boxes)>0:

                vis_util.visualize_boxes_and_labels_on_image_array(
                    image_np,
                    np.squeeze(self.boxes['boxes']),
                    np.squeeze(self.boxes['classes']).astype(np.int32),
                    np.squeeze(self.boxes['scores']),
                    category_index,
                    use_normalized_coordinates=True,
                    line_thickness=1)
            self.threadLock.release()

            return image_np

        def work_detect_objects(image_np, sess, detection_graph):
            # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
            image_np_expanded = np.expand_dims(image_np, axis=0)
            image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

            # Each box represents a part of the image where a particular object was detected.
            boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

            # Each score represent how level of confidence for each of the objects.
            # Score is shown on the result image, together with the class label.
            scores = detection_graph.get_tensor_by_name('detection_scores:0')
            classes = detection_graph.get_tensor_by_name('detection_classes:0')
            num_detections = detection_graph.get_tensor_by_name('num_detections:0')

            # Actual detection.
            (boxes, scores, classes, num_detections) = sess.run(
                [boxes, scores, classes, num_detections],
                feed_dict={image_tensor: image_np_expanded})

            # Visualization of the results of a detection.
            vis_util.visualize_boxes_and_labels_on_image_array(
                image_np,
                np.squeeze(boxes),
                np.squeeze(classes).astype(np.int32),
                np.squeeze(scores),
                category_index,
                use_normalized_coordinates=True,
                line_thickness=1)
            self.threadLock.acquire()

            self.boxes['boxes']=boxes
            self.boxes['classes']=classes
            self.boxes['scores']=scores
            # for i in range(len(self.boxes['scores'])):
                # self.boxes['scores'][i]=0
            self.threadLock.release()

            return image_np

        while True:
            self.threadLock.acquire()
            # self.every_n_frame['cnt']=(self.every_n_frame['cnt']+1)%self.n
            # self.obj_track = self.every_n_frame['cnt']
            self.n=self.every_n_frame['n']
            self.threadLock.release()
            if self.n==-1:
                self.output_q.put({'cnt':-1})
                break




            stuff=self.input_q.get()
            if stuff['cnt']==-1:
                self.output_q.put({'cnt':-1})
                break
            # self.n = stuff['n']
            self.obj_track = stuff['cnt']
            # print(self.obj_track,self.n,self.obj_track%self.n)

            frame = stuff['blob']
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            t = time.time()
            if self.obj_track%self.n==0:
                # self.output_q.put({'blob':use_prev_boxes(frame_rgb),'cnt':stuff['cnt']})                
                self.output_q.put({'blob':work_detect_objects(frame_rgb, self.sess, self.detection_graph),'cnt':stuff['cnt']})
                print("--------------------thread:",self.thread_id," gonna dnn", "cnt:",self.obj_track,'n:',self.n)

            else:
                self.output_q.put({'blob':use_prev_boxes(frame_rgb),'cnt':stuff['cnt']})                


            # frame = self.input_q.get()
            # frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # t = time.time()
            # if self.obj_track%5==0:
            #     self.output_q.put(work_detect_objects(frame_rgb, self.sess, self.detection_graph))
            # else:
            #     self.output_q.put(frame_rgb)
            # print('thread:',self.thread_id,'[INFO] rate: {:.2f}'.format(1/(time.time() - t)))

        self.sess.close()


# logger = multiprocessing.log_to_stderr()
# logger.setLevel(multiprocessing.SUBDEBUG)


# pool = Pool(args.num_workers, worker, (input_q, output_q))

input_q = Queue()  # fps is better if queue is higher but then more lags
output_q = Queue()
threads = []
every_n_frame = {'cnt':-1,'n':m1.get()}
boxes={}
total_num_threads=1
threadLock = threading.Lock()
for i in range(total_num_threads):
    tmp_thread = Workers(threadLock,every_n_frame,boxes,PATH_TO_CKPT,i,input_q,output_q)
    tmp_thread.start()
    threads.append(tmp_thread)
# video_capture = WebcamVideoStream(src=args.video_source,width=args.width,height=args.height).start()
#video_capture = VideoStream('rtsp://admin:admin@65.114.169.108:88/videoMain').start()
#video_capture = VideoStream('rtsp://arittenbach:8mmhamcgt16!@65.114.169.154:88/videoMain').start()

video_capture = FileVideoStream("walkcat.mp4").start()
time.sleep(2.0)
# outvid = cv2.VideoWriter('outpy_tf_15.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 10, (600,337))
fps = FPS().start()
global_cnt=0
num_threads_exiting=0
cnt=0

while video_capture.more():  # fps._numFrames < 120
# while True:  # fps._numFrames < 120
    current_f_size=w1.get()
    if current_f_size == 0:
        threadLock.acquire()
        every_n_frame['n']=-1
        threadLock.release()
        # while not input_q.empty():
        #     x=input_q.get()
        # input_q.put({'cnt':-1})
    else:
        frame = video_capture.read()
        frame = imutils.resize(frame, width=current_f_size)
        # input_q.put(frame)
        threadLock.acquire()
        every_n_frame['n']=m1.get()
        threadLock.release()
        stuff={'blob':frame,'cnt':cnt,'n':999}
        cnt+=1
        input_q.put(stuff)
    if output_q.empty():
        print('empty ouput queue...')
    else:
        stuff = output_q.get()
        if stuff['cnt']==-1:
            num_threads_exiting+=1
            print('------------global cnt:',global_cnt,'num_threads_exiting',num_threads_exiting)
            if num_threads_exiting==total_num_threads:
                break
            continue
        output_rgb = cv2.cvtColor(stuff['blob'], cv2.COLOR_RGB2BGR)
        # output_rgb = cv2.cvtColor(output_q.get(), cv2.COLOR_RGB2BGR)
        cv2.imshow('Frame',output_rgb )
        global_cnt+=1
        # if global_cnt>50:
        #     outvid.write(output_rgb)

        fps.update()

        master.update_idletasks()
        master.update()
        # hb stuff
        hb.heartbeat_beat()
        window_hr = hb.get_window_heartrate()
        # instant_hr = hb.get_instant_heartrate()
        comm.write("heart_rate",window_hr)
        print('------------------window_hr:',window_hr)
        print('instant_hr:',instant_hr)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    if w1.get()==0:
        break

fps.stop()
print('[INFO] elapsed time (total): {:.2f}'.format(fps.elapsed()))
print('[INFO] approx. FPS: {:.2f}'.format(fps.fps()))
# pool.terminate()
video_capture.stop()
for i in range(total_num_threads):
    input_q.put({'cnt':-1})
# outvid.release()
cv2.destroyAllWindows()
hb.heartbeat_finish()
comm.write("heart_rate","done")
for t in threads:
    t.join()