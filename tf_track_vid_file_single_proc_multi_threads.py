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

MODES = [
    ("600", 600),
    ("800", 800),
    ("1000", 1000),
    ("done",0)
]
w1 = IntVar()
w1.set(600) # initialize
previous_f_size = w1.get()
for text, mode in MODES:
    b = Radiobutton(master, text=text,variable=w1, value=mode)
    b.pack(side=LEFT)
ml = Button(master, text="left",command= lambda: move_left(mycam))
ml.pack(side=LEFT)
mr = Button(master,text="right",command= lambda: move_right(mycam))
mr.pack(side=LEFT)

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
    def __init__(self,threadLock,every_n_frame,PATH_TO_CKPT,thread_id,input_q,output_q):
        threading.Thread.__init__(self)
        self.detection_graph = tf.Graph()
        self.thread_id=thread_id
        self.input_q=input_q
        self.output_q=output_q
        self.every_n_frame=every_n_frame
        self.threadLock=threadLock
        self.obj_track=0
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')
            config = tf.ConfigProto(intra_op_parallelism_threads=5, inter_op_parallelism_threads=5, 
                        allow_soft_placement=True, device_count = {'CPU': 1})
            self.sess = tf.Session(graph=self.detection_graph,config=config)
            # self.sess = tf.Session(graph=self.detection_graph)
    def run(self):
        # Acquire lock to synchronize thread
        # self.threadLock.acquire()
        self.work()
        # Release lock for the next thread
        # self.threadLock.release()
        print("Exiting thread" , self.thread_id)
    def work(self):
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
            return image_np
        while True:
            self.threadLock.acquire()
            self.every_n_frame['cnt']=(self.every_n_frame['cnt']+1)%5
            self.obj_track = self.every_n_frame['cnt']
            self.threadLock.release()

            frame = self.input_q.get()
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            t = time.time()
            if self.obj_track%5==0:
                self.output_q.put(work_detect_objects(frame_rgb, self.sess, self.detection_graph))
            else:
                self.output_q.put(frame_rgb)
            print('thread:',self.thread_id,'[INFO] elapsed time: {:.2f}'.format(1/(time.time() - t)))


        self.sess.close()








if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-src', '--source', dest='video_source', type=int,
                        default=0, help='Device index of the camera.')
    parser.add_argument('-wd', '--width', dest='width', type=int,
                        default=200, help='Width of the frames in the video stream.')
    parser.add_argument('-ht', '--height', dest='height', type=int,
                        default=200, help='Height of the frames in the video stream.')
    parser.add_argument('-num-w', '--num-workers', dest='num_workers', type=int,
                        default=1, help='Number of workers.')
    parser.add_argument('-q-size', '--queue-size', dest='queue_size', type=int,
                        default=15, help='Size of the queue.')
    args = parser.parse_args()

    # logger = multiprocessing.log_to_stderr()
    # logger.setLevel(multiprocessing.SUBDEBUG)


    # pool = Pool(args.num_workers, worker, (input_q, output_q))

    input_q = Queue()  # fps is better if queue is higher but then more lags
    output_q = Queue()
    threads = []
    every_n_frame = {'cnt':-1}
    threadLock = threading.Lock()
    for i in range(4):
        tmp_thread = Workers(threadLock,every_n_frame,PATH_TO_CKPT,i,input_q,output_q)
        tmp_thread.start()
        threads.append(tmp_thread)
    # video_capture = WebcamVideoStream(src=args.video_source,width=args.width,height=args.height).start()
    video_capture = VideoStream('rtsp://admin:admin@65.114.169.108:88/videoMain').start()
    # video_capture = VideoStream('rtsp://arittenbach:8mmhamcgt16!@65.114.169.154:88/videoMain').start()

    # video_capture = FileVideoStream("walkcat.mp4").start()
    time.sleep(2.0)

    fps = FPS().start()


    #while video_capture.more():  # fps._numFrames < 120
    while True:  # fps._numFrames < 120
        current_f_size=w1.get()
        if current_f_size == 0:
            break
        frame = video_capture.read()
        frame = imutils.resize(frame, width=current_f_size)

        input_q.put(frame)
        if output_q.empty():
            print('empty ouput queue...')
        else:

            output_rgb = cv2.cvtColor(output_q.get(), cv2.COLOR_RGB2BGR)
            cv2.imshow('Frame',output_rgb )
            fps.update()

            master.update_idletasks()
            master.update()
            # hb stuff
            hb.heartbeat_beat()
            window_hr = hb.get_window_heartrate()
            instant_hr = hb.get_instant_heartrate()
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
    cv2.destroyAllWindows()
    hb.heartbeat_finish()
    comm.write("heart_rate","done")
    for t in threads:
        t.join()