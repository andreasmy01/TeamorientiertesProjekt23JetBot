import math
import time
from enum import Enum

import PIL
import torch
import torchvision.transforms as transforms
from torch import Tensor

from jetbot import Robot, Camera


class State:

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
    def __init__(self, command: ReturnCommand, poi: (float, float) = (0, 0)):
        self._command = command
        self._poi = poi

    @property
    def command(self) -> ReturnCommand:
        return self._command

    @command.setter
    def command(self, value):
        self._command = value

    @property
    def poi(self) -> (float, float):
        return self._poi

    @poi.setter
    def poi(self, value):
        self._poi = value


class Handel:
    def execute(self, models: {}, image, tensor: Tensor, previous_values: list, state: State) -> ReturnData:
        pass


class ExtendedRobot(Robot):
    handels: list = []
    a = 0
    stop_counter = 0
    stop_limit = 10

    # field properties
    steer_gain = 0
    steer_kd_gain = 0
    steer_bias = 0
    speed_control = 0.1

    def __init__(self, camera: Camera, models: {}, device=torch.device("cpu"), *args, **kwargs):
        super(ExtendedRobot, self).__init__(*args, **kwargs)
        print("construct")
        self._camera = camera
        self._models = models
        self._device = device
        self._mean = torch.Tensor([0.485, 0.456, 0.406]).half().float().to(device)
        self._std = torch.Tensor([0.229, 0.224, 0.225]).half().float().to(device)
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
        for handel in self.handels:
            return_data: ReturnData = handel.execute(
                models=self._models,
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

        left, right = 0, 0
        if len(return_values) > 0:
            last: ReturnData = return_values.pop()
            x, y = last.poi
            self.a, left, right = self.calculate_speed(self.a, x, y)
        self.left_motor.value = left
        self.right_motor.value = right

    def register(self, handel: Handel):
        print("register")
        self.handels.append(handel)

    def unregister(self, handel: Handel):
        print("unregister")
        self.handels.remove(handel)

    def preprocess(self, image):
        image = PIL.Image.fromarray(image)
        image = transforms.functional.to_tensor(image).to(self._device)
        image.sub_(self._mean[:, None, None]).div_(self._std[:, None, None])
        return image[None, ...]

    def calculate_speed(self, last_a: float, x_in: float, y_in: float) -> (float, float, float):
        a: float = math.atan2(x_in, y_in)
        pid: float = a * self.steer_gain + (a - last_a) * self.steer_kd_gain
        steer_val: float = pid + self.steer_bias
        left: float = max(min(self.speed_control + steer_val, 1.0), 0.0)
        right: float = max(min(self.speed_control - steer_val, 1.0), 0.0)
        # TODO: apply speed limit here
        return a, left, right
