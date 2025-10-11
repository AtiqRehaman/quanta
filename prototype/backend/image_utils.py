from PIL import Image
import io
import numpy as np
import cv2
from skimage.measure import shannon_entropy

def convert_to_png(image):
    # Convert to PNG in memory
    pil_img = Image.fromarray(image)
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    buf.seek(0)
    return np.array(Image.open(buf))

def aspect_size(image):
    new_w = image.shape[1] // 2
    aspect_ratio = image.shape[1] / image.shape[0]
    new_h = int(new_w / aspect_ratio)
    return (new_w, new_h)

def score_image(blocks):
    # -------------------------------
    # Compute block scores
    # -------------------------------
    scores = []
    for i in range(blocks.shape[0]):
        for j in range(blocks.shape[1]):
            block = blocks[i, j]
            score = shannon_entropy(block)  # or np.var(block)
            scores.append((score, i, j))
            
    return scores

def mask_classical_blocks(color_cropped, top_blocks, block_size=8):
    # -------------------------------
    # Create mask for classical/quantum separation
    # -------------------------------
    mask = np.ones_like(color_cropped, dtype=np.uint8) * 255
    for _, i, j in top_blocks:
        y = i * block_size
        x = j * block_size
        mask[y:y+block_size, x:x+block_size] = 0  # quantum blocks

    classical_image = cv2.bitwise_and(color_cropped, mask)
    
    return classical_image