from JetsonYoloNew import DetectableObject
from JetsonYoloNew.JetbotYolo import *
from torch import Tensor

from libjetbot.ExtendedRobot import ReturnData, Handle, ReturnCommand, State


class ObjectDetectionHandle(Handle):

    def __init__(self, path):
        self.yolo = JetbotYolo(path)
        self._model = None

    def execute(self, image, tensor: Tensor, previous_values: list, state: State) -> ReturnData:
        # invoke method to get classes
        self.yolo.run_detection_only(image)
        detected = self.yolo.get_filtered_objects()

        # handle detected objects and return command & poi
        return self.__process_classes__(detected, state)

    def __process_classes__(self, detected_objects: dict[DetectableObject], state: State) -> ReturnData:
        if detected_objects is None:
            return ReturnData(ReturnCommand.CONTINUE)
        else:

            for sign in detected_objects:
                if sign == 'sign_stop':
                    return ReturnData(ReturnCommand.STOP)
                    pass
                elif sign == 'sign_limit':
                    return self.handle_limit_sign(sign, state)

    # Class to handle signs detected previously
    def handle_limit_sign(self, sign, state):
        pass
