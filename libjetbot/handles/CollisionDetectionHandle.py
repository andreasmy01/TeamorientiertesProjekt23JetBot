import torch
import torch.nn.functional as functional
from torch import Tensor
from torch2trt import TRTModule

from libjetbot.ExtendedRobot import Handle, ReturnData, ReturnCommand, State


class CollisionDetectionHandle(Handle):
    threshold_collision = 0.8

    def __init__(self, path_to_model):
        # models/collision_resnet/collision_model_resnet_19_04_a_trt.pth
        self._model = TRTModule()
        self._model.load_state_dict(torch.load(path_to_model))

    def execute(self, image, state: State) -> ReturnData:
        collision_chance: float = self.get_collision_chance(image)
        if collision_chance > self.threshold_collision:
            state.CDH_said_stop = True
            return ReturnData(command=ReturnCommand.STOP, angle=None, max_speed=None, left=None, right=None)
        else:
            state.CDH_said_stop = False
            return ReturnData(command=ReturnCommand.CONTINUE, angle=None, max_speed=None, left=None, right=None)

    def get_collision_chance(self, image_preproc) -> float:
        collision = self._model(image_preproc)
        collision_softmax = functional.softmax(collision, dim=1).flatten()
        return float(collision_softmax[0])
