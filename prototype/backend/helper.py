# ---------------------------
# Helper utilities
# ---------------------------

import cv2
import numpy as np

class Helper:
    
    @staticmethod
    def img_to_bitstream(block):
        """Convert RGB image block (np.array uint8) to string of bits."""
        bytes_data = block.tobytes()
        bits = ''
        for byte in bytes_data:
            for i in reversed(range(8)):
                bits += str((byte >> i) & 1)
        return bits

    @staticmethod
    def bitstream_to_image(bitstr: str, shape):
        """Convert bitstring back to a numpy uint8 array with given shape."""
        L = len(bitstr)
        if L % 8 != 0:
            raise ValueError("Bit string length must be multiple of 8")
        bytes_list = [int(bitstr[i:i+8], 2) for i in range(0, L, 8)]
        arr = np.array(bytes_list, dtype=np.uint8).reshape(shape)
        return arr

    @staticmethod
    def pad_bitstring_to_even_pairs(bstr):
        """Pad bitstring (append 0) so length is even number of bits (pairs of 2)."""
        if len(bstr) % 2 == 1:
            bstr += '0'
        return bstr
    
    @staticmethod
    def chunk_bits_by2(bstr):
        return [bstr[i:i+2] for i in range(0, len(bstr), 2)]

    @staticmethod
    def sharpen(img):
        blur = cv2.GaussianBlur(img, (3,3), 0)
        return cv2.addWeighted(img, 2.0, blur, -1.0, 0)