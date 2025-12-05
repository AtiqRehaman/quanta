from helper import Helper
import image_utils
import super_dense
import metadata
import reconstruct
import plotting
import parallel_process

import cv2
import json
import numpy as np
from skimage.util import view_as_blocks
# from skimage.measure import shannon_entropy
# import matplotlib.pyplot as plt
import time
# from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from matplotlib import pyplot as plt

helper = Helper()

# -------------------------------
# Main function
# -------------------------------
image_path = "prototype/backend/images/letter.jpg"
# noise_params=(0.3, 0.2, 0.3) # (p1, p2, p_meas)
# noise_params=None # (p1, p2, p_meas)
noise_params = (0.6, 0.4, 0.5)
# -------------------------------
# Load image
# -------------------------------
start_time = time.time()
image = cv2.imread(image_path)
if image is None:
    raise FileNotFoundError(f"Image not found at path: {image_path}")
org_h, org_w = image.shape[:2]

image = image_utils.convert_to_png(image)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

new_size = image_utils.aspect_size(image)
# image = cv2.resize(image, new_size, interpolation=cv2.INTER_LANCZOS4)
# gray = cv2.resize(gray, new_size, interpolation=cv2.INTER_LANCZOS4)

block_size = 8
h, w = gray.shape
h_crop = h - h % block_size
w_crop = w - w % block_size
gray_cropped = gray[:h_crop, :w_crop]
color_cropped = image[:h_crop, :w_crop]


# Divide into blocks
blocks = view_as_blocks(gray_cropped, block_shape=(block_size, block_size))
color_blocks = view_as_blocks(color_cropped, block_shape=(block_size, block_size, 3))

scores = image_utils.score_image(blocks)

# Select top-k blocks (e.e.g., top 15%)
k = int(0.15 * len(scores))
top_blocks = sorted(scores, reverse=True)[:k]

classical_image = image_utils.mask_classical_blocks(color_cropped, top_blocks, block_size=block_size)

quantum_image = np.zeros_like(color_cropped, dtype=np.uint8)
if noise_params is not None:
    nm = super_dense.build_noise_model(*noise_params)
else:
    nm = None

backend = AerSimulator()
circuits = super_dense.superdense_circuit_for_message()

quantum_reconstructed_blocks = {}
all_bit_pairs = []
block_indices = []
pair_counts = []

for _, i, j in top_blocks:
    block = color_blocks[i, j]
    bit_pairs = helper.img_to_bitstream(block)  # List of bit pair strings
    bit_pairs = helper.pad_bitstring_to_even_pairs(bit_pairs)
    bit_pairs = helper.chunk_bits_by2(bit_pairs)
    all_bit_pairs.extend(bit_pairs)
    block_indices.append((i, j))
    pair_counts.append(len(bit_pairs)) 
# Transmit all bit pairs

metadata_full = metadata.metadata(blocks, top_blocks, block_size=block_size)


# Simulate SDC for all bit pairs at once
print(f"Total bit pairs to transmit: {len(all_bit_pairs)}")
# received_bit_pairs = super_dense.transmit_bit_pairs(
#     all_bit_pairs, circuits=circuits, noise_model=nm, backend=backend
# )
block_bitpairs_list = parallel_process.block_bitpairs_list(top_blocks, color_blocks)
n_blocks = len(block_bitpairs_list)
batch_size = parallel_process.auto_batch_size(n_blocks, n_jobs=4, k=3)
print(f"Batch size: {batch_size}")

# Run transmission in parallel
received_bit_pairs = parallel_process.transmit_blocks_in_parallel(
    block_bitpairs_list, circuits, backend, nm,
    shots_per_pair=100, n_jobs=4, batch_size=batch_size
)

print(f"Received bit pairs: {len(received_bit_pairs)}")
end_time = time.time()
time_diff = end_time - start_time
minutes = time_diff / 60
print(f"Transmission time: {time_diff:.2f} seconds ({minutes:.2f} minutes)")

# Save metadata to JSON (simulate classical channel)
with open("metadata.json", "w") as f:
    json.dump(metadata_full, f, indent=4)

print("Metadata saved to metadata.json")

quantum_reconstructed_blocks = reconstruct.reconstruct_quantum_blocks(
    received_bit_pairs, block_indices, pair_counts, block_shape=(block_size, block_size, 3)
)

quantum_image = reconstruct.reconstruct_quantum_image(
    quantum_reconstructed_blocks, image_shape=color_cropped.shape, block_size=block_size
)

# quantum_denoised = quantum_image.copy()
# for _, i, j in top_blocks:
#     y = i * block_size
#     x = j * block_size
#     # Apply denoising only to quantum blocks
#     block = quantum_image[y:y+block_size, x:x+block_size]
#     denoised_block = cv2.fastNlMeansDenoisingColored(block, None, 10, 10, 7, 21)
#     quantum_denoised[y:y+block_size, x:x+block_size] = denoised_block
    
reconstructed = reconstruct.reconstruct_full_image(
    metadata_full, classical_image, quantum_image, block_size=block_size
)

# -------------------------------
# Save outputs
# -------------------------------
# classical_resized = cv2.resize(classical_image, (org_w, org_h), interpolation=cv2.INTER_CUBIC)
# quantum_resized   = cv2.resize(quantum_image, (org_w, org_h), interpolation=cv2.INTER_CUBIC)
# reconstructed_resized = cv2.resize(reconstructed, (org_w, org_h), interpolation=cv2.INTER_CUBIC)

cv2.imwrite('meta_classical_transmission.png', classical_image)
cv2.imwrite('meta_sdc_transmission.png', quantum_image)
cv2.imwrite('meta_reconstructed.png', reconstructed)


print(f"Classical image size:{np.count_nonzero(classical_image)}")
print(f"Quantum image size:{np.count_nonzero(quantum_image)}")
print("Hybrid transmission simulated and image reconstructed successfully.")

diff = cv2.absdiff(color_cropped, reconstructed)
diff_gray = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)
plotting.plot_histogram(diff_gray)
plotting.error_heatmap(diff_gray)

try:
    # Coincidence counter
    coincidences = np.sum(image == reconstructed)
    total = color_cropped.size
    coincidence_rate = coincidences / total
    fidelity = coincidence_rate * 100 if total > 0 else 0.0
    print("Image Fidelity (Coincidence counter):", fidelity)
except ValueError:
    # SSIM
    ssim = plotting.psnr_ssim_plots(color_cropped, reconstructed)[-1]
    total = color_cropped.size
    fidelity = ssim * 100 if total > 0 else 0.0
    print("Image Fidelity (SSIM):", fidelity)
    

# plotting.plot_bandwidth_scaling([256, 512, 1024, 2048], block_size=16, entropy_fraction=0.15)

# plt.style.use('seaborn-v0_8-white')
# fig, axes = plt.subplots(1, 2, figsize=(10, 5))

# axes[0].imshow(reconstructed_resized)
# axes[0].set_title('Reconstructed Image')
# axes[0].axis('off')

# # Heatmap with proper color scaling
# im = axes[1].imshow(diff_gray, cmap='hot', vmin=0, vmax=50)
# axes[1].set_title('Error Heatmap (Original vs Hybrid)')
# axes[1].axis('off')

# # # Add shared colorbar
# # cbar = fig.colorbar(im, ax=axes.ravel().tolist(), orientation='horizontal', fraction=0.05, pad=0.05)
# # cbar.set_label('Error Intensity')

# plt.tight_layout()
# plt.savefig('recon_heatmap_sidebyside.png', dpi=300, bbox_inches='tight')
# plt.show()