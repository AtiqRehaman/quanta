import base64
from joblib import Parallel, delayed
import math
import multiprocessing
from super_dense import transmit_bit_pairs
from helper import Helper
helper = Helper()


def encode_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")
    

def transmit_blocks_in_parallel(block_bitpairs_list, circuits, backend, noise_model, shots_per_pair=200, n_jobs=4, batch_size=50):
    """
    Transmit quantum blocks in parallel batches.
    
    Parameters
    ----------
    block_bitpairs_list : list
        List of lists of bit_pairs for each block.
    circuits : dict
        Pre-built SDC circuits.
    backend : AerSimulator
        Qiskit backend.
    noise_model : NoiseModel
        Noise model for transmission.
    shots_per_pair : int
        Shots per circuit.
    n_jobs : int
        Number of parallel processes (CPU cores).
    batch_size : int
        Number of blocks to send together in one job.
    
    Returns
    -------
    all_decoded_pairs : list
        Flattened list of decoded bit pairs for all blocks.
    """
    
    # Split blocks into batches
    num_batches = math.ceil(len(block_bitpairs_list) / batch_size)
    batches = [
        block_bitpairs_list[i*batch_size : (i+1)*batch_size]
        for i in range(num_batches)
    ]
    
    def process_batch(batch):
        decoded_batch = []
        for bit_pairs in batch:
            decoded_pairs = transmit_bit_pairs(
                bit_pairs, circuits, shots_per_pair=shots_per_pair, noise_model=noise_model,
                backend=backend
            )
            decoded_batch.extend(decoded_pairs)
        return decoded_batch

    # Run batches in parallel
    results = Parallel(n_jobs=n_jobs)(
        delayed(process_batch)(batch) for batch in batches
    )
    
    # Flatten results, skipping any None values
    all_decoded_pairs = [pair for decoded in results if decoded is not None for pair in decoded]
    return all_decoded_pairs

def block_bitpairs_list(top_blocks, color_blocks):
    block_bitpairs_list = []
    for _, i, j in top_blocks:
        block = color_blocks[i, j]
        bits = helper.img_to_bitstream(block)
        bits = helper.pad_bitstring_to_even_pairs(bits)
        bit_pairs = helper.chunk_bits_by2(bits)
        block_bitpairs_list.append(bit_pairs)
    return block_bitpairs_list

def auto_batch_size(n_blocks, n_jobs=None, k=3):
    if n_jobs is None:
        n_jobs = multiprocessing.cpu_count() // 2  # safe default
    n_batches = n_jobs * k
    batch_size = math.ceil(n_blocks / n_batches)
    return batch_size