import matplotlib.pyplot as plt
import numpy as np
from skimage.metrics import structural_similarity as ssim

plt.rcParams.update({
    # "figure.figsize": (4, 3),       # Default single-column figure size in inches
    "font.size": 14,                # Base font size
    "axes.labelsize": 16,           # Axis label size
    "axes.titlesize": 16,           # Title size
    "xtick.labelsize": 12,          # X tick labels
    "ytick.labelsize": 12,          # Y tick labels
    "legend.fontsize": 12,          # Legend font size
    "lines.linewidth": 2.0,         # Thicker lines
    "lines.markersize": 8,          # Larger markers
    "legend.loc": "best",           # Best location for legend
    "savefig.dpi": 300,             # High-resolution export
    "figure.dpi": 120               # On-screen figure clarity
})


def plot_histogram(diff):
    plt.hist(diff.flatten(), bins=50, color='b', alpha=0.7)
    plt.xlabel('Intensity')
    plt.ylabel('Frequency')
    plt.title('Histogram of Pixel Values')
    # plt.savefig('histogram.png', dpi=300)
    # plt.show()
    # plt.close()
    
def error_heatmap(diff):

    plt.imshow(diff, cmap="hot", vmin=0, vmax=50)
    plt.colorbar(label="Error Intensity")
    plt.title("Error Heatmap (Original vs Hybrid)")
    plt.axis("off")
    # plt.savefig('heat_map.png', dpi=300, bbox_inches='tight')
    # plt.show()
    # plt.close()


def block_mse(orig, recon, block_size=8):
    h, w = orig.shape
    mse_map = np.zeros((h//block_size, w//block_size))

    for i in range(0, h, block_size):
        for j in range(0, w, block_size):
            block_orig = orig[i:i+block_size, j:j+block_size]
            block_recon = recon[i:i+block_size, j:j+block_size]
            mse = np.mean((block_orig - block_recon) ** 2)
            mse_map[i//block_size, j//block_size] = mse

    # plt.imshow(mse_map, cmap="hot")
    plt.colorbar(label="Block MSE")
    plt.title("Block-wise Error Map")
    # plt.show()
    
def psnr_ssim_plots(color_cropped, reconstructed):
    # Ensure images are in correct format
    color_cropped = np.array(color_cropped, dtype=np.uint8)
    reconstructed = np.array(reconstructed, dtype=np.uint8)
    # Calculate PSNR safely to avoid divide-by-zero warnings
    # Compute MSE over all channels
    mse = np.mean((color_cropped.astype(np.float64) - reconstructed.astype(np.float64)) ** 2)
    if mse == 0:
        psnr_value = float(100.0)  # Perfect match
    else:
        psnr_value = 10 * np.log10((255.0 ** 2) / mse)
    
    # Calculate SSIM
    ssim_raw = ssim(
        color_cropped,
        reconstructed,
        win_size=7,
        gaussian_weights=True,
        sigma=1.5,
        channel_axis=2,
        data_range=255,
        K1=0.01,
        K2=0.03,
    )

    # ssim() may return a scalar or a tuple (score, full_map). Handle both.
    if isinstance(ssim_raw, tuple):
        ssim_value = ssim_raw[0]
    else:
        ssim_value = ssim_raw
    
    # Ensure numeric scalars for plotting
    psnr_value = float(psnr_value)
    try:
        ssim_value = float(np.asarray(ssim_value).item())
    except Exception:
        ssim_value = float(ssim_value)

    # Plot PSNR and SSIM
    plt.figure()
    plt.bar(["PSNR", "SSIM"], [psnr_value, ssim_value], color=["orange", "green"])
    plt.title("Quality Metrics")
    plt.ylabel("Value")
    plt.grid(True, axis='y')
    # plt.savefig('psnr_ssim.png', dpi=300, bbox_inches='tight')
    plt.close()  # Close to free memory
    
    print(f"PSNR: {psnr_value} dB")
    print(f"SSIM: {ssim_value}")

    return (psnr_value, ssim_value)
    


def plot_bandwidth_scaling(image_sizes, block_size=16, entropy_fraction=0.15):
    """
    Plot channel usage vs image size for classical vs hybrid (with SDC).

    Parameters
    ----------
    image_sizes : list of int
        Side lengths of square images (e.g. [128, 256, 512]).
    block_size : int
        Block size used for entropy partitioning (default=16).
    entropy_fraction : float
        Fraction of blocks sent via SDC (0.0 = none, 1.0 = all quantum).
    """
    classical_usage = []
    hybrid_usage = []

    for size in image_sizes:
        n_blocks = (size // block_size) ** 2
        block_bits = block_size * block_size * 8   # grayscale: 8 bits/pixel

        # All-classical: all bits transmitted directly
        total_classical = n_blocks * block_bits

        # Hybrid: some fraction sent via SDC
        quantum_blocks = int(entropy_fraction * n_blocks)
        classical_blocks = n_blocks - quantum_blocks

        classical_bits = classical_blocks * block_bits
        quantum_qubits = (quantum_blocks * block_bits) // 2  # 2 bits per qubit

        total_hybrid = classical_bits + quantum_qubits

        classical_usage.append(total_classical)
        hybrid_usage.append(total_hybrid)

    # Plot
    plt.figure(figsize=(7,5))
    plt.plot(image_sizes, classical_usage, marker='o', label="All-Classical")
    plt.plot(image_sizes, hybrid_usage, marker='s', label=f"Hybrid (SDC {int(entropy_fraction*100)}%)")
    plt.xlabel("Image size (pixels per side)")
    plt.ylabel("Channel usage (bits/qubits)")
    plt.title("Channel Usage vs Image Size")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    # plt.savefig('bandwidth_scaling.png', dpi=300)
    # plt.show()

# plot_bandwidth_scaling([128, 256, 512])

    