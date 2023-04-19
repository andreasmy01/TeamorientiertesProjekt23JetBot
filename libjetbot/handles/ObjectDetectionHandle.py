from torch import Tensor
from JetsonYoloNew.JetbotYolo import *
from JetsonYoloNew import DetectableObject
from libjetbot.ExtendedRobot import ReturnData, Handle, ReturnCommand


class ObjectDetectionHandle(Handle):

    def __init__(self, path):
        self.yolo = JetbotYolo(path)

    def execute(self, models: {}, image, tensor: Tensor, previous_values: list) -> ReturnData:
        model = models['detection']

        # invoke method to get classes
        self.yolo.run_detection_only(image)
        detected = self.yolo.get_filtered_objects()

        # handle detected objects and return command & poi
        return self.__process_classes__(detected)

    def __process_classes__(self, detected_objects: dict[DetectableObject]) -> ReturnData:
        if detected_objects is None:
            detected_objects = []
            return ReturnData(ReturnCommand.CONTINUE)
        else:
            for sign in detected_objects:
                if sign == 'sign_stop':
                    return ReturnData(ReturnCommand.STOP)
                    pass
                else:
                    return ReturnData(ReturnCommand.CONTINUE)

    # Class to handle signs detected previously
    def handle_signs(self, sign):
        pass
