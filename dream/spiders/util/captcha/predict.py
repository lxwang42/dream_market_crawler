from keras.models import load_model
from keras import backend as K
import tensorflow as tf
from imutils import paths
import numpy as np
import imutils
import cv2
import os
import pickle
import logging


class CaptchaSolver:
    def __init__(self,):
        logging.getLogger('tensorflow').disabled = True
        path = os.path.dirname(__file__)
        MODEL_FILENAME = path + "/captcha_model.hdf5"
        self.model = load_model(MODEL_FILENAME)
        self.model.predict(np.random.rand(8, 20, 20, 1))
        self.session = K.get_session()
        self.graph = tf.get_default_graph()
        self.graph.finalize() 

    def SolveCaptcha(self, url):
        with self.session.as_default():
            with self.graph.as_default():
                path = os.path.dirname(__file__)
                MODEL_LABELS_FILENAME = path + "/model_labels.dat"

                with open(MODEL_LABELS_FILENAME, "rb") as f:
                    lb = pickle.load(f)



                img_url = url

                img = self.crop(img_url)

                image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                image = cv2.copyMakeBorder(image, 20, 20, 20, 20, cv2.BORDER_REPLICATE)


                thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

                contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                contours = contours[0] if imutils.is_cv2() else contours[1]
                letter_image_regions = []


                min_height =100

                confusing = {
                    'C':'c',
                    'cs':'C',
                    'I':'is',
                    'is':'I',
                    'J':'j',
                    'js':'J',
                    'O':'o',
                    'os':'O',
                    'P':'p',
                    'ps':'P',
                    'S':'s',
                    'ss':'S',
                    'U':'u',
                    'us':'U',
                    'V':'v',
                    'vs':'V',
                    'W':'w',
                    'ws':'W',
                    'X':'x',
                    'xs':'X',
                    'Y':'y',
                    'ys':'Y',
                    'Z':'zs',
                    'zs':'Z'
                }


                for contour in contours:
                        # Get the rectangle that contains the contour
                    (x, y, w, h) = cv2.boundingRect(contour)

                    if h>10:
                        if h < min_height:
                            min_height = h

                        if w / h > 1.7:
                                # This contour is too wide to be a single letter!
                                # Split it in half into two letter regions!
                            half_width = int(w / 2)
                            letter_image_regions.append((x, y, half_width, h))
                            letter_image_regions.append((x + half_width, y, half_width, h))
                        else:
                                # This is a normal letter by itself
                            letter_image_regions.append((x, y, w, h))


                    letter_image_regions = sorted(letter_image_regions, key=lambda x: x[0])

                    predictions = []


                    count = 0

                    for letter_bounding_box in letter_image_regions:


                        x, y, w, h = letter_bounding_box
                        letter_image = image[y - 2:y + h + 2, x - 2:x + w + 2]

                        count = count + 1


                        letter_image = self.resize_to_fit(letter_image, 20, 20)


                        letter_image = np.expand_dims(letter_image, axis=2)
                        letter_image = np.expand_dims(letter_image, axis=0)


                        # letter_image = np.random.rand(8, 20, 20, 1)
                        prediction = self.model.predict(letter_image)
                        letter = lb.inverse_transform(prediction)[0]

                        if letter in confusing:
                            if h/min_height<=1.0 and letter.islower:
                                letter = letter
                            elif h/min_height<= 1.0 and letter.isupper:
                                letter = confusing[letter]
                            elif h/min_height>=1.0 and letter.isupper:
                                letter = letter
                            else:
                                letter = confusing[letter]


                        if len(letter) >1:
                            letter  = letter[:1]
                        else:
                            letter = letter

                        predictions.append(letter)



                    captcha_text = "".join(predictions)
        print("CAPTCHA text is: {}".format(captcha_text))
        K.clear_session()
        return captcha_text

    def resize_to_fit(self, image, width, height):
        """
        A helper function to resize an image to fit within a given size
        :param image: image to resize
        :param width: desired width in pixels
        :param height: desired height in pixels
        :return: the resized image
        """

        # grab the dimensions of the image, then initialize
        # the padding values
        (h, w) = image.shape[:2]

        # if the width is greater than the height then resize along
        # the width
        if w > h:
            image = imutils.resize(image, width=width)

        # otherwise, the height is greater than the width so resize
        # along the height
        else:
            image = imutils.resize(image, height=height)

        # determine the padding values for the width and height to
        # obtain the target dimensions
        padW = int((width - image.shape[1]) / 2.0)
        padH = int((height - image.shape[0]) / 2.0)

        # pad the image then apply one more resizing to handle any
        # rounding issues
        image = cv2.copyMakeBorder(image, padH, padH, padW, padW,
            cv2.BORDER_REPLICATE)
        image = cv2.resize(image, (width, height))

        # return the pre-processed image
        return image

    def crop(self, img_path):
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