import os
import traitlets
import ipywidgets
from jetbot import Camera, bgr8_to_jpeg
from multiprocessing import Process
from uuid import uuid1



class AutomaticDataCollector:

    camera = None
    frame_counter = 0
    secondscounter = 0
    image_widget = None
    p1 = None
    waittime = 5

### INIT ###

    def __init__(self, wait_time, camerauebergeben):
        AutomaticDataCollector.waittime = wait_time
        AutomaticDataCollector.camera = camerauebergeben
        self.wait_time = wait_time
        self.__init_controller()
        self.__init_camera()
        self.__init_directories()

    def __init_controller(self):
        print("init controller")

    def __init_camera(self):
        #AutomaticDataCollector.camera = Camera()
        AutomaticDataCollector.image_widget = ipywidgets.Image()
        traitlets.dlink((AutomaticDataCollector.camera, 'value'),(AutomaticDataCollector.image_widget, 'value'), transform=bgr8_to_jpeg)
        print("init camera")

    def __init_directories(self):
        try:
            os.makedirs("dataset/collection")
        except FileExistsError:
            print('Directories not created because they already exist')

        print("init directories")



### PUBLIC ###
    def start(self):
        AutomaticDataCollector.p1 = Process(target=self.__start_observer())
        AutomaticDataCollector.p1.start()

    def stop(self):
        AutomaticDataCollector.p1.stop()
        print("stop")

### ACTION ###
    def __handle_take_image_after_wait_time(self, sec):
        AutomaticDataCollector.frame_counter += 1
        print(AutomaticDataCollector.frame_counter)
        if AutomaticDataCollector.frame_counter % AutomaticDataCollector.camera.fps == 0:
            AutomaticDataCollector.frame_counter = 0
            AutomaticDataCollector.secondscounter += 1
            if AutomaticDataCollector.secondscounter == sec:
                AutomaticDataCollector.secondscounter = 0
                print("take image now")
                self.__take_image()
        print("handle")

    def __take_image(self):
        image_path = os.path.join('dataset/collection', str(uuid1()) + '.jpg')
        with open(image_path, 'wb') as f:
            f.write(AutomaticDataCollector.image_widget.value)
        print("image taken")


    def __start_observer(self):
        AutomaticDataCollector.camera.observe(lambda change: self.__handle_take_image_after_wait_time(AutomaticDataCollector.waittime), names='value')
        print("Observer started")


