import cv2
import numpy as np
from elements.yolo import OBJ_DETECTION

from jetbot import Camera, bgr8_to_jpeg
from jetbot import Robot
import time
import torch
import torch.nn.functional as functional
import torchvision
import torchvision.transforms as transforms

import math
import os
import time
from uuid import uuid1
import traitlets
import PIL.Image

print("imports")

robot = Robot()
angle_last = 0.0
stop_counter = 0  
x = 0.0
y = 0.0
speed_control=0.11
can_drive = True
stop_counter_limit = 10
blocked_threshold=0.9
steer_gain=0.04
steer_kd_gain=0.01
steer_bias=0
robot_is_stopped = True
max_speed = 0.11
steering_correction_activation = 0.25

model_road = torchvision.models.resnet18(pretrained=False)
model_road.fc = torch.nn.Linear(512, 2)
model_road.load_state_dict(torch.load('weights/model_road_following.pth'))

model_collision = torchvision.models.alexnet(pretrained=False)
model_collision.classifier[6] = torch.nn.Linear(model_collision.classifier[6].in_features, 2)
model_collision.load_state_dict(torch.load('weights/model_collavoid.pth'))
print("loads")
device = torch.device('cuda')
model_road = model_road.to(device)
model_collision = model_collision.to(device)
print("to device")

mean = torch.Tensor([0.485, 0.456, 0.406]).half().float().to(device)
std = torch.Tensor([0.229, 0.224, 0.225]).half().float().to(device)

angle_last, stop_counter = 0.0, 0
can_drive = True
stop_counter_limit = 10
x, y = 0.0, 0.0
robot_is_stopped = False

def get_collision_chance(image) -> float:
    collision = model_collision(image)
    collision_softmax = functional.softmax(collision, dim=1).flatten()
    return float(collision_softmax[0])

def calculate_speed(last_a: float, x_in: float, y_in: float) -> (float, float, float):
    if robot_is_stopped:
        return 0.0, 0.0, 0.0
    a = math.atan2(x_in, y_in)
    #xy_out.value = f"({x:.02f} {y:.02f})"
    pid = a * steer_gain + (a - last_a) * steer_kd_gain
    steer_val = pid + steer_bias
    left = max(min(speed_control + steer_val, 1.0), 0.0)
    right = max(min(speed_control - steer_val, 1.0), 0.0)
    return a, left, right

def get_road_direction(image) -> (float, float):
    model_xy = model_road(image).detach().float().cpu().numpy().flatten()
    model_x = model_xy[0]
    model_y = (0.5 - model_xy[1]) / 2.0
    return model_x, model_y

def preprocess(image):
    image = PIL.Image.fromarray(image)
    image = transforms.functional.to_tensor(image).to(device)
    image.sub_(mean[:, None, None]).div_(std[:, None, None])
    return image[None, ...]

def correct_steering(left: float, right: float, angle: float) -> (float, float):
    abs_angle = math.fabs(angle)
    global steering_correction_activation
    if abs_angle < steering_correction_activation:
        return left, right
    
    angle_f = abs_angle / math.pi + 0
    diff_gain_limit = 1.5
    curve_min_val = 0.08

    if left * diff_gain_limit < right:
        l = (left * diff_gain_limit)
        right = min(l if l > 0 else curve_min_val, right)
        left = left - (angle_f * left)

    elif left > right * diff_gain_limit:
        r = (right * diff_gain_limit)
        left = min(r if r > 0 else curve_min_val, left)
        right = right - (angle_f * right)

    return left, right

def execute(image):
    global angle_last, robot, stop_counter, stop_counter_limit, can_drive, x, y, blocked_threshold
    global speed_control, steer_gain, steer_kd_gain, steer_bias, max_speed
    
    image_preproc = preprocess(image).to(device)

    prob_blocked = get_collision_chance(image_preproc)
    #print("prob blocked: ", prob_blocked)
    if can_drive:
        can_drive = prob_blocked <= blocked_threshold
        if can_drive:
            stop_counter = 0
            x, y = get_road_direction(image_preproc)
            speed_control = max_speed
        else:
            stop_counter += 1
    else:
        stop_counter += 1
        if stop_counter < stop_counter_limit:
            x, y, speed_control = 0.0, 0.0, 0
        else:
            can_drive = True
            stop_counter = 0

    angle, left, right = calculate_speed(angle_last, x, y)
    angle_last = angle
    left, right = correct_steering(left, right, angle)
    robot.left_motor.value = left
    robot.right_motor.value = right

def gstreamer_pipeline(
    capture_width=224,
    capture_height=224,
    display_width=224,
    display_height=224,
    framerate=10,
    flip_method=0,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )


# To flip the image, modify the flip_method parameter (0 and 2 are the most common)
#camera = Camera.instance(width=224, height=224, fps=10)
#execute({'new': camera.value})
#camera.observe(execute, names='value')

print(gstreamer_pipeline(flip_method=0))
cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
if cap.isOpened():
    while 1 >= 0:
        ret, frame = cap.read()
        if ret:
            execute(frame)
    #camera.unobserve(execute, names='value')
    #time.sleep(0.1)
    robot.stop()
    cap.release()
else:
    print("Unable to open camera")


