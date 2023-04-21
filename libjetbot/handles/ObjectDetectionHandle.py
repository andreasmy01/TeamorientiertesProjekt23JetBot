from JetbotYolo.DetectableObject import DetectableObject
from JetbotYolo.JetbotYolo import JetbotYolo
from torch import Tensor

from libjetbot.ExtendedRobot import ReturnData, Handle, ReturnCommand, State


class ObjectDetectionHandle(Handle):
    """
    Class that handles object detection with YoloV5 as the model.

    Implements :class:`Handle` interface and performs actions calculated from the given frame.
    """

    def __init__(self, path):
        """
        Method that initializes the object detection model with a given path
        :param path: to YoloV5 weights file
        """
        self.model = JetbotYolo(path)
        self.threshold_xmax = 120
        self.threshold_ymax = 40

        self.threshold_frames_stop = 30  # nach 30 frames is_stopped auf False setzen
        self.threshold_frames_beforeStop = 10  # nach 10 frames is_preparing_to_stop auf False setzen
        self.stop_started = False
        self.counter_frames_stop = 0

    def execute(self, image, tensor: Tensor, previous_values: list, state: State) -> ReturnData:
        # invoke method to get classes
        self.model.run_detection_only(image)

        detected = self.model.get_nearest_object()

        # handle detected objects and return command & poi
        return self.process_class(detected, state)

    def process_class(self, obj: DetectableObject, state: State) -> ReturnData:
        if obj is None:
            return ReturnData(command=ReturnCommand.CONTINUE)
        else:
            if obj.get_probability() > 0.3 and obj.get_xmax() > self.threshold_xmax and obj.get_ymax() > self.threshold_ymax:
                if obj.get_type() == 'sign_stop':
                    return self.handle_stop_sign(state)
                elif obj.get_type() == 'sign_limit':
                    # @todo max_speed auf 0.11 setzen
                    # return self.handle_limit_sign(sign, state)
                    pass
                elif obj.get_type() == 'no_limit':
                    # @todo max_speed auf 0.15 setzen
                    # return self.handle_nolimit_sign(sign, state)
                    pass

    def handle_stop_sign(self, state) -> ReturnData:
        # After 1 second stop for 3 seconds
        if not self.stop_started:
            if self.counter_frames_stop < self.threshold_frames_beforeStop:
                if self.counter_frames_stop == 0:
                    print('Preparing to stop.')
                self.counter_frames_stop += 1
                return ReturnData(command=ReturnCommand.CONTINUE)
            else:
                self.stop_started = True
                self.counter_frames_stop = 0
                print('Starting stop procedure')
        else:
        # Start the stop process
            if self.counter_frames_stop < self.counter_frames_stop:
                self.counter_frames_stop += 1
                state.max_limit = 0
                return ReturnData(command=ReturnCommand.STOP, alpha=0, left=0, right=0)
            else:
                state.reset_to_default_limit()
                self.counter_frames_stop = 0
                self.stop_started = False
                return ReturnData(command=ReturnCommand.CONTINUE)

    # Da bei uns nur NoLimit, Limit und Stop verarbeitet werden und diese 3 Schilder sich widersprechen, nur das mit höchstem ymax behandeln
    def getTotalNearestObject(self, detected_objects: dict[DetectableObject]) -> DetectableObject:
        obj = next(iter(detected_objects))  # first object
        for sign in detected_objects:
            if sign.get_ymax() > obj.get_ymax():
                obj = sign
        return obj

    '''
    # Class to handle signs detected previously
    def handle_limit_sign(self, sign, state):
        pass
    '''
