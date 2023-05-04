import cv2
import numpy as np
from JetbotYolo.elements.yolo import OBJ_DETECTION
from multiprocessing import Process
from DetectableObject import DetectableObject
import pandas as pd

class JetbotYolo:

    process = None


    def __init__(self, modelpath, trt=False):
        print("init JetsonYoloTest")
        self.nearest_object = DetectableObject()
        self.detected_objects = dict()
        self.filtered_objects = dict()
        self.Object_colors = list(np.random.rand(80,3)*255)

        self.Object_classes = ['sign_forbidden', 'sign_limit', 'sign_nolimit', 'sign_stop', 'kreuzung' ]

        self.Object_detector = OBJ_DETECTION(modelpath, self.Object_classes, trt)
        #self.init_detection()


    def gstreamer_pipeline(
            self,
            capture_width=1280,
            capture_height=720,
            display_width=1280,
            display_height=720,
            framerate=60,
            flip_method=0,
    ):
        return (
            "nvarguscamerasrc ! "
            "video/x-raw(memory:NVMM), "
            "width=(int)%d, height=(int)%d, "
            "format=(string)NV12, framerate=(fraction)%d/1 ! "
            "nvvidconv flip-method=%d ! "
            "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
            "videoconvert ! "
            "video/x-raw, format=(string)BGR ! appsink"
            % (
                capture_width,
                capture_height,
                framerate,
                flip_method,
                display_width,
                display_height,
            )
        )

    def init_detection(self):
        print("init detection")
        # To flip the image, modify the flip_method parameter (0 and 2 are the most common)
        #print(gstreamer_pipeline(flip_method=0))
        self._cap = cv2.VideoCapture(self.gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
        if self._cap.isOpened():
            print("init detection complete")
        else:
            print("Unable to open camera")
    #cv2.destroyAllWindows()

    def run_detection(self, frame):
        print("run detection")

        # detection process
        objs = self.Object_detector.detect(frame)

        try:
            if objs[0] is not None:
                print(objs[0]['bbox'[1][1]])
        except:
            print("currently no objects available")

        self.filter_nearest_object_of_each_type(objs)

        # plotting
        for obj in objs:
            print("now: ")
            print(obj)
            label = obj['label']
            score = obj['score']
            [(xmin,ymin),(xmax,ymax)] = obj['bbox']
            color = self.Object_colors[self.Object_classes.index(label)]
            frame = cv2.rectangle(frame, (xmin,ymin), (xmax,ymax), color, 2)
            frame = cv2.putText(frame, f'{label} ({str(score)})', (xmin,ymin), cv2.FONT_HERSHEY_SIMPLEX , 0.75, color, 1, cv2.LINE_AA)

            current_object = DetectableObject(obj['label'], xmin, ymin, xmax, ymax, obj['score'])
            self.detected_objects[obj["label"]] = current_object
            #self.detect_Nearest_object(current_object)

    def run_detection_only(self, frame):
        #print("run detection - only")

        # detection process
        objs = self.Object_detector.detect(frame)

        self.filter_nearest_object_of_each_type(objs)
        self.detect_Nearest_object()

        for obj in objs:
            [(xmin,ymin),(xmax,ymax)] = obj['bbox']
            current_object = DetectableObject(obj['label'], xmin, ymin, xmax, ymax, obj['score'])
            self.detected_objects[obj["label"]] = current_object


    def detect_Nearest_object(self):
        nearest = None
        for key in self.filtered_objects:
            if self.filtered_objects[key] is not None:
                if nearest is None or (self.filtered_objects[key].get_ymax() > nearest.get_ymax()): 
                    nearest = self.filtered_objects[key]
        self.nearest_object = nearest

    def filter_nearest_object_of_each_type(self, objects):
        forbidden_signs = list()
        limit_signs = list()
        nolimit_signs = list()
        stop_signs = list()
        kreuzungen = list()

        for obj in objects:
            #if obj['label'] == 'sign_forbidden':
                #forbidden_signs.append(obj)
            if obj['label'] == 'sign_limit':
                limit_signs.append(obj)
            elif obj['label'] == 'sign_nolimit':
                nolimit_signs.append(obj)
            elif obj['label'] == 'sign_stop':
                stop_signs.append(obj)
            #else:
                #kreuzungen.append(obj)

        nearest_f = self.compare_and_get_nearest(forbidden_signs) # bleibt bei uns None
        nearest_l = self.compare_and_get_nearest(limit_signs)
        nearest_nl = self.compare_and_get_nearest(nolimit_signs)
        nearest_s = self.compare_and_get_nearest(stop_signs)
        nearest_k = self.compare_and_get_nearest(kreuzungen) # bleibt bei uns None

        if nearest_f is not None:
            f_object = DetectableObject(nearest_f['label'], nearest_f['xmin'], nearest_f['ymin'], nearest_f['xmax'], nearest_f['ymax'], nearest_f['score'])
        else:
            f_object = None

        if nearest_l is not None:
            l_object = DetectableObject(nearest_l['label'], nearest_l['xmin'], nearest_l['ymin'], nearest_l['xmax'], nearest_l['ymax'], nearest_l['score'])
        else:
            l_object = None

        if nearest_nl is not None:
            nl_object = DetectableObject(nearest_nl['label'], nearest_nl['xmin'], nearest_nl['ymin'], nearest_nl['xmax'], nearest_nl['ymax'], nearest_nl['score'])
        else:
            nl_object = None

        if nearest_s is not None:
            s_object = DetectableObject(nearest_s['label'], nearest_s['xmin'], nearest_s['ymin'], nearest_s['xmax'], nearest_s['ymax'], nearest_s['score'])
        else:
            s_object = None
            
        if nearest_k is not None:
            k_object = DetectableObject(nearest_k['label'], nearest_k['xmin'], nearest_k['ymin'], nearest_k['xmax'], nearest_k['ymax'], nearest_k['score'])
        else:
            k_object = None

        # ['sign_forbidden', 'sign_limit', 'sign_nolimit', 'sign_stop', 'kreuzung']
        self.filtered_objects = {'sign_forbidden': f_object,
                                 'sign_limit': l_object,
                                 'sign_nolimit': nl_object,
                                 'sign_stop': s_object,
                                 'kreuzung': k_object}

        #print("LOOK HERE: ")
        #for v in list(self.filtered_objects.values()):
            #if v is not None:
                #print(v.get_type())



    def compare_and_get_nearest(self, signs):
        result = None
        for s in signs:
            if result is None:
                result = s
            else:
                if s['ymax'] > result['ymax']:
                    result = s

        return result


    #GETTERS

    #Get one detected Object of each type
    #that is the nearest one
    def get_filtered_objects(self):
        return self.filtered_objects

    #Get the nearest detected object
    def get_nearest_object(self):
        return self.nearest_object

    #Get all detected objects
    def get_detected_objects(self):
        return self.detected_objects

    #Get the camera stream of yolo to
    #get a preview of which objects are detected
    def get_camera_stream(self):
        return self._cap.read()

