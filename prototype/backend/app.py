import os
import cv2
import json
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import zipfile
from io import BytesIO
from skimage.util import view_as_blocks
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
from matplotlib import pyplot as plt
import time
import base64
import traceback

# Assuming these modules are available
from helper import Helper
import image_utils
import super_dense
import metadata
import reconstruct
import plotting
import parallel_process
from qiskit_aer import AerSimulator

app = Flask(__name__)
CORS(app, resources={r"/process_image": {"origins": "http://localhost:3000"}})

# Initialize helper
helper = Helper()

# Configuration
UPLOAD_FOLDER = 'Uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return """
    <h1>Image Processor</h1>
    <form action="/process_image" method="POST" enctype="multipart/form-data">
        <label for="image">Upload Image:</label>
        <input type="file" name="image" accept=".png,.jpg,.jpeg" required><br>
        <label for="use_noise">Use Noise:</label>
        <input type="checkbox" name="use_noise" value="true"><br>
        <button type="submit">Process Image</button>
    </form>
    """

@app.route('/process_image', methods=['POST'])
def process_image():
    start_time = time.time()
    print("Starting image processing...")

    # Check if image and noise parameter are provided
    if 'image' not in request.files or 'use_noise' not in request.form:
        return jsonify({'error': 'Image file and use_noise parameter are required'}), 400

    file = request.files['image']
    use_noise = request.form.get('use_noise', default='false').lower() == 'true'

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg'}), 400

    # Save uploaded file
    filename = secure_filename(file.filename)
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(image_path)

    # Noise parameters based on boolean
    noise_params = (0.2, 0.3, 0.2) if use_noise else (0.0, 0.0, 0.0)

    try:
        # Load and process image
        t1 = time.time()
        print("Loading image...")
        image = cv2.imread(image_path)
        if image is None:
            return jsonify({'error': f"Image not found at path: {image_path}"}), 400
        org_h, org_w = image.shape[:2]
        print(f"Image size: {org_w}x{org_h}")
        if org_w > 512 or org_h > 512:
            return jsonify({'error': 'Image resolution exceeds 512x512 pixels'}), 400
        print(f"Image loading time: {(time.time() - t1):.2f}s")

        t2 = time.time()
        image = image_utils.convert_to_png(image)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        new_size = image_utils.aspect_size(image)
        block_size = 8
        h, w = gray.shape
        h_crop = h - h % block_size
        w_crop = w - w % block_size
        gray_cropped = gray[:h_crop, :w_crop]
        color_cropped = image[:h_crop, :w_crop]
        print(f"Image preprocessing time: {(time.time() - t2):.2f}s")

        # Divide into blocks
        t3 = time.time()
        print("Dividing into blocks...")
        blocks = view_as_blocks(gray_cropped, block_shape=(block_size, block_size))
        color_blocks = view_as_blocks(color_cropped, block_shape=(block_size, block_size, 3))
        scores = image_utils.score_image(blocks)
        k = int(0.15 * len(scores))
        top_blocks = sorted(scores, reverse=True)[:k]
        print(f"Block division time: {(time.time() - t3):.2f}s")

        t4 = time.time()
        classical_image = image_utils.mask_classical_blocks(color_cropped, top_blocks, block_size=block_size)
        quantum_image = np.zeros_like(color_cropped, dtype=np.uint8)
        print(f"Classical image masking time: {(time.time() - t4):.2f}s")

        # Quantum processing
        t5 = time.time()
        print("Building quantum circuits...")
        nm = super_dense.build_noise_model(*noise_params)
        backend = AerSimulator(noise_model=nm)
        circuits = super_dense.superdense_circuit_for_message()
        print(f"Circuit building time: {(time.time() - t5):.2f}s")

        t6 = time.time()
        all_bit_pairs = []
        block_indices = []
        pair_counts = []
        for _, i, j in top_blocks:
            block = color_blocks[i, j]
            bit_pairs = helper.img_to_bitstream(block)
            bit_pairs = helper.pad_bitstring_to_even_pairs(bit_pairs)
            bit_pairs = helper.chunk_bits_by2(bit_pairs)
            all_bit_pairs.extend(bit_pairs)
            block_indices.append((i, j))
            pair_counts.append(len(bit_pairs))
        print(f"Total bit pairs: {len(all_bit_pairs)}")
        block_bitpairs_list = parallel_process.block_bitpairs_list(top_blocks, color_blocks)
        n_blocks = len(block_bitpairs_list)
        batch_size = parallel_process.auto_batch_size(n_blocks, n_jobs=4, k=3)
        print(f"Batch size: {batch_size}")
        print(f"Bit pair preparation time: {(time.time() - t6):.2f}s")

        t7 = time.time()
        print("Transmitting bit pairs...")
        received_bit_pairs = parallel_process.transmit_blocks_in_parallel(
            block_bitpairs_list, circuits, backend, nm,
            shots_per_pair=50, n_jobs=4, batch_size=batch_size
        )
        print(f"Received bit pairs: {len(received_bit_pairs)}")
        print(f"Quantum transmission time: {(time.time() - t7):.2f}s")

        t8 = time.time()
        metadata_full = metadata.metadata(blocks, top_blocks, block_size=block_size)
        quantum_reconstructed_blocks = reconstruct.reconstruct_quantum_blocks(
            received_bit_pairs, block_indices, pair_counts, block_shape=(block_size, block_size, 3)
        )
        quantum_image = reconstruct.reconstruct_quantum_image(
            quantum_reconstructed_blocks, image_shape=color_cropped.shape, block_size=block_size
        )
        print(f"Quantum reconstruction time: {(time.time() - t8):.2f}s")

        t9 = time.time()
        print("Denoising quantum image...")
        quantum_denoised = quantum_image.copy()
        for _, i, j in top_blocks:
            y = i * block_size
            x = j * block_size
            block = quantum_image[y:y+block_size, x:x+block_size]
            denoised_block = cv2.fastNlMeansDenoisingColored(block, None, 10, 10, 7, 21)
            quantum_denoised[y:y+block_size, x:x+block_size] = denoised_block
        print(f"Denoising time: {(time.time() - t9):.2f}s")

        t10 = time.time()
        reconstructed = reconstruct.reconstruct_full_image(
            metadata_full, classical_image, quantum_denoised, block_size=block_size
        )
        print(f"Full image reconstruction time: {(time.time() - t10):.2f}s")

        # Resize images
        t11 = time.time()
        print("Resizing and saving images...")
        classical_resized = cv2.resize(classical_image, (org_w, org_h), interpolation=cv2.INTER_CUBIC)
        quantum_resized = cv2.resize(quantum_image, (org_w, org_h), interpolation=cv2.INTER_CUBIC)
        reconstructed_resized = cv2.resize(reconstructed, (org_w, org_h), interpolation=cv2.INTER_CUBIC)

        # Save output images as PNG
        classical_path = os.path.join(OUTPUT_FOLDER, 'meta_classical_transmission.png')
        quantum_path = os.path.join(OUTPUT_FOLDER, 'meta_sdc_transmission.png')
        reconstructed_path = os.path.join(OUTPUT_FOLDER, 'meta_reconstructed.png')
        cv2.imwrite(classical_path, classical_resized, [cv2.IMWRITE_PNG_COMPRESSION, 9])
        cv2.imwrite(quantum_path, quantum_resized, [cv2.IMWRITE_PNG_COMPRESSION, 9])
        cv2.imwrite(reconstructed_path, reconstructed_resized, [cv2.IMWRITE_PNG_COMPRESSION, 9])
        print(f"Image resizing and saving time: {(time.time() - t11):.2f}s")

        # Generate graphs
        t12 = time.time()
        print("Generating graphs...")
        diff = cv2.absdiff(color_cropped, reconstructed)
        diff_gray = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)

        plt.style.use('seaborn-v0_8-white')
        fig, axes = plt.subplots(1, 2, figsize=(10, 5))
        axes[0].imshow(reconstructed_resized)
        axes[0].set_title('Reconstructed Image')
        axes[0].axis('off')
        im = axes[1].imshow(diff_gray, cmap='hot', vmin=0, vmax=50)
        axes[1].set_title('Error Heatmap (Original vs Hybrid)')
        axes[1].axis('off')
        plt.tight_layout()
        recon_heatmap_path = os.path.join(OUTPUT_FOLDER, 'recon_heatmap_sidebyside.png')
        plt.savefig(recon_heatmap_path, dpi=100, bbox_inches='tight')
        plt.close(fig)

        fig = plt.figure()
        plotting.plot_histogram(diff_gray)
        histogram_path = os.path.join(OUTPUT_FOLDER, 'histogram.png')
        plt.savefig(histogram_path, dpi=100, bbox_inches='tight')
        plt.close(fig)
        print(f"Graph generation time: {(time.time() - t12):.2f}s")

        # Calculate metrics
        t13 = time.time()
        print("Calculating metrics...")
        try:
            psnr_value, ssim_value = plotting.psnr_ssim_plots(color_cropped, reconstructed)
        except Exception as e:
            print(f"Error in psnr_ssim_plots: {str(e)}")
            print(traceback.format_exc())
            psnr_value, ssim_value = 0.0, 0.0
        classical_size = np.count_nonzero(classical_image)
        quantum_size = np.count_nonzero(quantum_image)
        metrics = {
            'total_bit_pairs': len(all_bit_pairs),
            'classical_image_size': classical_size,
            'quantum_image_size': quantum_size,
            'psnr': psnr_value,
            'ssim': ssim_value,
            'image_fidelity_ssim': ssim_value * 100
        }
        print(f"Metrics calculation time: {(time.time() - t13):.2f}s")

        # Collect base64 images
        t14 = time.time()
        print("Encoding images to base64...")
        images = []
        for path, name in [
            (classical_path, 'meta_classical_transmission.png'),
            (quantum_path, 'meta_sdc_transmission.png'),
            (reconstructed_path, 'meta_reconstructed.png'),
            (recon_heatmap_path, 'recon_heatmap_sidebyside.png'),
            (histogram_path, 'histogram.png')
        ]:
            with open(path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')
            images.append({'name': name, 'data': img_data})
            print(f"{name} base64 size: {len(img_data) / 1024:.2f} KB")
        print(f"Base64 encoding time: {(time.time() - t14):.2f}s")

        end_time = time.time()
        processing_time = round(end_time - start_time, 2)
        print(f"Total processing time: {processing_time}s")

        # Return JSON with metrics, time, and images array
        response_data = {
            'metrics': metrics,
            'time': processing_time,
            'message': 'Image processed successfully',
            'images': images
        }

        print("Sending response...")
        return jsonify(response_data)

    except Exception as e:
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up uploaded file
        if os.path.exists(image_path):
            os.remove(image_path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)