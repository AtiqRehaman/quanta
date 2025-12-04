import cv2
import numpy as np

# Load image into img1
img1 = cv2.imread("C:/Hybrid_Image/backend/images/sample_cube1.png") 

if img1 is None:
    raise FileNotFoundError("Image not found or path is incorrect.")

# Copy to img2
img2 = img1.copy()

# Convert img2 to bitstream (flatten and convert to binary string per pixel)
height, width, channels = img2.shape
bitstream = ''
for y in range(height):
    for x in range(width):
        for c in range(channels):
            bitstream += format(img2[y, x, c], '08b')  # 8-bit binary for each channel value
height, width, channels = img2.shape
bitstream = ''
for y in range(height):
    for x in range(width):
        for c in range(channels):
            bitstream += format(img2[y, x, c], '08b')  # 8-bit binary for each channel value

# Convert bitstream back to image
reconstructed = np.zeros_like(img2)
bit_index = 0
for y in range(height):
    for x in range(width):
        for c in range(channels):
            byte = bitstream[bit_index:bit_index+8]
            reconstructed[y, x, c] = int(byte, 2)
            bit_index += 8

# Calculate coincidence rate (percentage of matching pixels)
matching_pixels = np.sum(img1 == reconstructed)
total_pixels = img1.size
coincidence_rate = (matching_pixels / total_pixels) * 100 if total_pixels > 0 else 0.0

# Print coincidence rate
print(f"Coincidence Rate: {coincidence_rate:.2f}%")