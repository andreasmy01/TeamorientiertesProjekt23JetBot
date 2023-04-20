import time
from enum import Enum

import PIL
import torch
import torchvision.transforms as transforms
from torch import Tensor

from jetbot import Robot, Camera


class State:
    is_preparing_to_stop = False 
    frames_preparing_to_stop = 0 # globalen Framecounter an zwei Zeitpunkten subtrahieren

    is_stopped = False
    frames_stopped = 0 # globalen Framecounter an zwei Zeitpunkten subtrahieren

    def __init__(self):
        self._max_limit = 0.1

    @property
    def max_limit(self) -> float:
        return self._max_limit

    @max_limit.setter
    def max_limit(self, value: float):
        self._max_limit = value



class ReturnCommand(Enum):
    CONTINUE = 0
    STOP = 1


class ReturnData:
    def __init__(self, command: ReturnCommand, alpha: float, left: float, right: float):
        self._command = command
        self._alpha = alpha
        self._left = left
        self._right = right

    @property
    def command(self) -> ReturnCommand:
        return self._command

    @command.setter
    def command(self, value):
        self._command = value

    @property
    def alpha(self) -> float:
        return self._alpha

    @alpha.setter
    def alpha(self, value: float):
        self._alpha = value

    @property
    def left(self) -> float:
        return self._left

    @left.setter
    def left(self, value: float):
        self._left = value

    @property
    def right(self) -> float:
        return self._right

    @right.setter
    def right(self, value: float):
        self._right = value


class Handle:
    def execute(self, image, tensor: Tensor, previous_values: list, state: State) -> ReturnData:
        pass


class ExtendedRobot(Robot):
    handles: list = []
    a = 0
    stop_counter = 0
    stop_limit = 10

    # field properties
    steer_gain = 0
    steer_kd_gain = 0
    steer_bias = 0
    speed_control = 0.1

    def __init__(self, camera: Camera, device=torch.device('cuda'), *args, **kwargs):
        super(ExtendedRobot, self).__init__(*args, **kwargs)
        print("construct")
        self._camera = camera
        self._device = device
        self._mean = torch.Tensor([0.485, 0.456, 0.406]).cuda().half()
        self._std = torch.Tensor([0.229, 0.224, 0.225]).cuda().half()
        self._state = State()

    def start(self):
        print("start")
        self.execute({'new': self._camera.value})
        self._camera.observe(self.execute, names='value')

    def stop(self):
        print("stop")
        self._camera.unobserve(self.execute, names='value')
        time.sleep(0.1)
        super().stop()

    def destroy(self):
        self._camera.stop()

    def execute(self, change):
        print("exec")
        image = change['new']
        tensor = self.preprocess(image).to(self._device)
        return_values: list = []
        for handle in self.handles:
            return_data: ReturnData = handle.execute(
                image=image,
                tensor=tensor,
                previous_values=return_values,
                state=self._state
            )
            if return_data.command == ReturnCommand.STOP:
                if self.stop_counter < self.stop_limit:
                    break
                else:
                    self.stop_counter = 0

            return_values.append(return_data)

        if len(return_values) > 0:
            last: ReturnData = return_values.pop()
            a, left, right = last.alpha, last.left, last.right
            self.left_motor.value = left
            self.right_motor.value = right
        else:
            self.left_motor.value = 0.0
            self.right_motor.value = 0.0

    def register(self, handle: Handle):
        print("register")
        self.handles.append(handle)

    def unregister(self, handle: Handle):
        print("unregister")
        self.handles.remove(handle)

    def preprocess(self, image):
        image = PIL.Image.fromarray(image)
        image = transforms.functional.to_tensor(image).to(self._device)
        image.sub_(self._mean[:, None, None]).div_(self._std[:, None, None])
        return image[None, ...]
