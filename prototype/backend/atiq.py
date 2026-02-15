import cv2 
import numpy as np
from matplotlib import pyplot as plt

def pixel_replacement(image, old, new, color):
    low = np.array(old, dtype="uint8")
    high = np.array(new, dtype="uint8")
    mask = cv2.inRange(image, low, high)
    print("mask shape:", mask.shape)
    image[mask > 0] = color
    # return image

path = "prototype/backend/images/sample_cube.png"

img = cv2.imread(path)
if img is None:
	print(f"Error: Could not load image from {path}")
else:
    print(type(img))
    print(img.shape)
    

    pixel_replacement(img, [190,190,190], [255,255,255],[0,0,0])
    cv2.imshow("Modified Image", img)
    # cv2.imshow("Image", img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows() 
    
    # fig, axis = plt.subplots(1, 2, figsize=(10, 5))
    
    # axis[0].imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # axis[0].set_title("Original Image")
    # axis[0].axis('off')
    
    # axis[1].imshow(cv2.cvtColor(img_copy, cv2.COLOR_BGR2RGB))
    # axis[1].set_title("Modified Image")
    # axis[1].axis('off')
    
    # plt.tight_layout()
    # plt.show()
    b, g, r = cv2.split(img)
    print(b.shape, g.shape, r.shape)
    merged = cv2.merge((b, g, r))
    print(merged.shape)
    img[:, :, 2] = 0
    # cv2.imshow("No Blue Channel", img)
    # cv2.imshow("Blue Channel", b)
    # cv2.imshow("Green Channel", g)
    # cv2.imshow("Red Channel", r)
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    