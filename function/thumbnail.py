import cv2
import os

def make_thumbnail(video, userFileName):
    vidcap = cv2.VideoCapture(video);

    while(vidcap.isOpened()):
      ret, image = vidcap.read()
  
      if(int(vidcap.get(1)) % 100 == 0):
        tempThumbnailSrc = '/tmp/' + userFileName + '-temp.jpg'
        cv2.imwrite(tempThumbnailSrc, image)
        break

    return tempThumbnailSrc