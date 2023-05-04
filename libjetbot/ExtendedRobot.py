import time
from enum import Enum

import PIL
import torch
import torchvision.transforms as transforms
from torch import Tensor

from jetbot import Robot, Camera


class State:
    state_sign_stop = 0
    fcounter_collision = 0
    fcounter_stop_sign = 0
    fcounter_global = 0
    fcounter_max = 500

    CDH_said_stop = False
    ODH_said_stop = False

    def __init__(self):
        self._max_speed = 0.12

    @property
    def max_speed(self) -> float:
        return self._max_speed

    @max_speed.setter
    def max_speed(self, value: float):
        self._max_speed = value


class ReturnCommand(Enum):
    CONTINUE = 0
    STOP = 1


class HandleTypes(Enum):
    """
    Enum for known Handle Types
    """
    ROAD_FOLLOWING = 0,
    COLLISION_DETECTION = 1,
    OBJECT_DETECTION = 2


class ReturnData:
    def __init__(self, command: ReturnCommand, max_speed: float, angle: float, left: float, right: float):
        self._max_speed = max_speed
        self._command = command
        self._angle = angle
        self._left = left
        self._right = right

    @property
    def command(self) -> ReturnCommand:
        return self._command

    @command.setter
    def command(self, value):
        self._command = value

    @property
    def angle(self) -> float:
        return self._angle

    @angle.setter
    def angle(self, value: float):
        self._angle = value

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

    @property
    def max_speed(self) -> float:
        return self._max_speed

    @max_speed.setter
    def max_speed(self, value: float):
        self._max_speed = value


class Handle:
    """
    Handle Interface that includes an "execute" method for internal processing
    """
    def execute(self, image, tensor: Tensor, previous_values: list, state: State) -> ReturnData:
        """
        Execute method for processing on a new image frame
        :param image: current image to process
        :param tensor: tensor
        :param previous_values: previous values
        :param state: state
        :return: ReturnData object that is handled in ExtendedRobot
        """
        pass


class ExtendedRobot(Robot):
    """
    This class registers handles for execution on image frames and starts/stops the robot.
    """
    handles = {}
    data = ReturnData(None, None, None, None, None)

    # field properties
    steer_gain = 0.03
    steer_kd_gain = 0.00
    steer_bias = 0
    speed_control = 0.12

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

    def pause(self):
        print("pause")
        self._camera.unobserve(self.execute, names='value')
        time.sleep(0.1)
        self.stop()

    def destroy(self):
        self._camera.stop()

    # gets called every frame, calls handles accordingly, gives handles current image
    def execute(self, change):
        image = change['new']
        self.manage_fcounters()
        image_preproc = self.preprocess(image).to(self._device)  # CDH and RFH require a preprocessed image
        if not self._state.ODH_said_stop:  # if not stopped because of sign_stop: check for upcoming collision
            handle = self.handles[HandleTypes.COLLISION_DETECTION]
            return_data: ReturnData = handle.execute(
                image=image_preproc,
                state=self._state
            )
            self.data = self.process_return_data(return_data)
            if self.data.command == ReturnCommand.STOP:
                self.stop()
            elif self.data.command == ReturnCommand.CONTINUE:  # if collision threshold was not reached: calculate PoI
                handle = self.handles[HandleTypes.ROAD_FOLLOWING]
                return_data: ReturnData = handle.execute(
                    image=image_preproc,
                    state=self._state
                )
                self.data = self.process_return_data(return_data)
                # calculated motor speed values are set to drive curves
                self.left_motor.value = self.data.left
                self.right_motor.value = self.data.right

        if not self._state.CDH_said_stop:  # if not stopped because of upcoming collision: detect objects, do sign handling
            handle = self.handles[HandleTypes.OBJECT_DETECTION]
            return_data: ReturnData = handle.execute(
                image=image,
                state=self._state
            )
            self.data = self.process_return_data(return_data)
            if self.data.command == ReturnCommand.STOP:
                self.stop()

    # resets frame_counters accordingly, so int does not exceed MAX INTEGER
    def manage_fcounters(self):
        self._state.fcounter_global += 1
        if self._state.fcounter_global > self._state.fcounter_max:
            fcounter_difference = self._state.fcounter_global - self._state.fcounter_stop_sign
            self._state.fcounter_global = 1
            self._state.fcounter_stop_sign = self._state.fcounter_global - fcounter_difference

    # new values overwrite current values if new values are not None
    def process_return_data(self, return_data: ReturnData):

        new_command = return_data.command if not return_data.command is None else self.data.command
        new_maxspeed = return_data.max_speed if not return_data.max_speed is None else self.data.max_speed
        new_angle = return_data.angle if not return_data.angle is None else self.data.angle
        new_left = return_data.left if not return_data.left is None else self.data.left
        new_right = return_data.right if not return_data.right is None else self.data.right

        return ReturnData(
            command=new_command,
            max_speed=new_maxspeed,
            angle=new_angle,
            left=new_left,
            right=new_right
        )

    def register(self, name: HandleTypes, handle: Handle):
        print(f"Registering module '{name}'")
        self.handles[name] = handle

    def unregister(self, handle: Handle):
        print("unregister")
        self.handles.remove(handle)

    def preprocess(self, image):
        image = PIL.Image.fromarray(image)
        image = transforms.functional.to_tensor(image).to(self._device).half()
        image.sub_(self._mean[:, None, None]).div_(self._std[:, None, None])
        return image[None, ...]
