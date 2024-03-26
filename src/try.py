# import cv2 as cv
# import math
# import mediapipe as mp
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from utils.face_detection import add_vfx
#
#
# cap = cv.VideoCapture(0)
# while True:
#     ret, img = cap.read()
#     img = cv.flip(img, 1)
#
#     img = add_vfx(img, 'glasses', '01')
#     cv.imshow('img', img)
#     if cv.waitKey(1) & 0xFF == ord('q'):
#         break
