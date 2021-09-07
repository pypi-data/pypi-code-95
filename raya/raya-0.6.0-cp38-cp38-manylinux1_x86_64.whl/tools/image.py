import cv2

def show_image(img, title=''):
    for i in range(3):
        cv2.imshow(title, img)
        cv2.waitKey(10)