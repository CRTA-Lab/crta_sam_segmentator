import cv2
import random
import numpy as np


def flip(image_path, flip_axis:bool=True):
    '''
    Flips an image.
    
    Arguments:
        image_path (str): path to image
        flip_around_x_axis (int): 0 to flip over x axis (horizontal), 1 to flip over y axis (vertical), negative value to flip over both.
    '''
    image = cv2.imread(image_path)
    flipped_image = cv2.flip(image, flip_axis)
    
    return flipped_image
    
def flip_random(image_path):
    '''
    Flips an image over a random axis.
    
    Arguments:
        image_path (str): path to image
    '''
    image = cv2.imread(image_path)
    
    flipped_image = cv2.flip(image, random.randint(-1, 1))
    
    cv2.imshow('flipped', flipped_image)
    cv2.waitKey(0)
    
def blur(image_path, blur_val:int=5):
    '''
    Blurs an image with given blur value.
    
    Arguments:
        image_path (str): path to image
        blur_val (int): blur noise value
    '''
    image = cv2.imread(image_path)
    aug_img = cv2.blur(image,(blur_val, blur_val))
    return aug_img
    
def shift(image_path, tx:int=1, ty:int=1):
    '''
    Shifts an image in x and y direction.
    
    Arguments:
        image_path (str): path to image
        tx (int): x axis shift
        ty (int): y axis shift
    '''
    image = cv2.imread(image_path)
    rows, cols = image.shape[:2]
    M = np.float32([[1, 0, tx], [0, 1, ty]])
    aug_img = cv2.warpAffine(image, M, (cols, rows))

    # crop black area
    x, y = max(tx, 0), max(ty, 0)
    w, h = cols - abs(tx), rows - abs(ty)
    aug_img = aug_img[y:y+h, x:x+w]
    return cv2.resize(aug_img, (cols, rows))
    
def rotate(image_path, angle:int):
    '''
    Rotates the image around its axis by a given angle.
    
    Arguments:
        image_path (str): path to image
    '''
    
    if angle < -180 or angle > 180:
        print('Invalid angle...modifying')
        angle = angle % 180 if angle > 0 else -(abs(angle) % 180)
        print(f'using angle {angle}')
        
    image = cv2.imread(image_path)
    rows, cols = image.shape[:2]
    cx, cy = rows, cols # center of rotation
    M = cv2.getRotationMatrix2D((cy//2, cx//2), angle, 1)
    
    return cv2.warpAffine(image, M, (cols, rows))
    
def add_noise(image_path):
    '''
    Adds noise to an image by converting to HSV and then generating noise.
    
    Arguments:
        image_path (str): path to image
    '''
    
    rng = np.random.default_rng(30)
    image = cv2.imread(image_path)
    rows, cols = image.shape[:2]
    aug_img = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    h, s, v = cv2.split(aug_img)
    
    h += rng.normal(0, 30, size=(rows, cols)).astype(np.uint8)
    s += rng.normal(0, 10, size=(rows, cols)).astype(np.uint8)
    v += rng.normal(0, 5, size=(rows, cols)).astype(np.uint8)
    
    aug_img = cv2.merge([h, s, v])
    return cv2.cvtColor(aug_img, cv2.COLOR_HSV2RGB)
    
if __name__=='__main__':
    path = 'images/car.png'
    
    #augmented = flip(path, -1)
    #augmented = flip_random(path)
    #augmented = blur(path, 5)
    augmented = shift(path, 100, 100)
    cv2.imshow('augmented', augmented)
    cv2.waitKey(0)
    