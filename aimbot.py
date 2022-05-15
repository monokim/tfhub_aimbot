import keyboard
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import win32api, win32con
import cv2
import math
import time

from speedscreen import WindowCapture

detector = hub.load("https://tfhub.dev/tensorflow/centernet/resnet50v1_fpn_512x512/1")
size_scale = 3
hwnd = WindowCapture('Counter-Strike: Global Offensive - Direct3D 9')

while True:

    '''
    check windows name: 
    
    def winEnumHandler( hwnd, ctx ):
        if win32gui.IsWindowVisible( hwnd ):
        print (hex(hwnd), win32gui.GetWindowText( hwnd ))

    win32gui.EnumWindows( winEnumHandler, None )
    '''
    # Get rect of Window
    # hwnd = win32gui.FindWindow("UnrealWindow", None) # Fortnite

    # rect = win32gui.GetWindowRect(hwnd)
    # region = rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]
    screen = hwnd.get_screenshot()
    # Get image of screen
    ori_img = np.array(screen)
    ori_img = cv2.resize(ori_img, (ori_img.shape[1] // size_scale, ori_img.shape[0] // size_scale))
    image = np.expand_dims(ori_img, 0)
    img_w, img_h = image.shape[2], image.shape[1]

    # Detection
    result = detector(image)
    result = {key: value.numpy() for key, value in result.items()}
    boxes = result['detection_boxes'][0]
    scores = result['detection_scores'][0]
    classes = result['detection_classes'][0]

    # Check every detected object
    detected_boxes = []
    for i, box in enumerate(boxes):
        # Choose only person(class:1)
        if classes[i] == 1 and scores[i] >= 0.7:
            ymin, xmin, ymax, xmax = tuple(box)
            if ymin > 0.5 and ymax > 0.8:  # CS:Go
                # if int(xmin * img_w * 3) < 450: # Fortnite
                continue
            left, right, top, bottom = int(xmin * img_w), int(xmax * img_w), int(ymin * img_h), int(ymax * img_h)
            detected_boxes.append((left, right, top, bottom))
            cv2.rectangle(ori_img, (left, top), (right, bottom), (255, 255, 0), 2)

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
            dist = math.sqrt(math.pow(img_w / 2 - c_x, 2) + math.pow(img_h / 2 - c_y, 2))
            if dist < min:
                min = dist
                at = i

        # Pixel difference between crosshair(center) and the closest object
        x = centers[at][0] - img_w / 2
        y = centers[at][1] - img_h / 2 - (detected_boxes[at][3] - detected_boxes[at][2]) * 0.45

        # Move mouse and shoot
        scale = 1.7 * size_scale
        x = int(x * scale)
        y = int(y * scale)
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x, y, 0, 0)
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        # time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    ori_img = cv2.cvtColor(ori_img, cv2.COLOR_BGR2RGB)

    cv2.imshow("ori_img", ori_img)
    cv2.waitKey(1)
    if keyboard.is_pressed('q'):
        break
    # time.sleep(0.1)
