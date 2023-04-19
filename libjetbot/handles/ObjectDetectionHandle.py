from JetsonYoloNew import DetectableObject
from JetsonYoloNew.JetbotYolo import *
from torch import Tensor

from libjetbot.ExtendedRobot import ReturnData, Handle, ReturnCommand, State


class ObjectDetectionHandle(Handle):
    threshold_xmax = 120
    threshold_ymax = 40

    threshold_frames_stop = 30 #nach 30 frames is_stopped auf False setzen
    threshold_frames_beforeStop = 10 #nach 10 frames is_preparing_to_stop auf False setzen


    def __init__(self, path):
        self.yolo = JetbotYolo(path)
        self._model = None

    def execute(self, image, tensor: Tensor, previous_values: list, state: State) -> ReturnData:
        # invoke method to get classes
        self.yolo.run_detection_only(image)
        detected = self.yolo.get_filtered_objects()
        detected = self.getTotalNearestObject(detected)

        # handle detected objects and return command & poi
        return self.__process_class__(detected, state)

    def __process_class__(self, obj: DetectableObject, state: State) -> ReturnData:
        if obj is None:
            return ReturnData(ReturnCommand.CONTINUE)
        else:
            if obj.get_probability() > 0.3 and obj.get_xmax() > threshold_xmax and obj.get_ymax() > threshold_ymax:
                if obj.get_type() == 'sign_stop':
                    #@todo nach 10 Frames für 30 Frames stoppen
                    #return ReturnData(ReturnCommand.STOP)
                    pass
                elif obj.get_type() == 'sign_limit':
                    #@todo max_speed auf 0.11 setzen
                    #return self.handle_limit_sign(sign, state)
                    pass
                elif obj.get_type() == 'no_limit':
                    #@todo max_speed auf 0.15 setzen
                    #return self.handle_nolimit_sign(sign, state) 
                    pass
    
    # Da bei uns nur NoLimit, Limit und Stop verarbeitet werden und diese 3 Schilder sich widersprechen, nur das mit höchstem ymax behandeln
    def getTotalNearestObject(self, detected_objects: dict[DetectableObject]) -> DetectableObject:
        obj = next(iter(detected_objects)) #first object
        for sign in detected_objects:
            if sign.get_ymax() > obj.get_ymax():
                obj = sign
        return obj
  
    '''
    # Class to handle signs detected previously
    def handle_limit_sign(self, sign, state):
        pass
    '''