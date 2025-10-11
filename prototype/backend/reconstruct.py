import numpy as np
from helper import Helper
helper = Helper()

def reconstruct_quantum_blocks(received_bit_pairs, block_indices, pair_counts, block_shape):
    quantum_reconstructed_blocks = {}
    # Reconstruct blocks by splitting received bit pairs
    start_idx = 0
    for (i, j), count in zip(block_indices, pair_counts):
        block_bit_pairs = received_bit_pairs[start_idx:start_idx + count]
        bitstr = ''.join(block_bit_pairs)
        recon_block = helper.bitstream_to_image(bitstr, block_shape)
        quantum_reconstructed_blocks[(i, j)] = recon_block
        start_idx += count
        
    return quantum_reconstructed_blocks

def reconstruct_quantum_image(quantum_reconstructed_blocks, image_shape, block_size=8):
    h, w, c = image_shape
    quantum_image = np.zeros((h, w, c), dtype=np.uint8)
    
    for (i, j), block in quantum_reconstructed_blocks.items():
        y = i * block_size
        x = j * block_size
        quantum_image[y:y+block_size, x:x+block_size] = block

    return quantum_image


def  reconstruct_full_image(metadata, classical_image, quantum_denoised, block_size=8):
    """
    Reconstruct the image from its metadata and the two types of blocks.
    """
    reconstructed = np.zeros_like(classical_image)
    
    for block in metadata["blocks"]:
        i = block["row"]
        j = block["col"]
        y = i * block_size
        x = j * block_size

        if block["type"] == "classical":
            reconstructed[y:y+block_size, x:x+block_size] = classical_image[y:y+block_size, x:x+block_size]
        else:
            reconstructed[y:y+block_size, x:x+block_size] = quantum_denoised[y:y+block_size, x:x+block_size]
    
    return reconstructed

