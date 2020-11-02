import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import pyautogui
import win32api, win32con, win32gui
import cv2
import math
import time

detector = hub.load("https://tfhub.dev/tensorflow/centernet/resnet50v1_fpn_512x512/1")
size_scale = 3

while True:
    # Get rect of Window
    hwnd = win32gui.FindWindow(None, 'Counter-Strike: Global Offensive')
    rect = win32gui.GetWindowRect(hwnd)
    region = rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]

    # Get image of screen
    image = np.array(pyautogui.screenshot(region=region))
    image = cv2.resize(image, (image.shape[1] // size_scale, image.shape[0] // size_scale))
    image = np.expand_dims(image, 0)
    img_w, img_h = image.shape[2], image.shape[1]

    # Detection
    result = detector(image)
    result = {key:value.numpy() for key,value in result.items()}
    boxes = result['detection_boxes'][0]
    scores = result['detection_scores'][0]
    classes = result['detection_classes'][0]

    # Check every detected object
    detected_boxes = []
    for i, box in enumerate(boxes):
        # Choose only person(class:1)
        if classes[i] == 1 and scores[i] >= 0.5:
            ymin, xmin, ymax, xmax = tuple(box)
            if ymin > 0.5 and ymax > 0.8:
                continue
            left, right, top, bottom = int(xmin * img_w), int(xmax * img_w), int(ymin * img_h), int(ymax * img_h)
            detected_boxes.append((left, right, top, bottom))

    print("Detected:", len(detected_boxes))

    # Check Closest
    if len(detected_boxes) >= 1:
        min = 99999
        at = 0
        centers = []
        for i, box in enumerate(detected_boxes):
            x1, x2, y1, y2 = box
            c_x = ((x2 - x1) / 2) + x1
            c_y = ((y2 - y1) / 2) + y1
            centers.append((c_x, c_y))
            dist = math.sqrt(math.pow(img_w/2 - c_x, 2) + math.pow(img_h/2 - c_y, 2))
            if dist < min:
                min = dist
                at = i

        x = centers[at][0] - img_w/2
        y = centers[at][1] - img_h/2 - (detected_boxes[at][3] - detected_boxes[at][2]) * 0.45

        # Move mouse and shoot
        scale = 1.7 * size_scale
        x = int(x * scale)
        y = int(y * scale)
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x, y, 0, 0)
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    time.sleep(0.1)
