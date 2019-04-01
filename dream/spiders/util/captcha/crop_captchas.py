import cv2
import numpy as np
import os

def crop(img_path):
# Read the image and create a blank mask
    img = cv2.imread(img_path)
    if img is not None:
        h,w = img.shape[:2]
        mask = np.zeros((h,w), np.uint8)

        # Transform to gray colorspace and invert Otsu threshold the image
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

      

        # Search for contours, select the biggest and draw it on the mask
        _, contours, hierarchy = cv2.findContours(thresh, # if you use opening then change "thresh" to "opening"
                                                  cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
        cnt = max(contours, key=cv2.contourArea)
        cv2.drawContours(mask, [cnt], 0, 255, -1)

        # Perform a bitwise operation
        res = cv2.bitwise_and(img, img, mask=mask)

        ########### The result is a ROI with some noise
        ########### Clearing the noise

        # Create a new mask
        mask = np.zeros((h,w), np.uint8)

        # Transform the resulting image to gray colorspace and Otsu threshold the image
        gray = cv2.cvtColor(res,cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

        # Search for contours and select the biggest one again
        _, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
        cnt = max(contours, key=cv2.contourArea)

        # Draw it on the new mask and perform a bitwise operation again
        cv2.drawContours(mask, [cnt], 0, 255, -1)
        res = cv2.bitwise_and(img, img, mask=mask)

        x,y,w,h = cv2.boundingRect(cnt)
        cv2.rectangle(res,(x,y),(x+w,y+h),(255,255,255),1)

        # Crop the result
        final_image = res[y:y+h+1, x:x+w+1]

        return final_image

