from typing import Any
from traitlets import HasTraits, Int, Unicode, default
from JetbotYolo import DetectableObject
from JetbotYolo.JetbotYolo import *
from torch import Tensor

from libjetbot.ExtendedRobot import ReturnData, Handle, ReturnCommand, State


class ObjectDetectionThreshold:
    """
    This class defines a threshold for detected objects. It includes a method to increment
    a label and a method to see if a label has reached the threshold already.
    """

    def __init__(self, labels: str, threshold: int = 2):
        """
        Initializes the threshold object with labels and an integer value for the threshold
        :param labels: object detection labels
        :param threshold: integer number for threshold
        """
        self.object_labels = dict.fromkeys(labels, 0)
        self.threshold = threshold

    def increment_label(self, label: str):
        """
        Increments the counter for the given label by 1. Resets the counter for other labels.
        :param label: object detection label
        """
        self.object_labels[label] += 1
        for key in self.object_labels.keys():
            if key is not label:
                self.object_labels[key] = 0

    def reached_threshold(self, label) -> bool:
        """
        Checks if a label has reached the predefined threshold
        :param label: object detection label
        :return: - True - if the label has reached the defined threshold, False - if otherwise
        """
        return self.object_labels[label] >= self.threshold


class ObjectDetectionHandle(Handle, HasTraits):
    """
    This class implements the :class:`ExtendedRobot.Handle` Interface to be registered with the ExtendedBot.
    It handles the object detection and the sends commands to the bot based on detected road signs.
    """
    threshold_xmax = 90  # objects with xmax below threshold are ignored (signs left of the road)
    threshold_ymax = 70  # objects with ymax below threshold are too far away
    threshold_probability = 0.8  # objects with confidence below threshold may be hallucinations

    threshold_frames_beforeStop = 10  # for detected stop signs, don't stop immediately, but 10 frames later
    threshold_frames_stop = 30  # stop for 30 frames
    threshold_frames_ignoreStop = 20  # after stop, ignore all stop signs for 20 frames, in order not to be stuck in endless loop

    max_speed_sign_limit = 0.1
    max_speed_sign_nolimit = 0.16

    # For debugging purposes
    last_detected = Unicode()
    state_sign_stop = Int()
    global_fcounter = Int()

    state = None

    def __init__(self, yolo_model_path, trt=False):
        self.yolo = JetbotYolo(yolo_model_path, trt)
        self._model = None
        self.threshold = ObjectDetectionThreshold(self.yolo.Object_classes)

    def execute(self, image, state: State) -> ReturnData:
        # invoke method to get classes
        self.state = state
        self.adapt_thresholds_to_speed()
        self.yolo.run_detection_only(image)

        detected = self.yolo.get_nearest_object()
        self.last_detected = 'No sign' if detected is None else detected.get_type()

        # handle detected objects and return command 
        return self.__process_class__(detected)

    # higher speeds require lower thresholds for frames and ymax
    def adapt_thresholds_to_speed(self):
        self.threshold_frames_beforeStop = 10 * (0.10 / self.state.max_speed)
        self.threshold_frames_ignoreStop = 20 * (0.10 / self.state.max_speed)
        self.threshold_ymax = 70 * (0.10 / self.state.max_speed)

    def __process_class__(self, obj: DetectableObject) -> ReturnData:
        self.state.ODH_said_stop = False
        data = self.handle_stop_sign_preprocess()  # handle already detected stop_sign
        self.state_sign_stop = self.state.state_sign_stop
        self.global_fcounter = self.state.fcounter_global

        if data is None:
            if obj is None:
                return ReturnData(command=ReturnCommand.CONTINUE, max_speed=None, angle=None, left=None, right=None)
            else:
                self.threshold.increment_label(obj.get_type())
                if (obj.get_probability() > self.threshold_probability) and self.threshold.reached_threshold(
                        obj.get_type()) and (obj.get_xmax() > self.threshold_xmax) and (
                        obj.get_ymax() > self.threshold_ymax):
                    if obj.get_type() == 'sign_stop':
                        data = self.handle_stop_sign()
                    elif obj.get_type() == 'sign_limit':
                        data = self.handle_limit_sign()
                    elif obj.get_type() == 'sign_nolimit':
                        data = self.handle_nolimit_sign()

        if data is None:
            data = ReturnData(command=ReturnCommand.CONTINUE, max_speed=None, angle=None, left=None, right=None)
        return data

    def handle_stop_sign(self):
        if self.state.state_sign_stop == 0:  # 0: stop sign was seen in this frame, but not the frame before
            # robot continue, reset counter
            self.state.fcounter_stop_sign = self.state.fcounter_global
            self.state.state_sign_stop = 1  # next phase

    def handle_stop_sign_preprocess(self):
        if self.state.state_sign_stop == 1:  # 1: delay of action for seen stop sign
            if self.state.fcounter_global - self.state.fcounter_stop_sign > self.threshold_frames_beforeStop:  # if 10 frames, robot stop, reset counter
                self.state.state_sign_stop = 2  # next phase
                self.state.fcounter_stop_sign = self.state.fcounter_global
                self.state.ODH_said_stop = True
                return ReturnData(command=ReturnCommand.STOP, max_speed=None, angle=None, left=None, right=None)
        elif self.state.state_sign_stop == 2:  # 2: stop action for seen stop sign
            if self.state.fcounter_global - self.state.fcounter_stop_sign > self.threshold_frames_stop:  # if 30 frames, robot continue, reset counter
                self.state.state_sign_stop = 3  # next phase
                self.state.fcounter_stop_sign = self.state.fcounter_global
            else:
                self.state.ODH_said_stop = True
                return ReturnData(command=ReturnCommand.STOP, max_speed=None, angle=None, left=None, right=None)
        elif self.state.state_sign_stop == 3:  # 3: ignore stop sign after stop
            if self.state.fcounter_global - self.state.fcounter_stop_sign > self.threshold_frames_ignoreStop:  # if 20 frames, no longer ignore sign_stop
                self.state.state_sign_stop = 0  # next phase (reset)

    def handle_limit_sign(self):
        self.state.max_speed = self.max_speed_sign_limit
        return ReturnData(command=ReturnCommand.CONTINUE, max_speed=self.max_speed_sign_limit, angle=None, left=None,
                          right=None)

    def handle_nolimit_sign(self):
        self.state.max_speed = self.max_speed_sign_nolimit
        return ReturnData(command=ReturnCommand.CONTINUE, max_speed=self.max_speed_sign_nolimit, angle=None, left=None,
                          right=None)
