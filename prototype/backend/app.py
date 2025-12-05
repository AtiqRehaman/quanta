from os import makedirs, remove
from os.path import join, exists
import cv2
from numpy import zeros_like, count_nonzero, sum, uint8
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from skimage.util import view_as_blocks
from matplotlib import use, pyplot as plt
use('Agg')  # Use non-interactive backend
import time
import base64
import traceback

# Assuming these modules are available
from qiskit_aer import AerSimulator
from helper import Helper
from image_utils import convert_to_png, score_image, mask_classical_blocks
from super_dense import build_noise_model_ser, superdense_circuit_for_message
from metadata import metadata as build_metadata
from reconstruct import (
    reconstruct_quantum_blocks,
    reconstruct_quantum_image,
    reconstruct_full_image,
)
from plotting import plot_histogram, error_heatmap, psnr_ssim_plots
from parallel_process import (
    block_bitpairs_list,
    auto_batch_size,
    transmit_blocks_in_parallel,
)

# Initialize helper and global objects at startup
helper = Helper()
backend = AerSimulator()
nm = build_noise_model_ser(0.0)  # Default noise model
circuits = superdense_circuit_for_message()

# Configuration
UPLOAD_FOLDER = 'Uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
makedirs(UPLOAD_FOLDER, exist_ok=True)
makedirs(OUTPUT_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app, resources={r"/process_image": {"origins": "http://localhost:3000"}})



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
        <input type="checkbox" name="use_noise" value="1"><br>
        <label for="noise_percentage">Noise Percentage (0-1):</label>
        <input type="number" name="noise_percentage" step="0.01" min="0" max="1" value="0.3"><br>
        <button type="submit">Process Image</button>
    </form>
    """

@app.route('/process_image', methods=['POST'])
def process_image():
    start_time = time.time()

    # Check if image is provided
    if 'image' not in request.files:
        return jsonify({'error': 'Image file is required'}), 400

    file = request.files['image']
    use_noise = request.form.get('use_noise') == 'true' or 'use_noise' in request.form
    noise_percentage = request.form.get('noise_percentage', '0.3')
    noise_prob = float(noise_percentage) if use_noise else 0.0

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg'}), 400

    # Save uploaded file
    filename = secure_filename(str(file.filename))
    image_path = join(UPLOAD_FOLDER, filename)
    file.save(image_path)

    # Use global nm by default, override if use_noise is True
    current_nm = build_noise_model_ser(noise_prob)

    try:
        # Load and process image
        image = cv2.imread(image_path)
        if image is None:
            return jsonify({'error': f"Image not found at path: {image_path}"}), 400
        org_h, org_w = image.shape[:2]
        if org_w > 512 or org_h > 512:
            return jsonify({'error': 'Image resolution exceeds 512x512 pixels'}), 400

        image = convert_to_png(image)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        block_size = 8
        h, w = gray.shape
        h_crop = h - h % block_size
        w_crop = w - w % block_size
        gray_cropped = gray[:h_crop, :w_crop]
        color_cropped = image[:h_crop, :w_crop]

        # Divide into blocks
        blocks = view_as_blocks(gray_cropped, block_shape=(block_size, block_size))
        color_blocks = view_as_blocks(color_cropped, block_shape=(block_size, block_size, 3))
        scores = score_image(blocks)
        k = int(0.15 * len(scores))
        top_blocks = sorted(scores, reverse=True)[:k]

        classical_image = mask_classical_blocks(color_cropped, top_blocks, block_size=block_size)
        quantum_image = zeros_like(color_cropped, dtype=uint8)

        # Quantum processing
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

        block_bitpairs = block_bitpairs_list(top_blocks, color_blocks)
        n_blocks = len(block_bitpairs)
        batch_size = auto_batch_size(n_blocks, n_jobs=4, k=3)

        received_bit_pairs = transmit_blocks_in_parallel(
            block_bitpairs, circuits, backend, current_nm,
            shots_per_pair=30,
            n_jobs=4,
            batch_size=batch_size,
        )

        metadata_full = build_metadata(blocks, top_blocks, block_size=block_size)
        quantum_reconstructed_blocks = reconstruct_quantum_blocks(
            received_bit_pairs, block_indices, pair_counts, block_shape=(block_size, block_size, 3)
        )
        quantum_image = reconstruct_quantum_image(
            quantum_reconstructed_blocks, image_shape=color_cropped.shape, block_size=block_size
        )

        

        reconstructed = reconstruct_full_image(
            metadata_full, classical_image, quantum_image, block_size=block_size
        )

        # Save images with reduced compression
        classical_path = join(OUTPUT_FOLDER, 'meta_classical_transmission.png')
        quantum_path = join(OUTPUT_FOLDER, 'meta_sdc_transmission.png')
        reconstructed_path = join(OUTPUT_FOLDER, 'meta_reconstructed.png')
        cv2.imwrite(classical_path, classical_image, [cv2.IMWRITE_PNG_COMPRESSION, 3])
        cv2.imwrite(quantum_path, quantum_image, [cv2.IMWRITE_PNG_COMPRESSION, 3])
        cv2.imwrite(reconstructed_path, reconstructed, [cv2.IMWRITE_PNG_COMPRESSION, 3])

        # Generate graphs
        diff = cv2.absdiff(color_cropped, reconstructed)
        diff_gray = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)

        fig = plt.figure()
        plot_histogram(diff_gray)
        histogram_path = join(OUTPUT_FOLDER, 'histogram.png')
        plt.savefig(histogram_path, dpi=100, bbox_inches='tight')
        plt.close(fig)

        fig = plt.figure()
        error_heatmap(diff_gray)
        heatmap_path = join(OUTPUT_FOLDER, 'heatmap.png')
        plt.savefig(heatmap_path, dpi=100, bbox_inches='tight')
        plt.close(fig)

        # Calculate metrics
        try:
            psnr_value, ssim_value = psnr_ssim_plots(color_cropped, reconstructed)
        except Exception as e:
            print(f"Error in psnr_ssim_plots: {str(e)}")
            print(traceback.format_exc())
            psnr_value, ssim_value = 0.0, 0.0
        
        coincidence_rate = 0.0
        try:
            # Coincidence counter
            coincidences = sum(image == reconstructed)
            total = color_cropped.size
            coincidence_rate = coincidences / total
            fidelity = coincidence_rate * 100 if total > 0 else 0.0
            print("Image Fidelity (Coincidence counter):", fidelity)
        except ValueError:
            # SSIM
            ssim = psnr_ssim_plots(color_cropped, reconstructed)[-1]
            total = color_cropped.size
            fidelity = ssim * 100 if total > 0 else 0.0
            print("Image Fidelity (SSIM):", fidelity)

        classical_size = count_nonzero(classical_image)
        quantum_size = count_nonzero(quantum_image)
        metrics = {
            'total_bit_pairs': len(all_bit_pairs),
            'classical_image_size': classical_size,
            'quantum_image_size': quantum_size,
            'psnr': psnr_value,
            'ssim': ssim_value,
            'image_fidelity': coincidence_rate * 100,
        }

        end_time = time.time()
        processing_time = round(end_time - start_time, 2)
        print(f"Total processing time: {processing_time}s")

        # Collect base64 images
        images = []
        for path, name in [
            (classical_path, 'meta_classical_transmission.png'),
            (quantum_path, 'meta_sdc_transmission.png'),
            (reconstructed_path, 'meta_reconstructed.png'),
            (heatmap_path, 'heatmap.png'),
            (histogram_path, 'histogram.png'),
        ]:
            with open(path, "rb") as f:
                img_data = base64.encodebytes(f.read()).decode("ascii")
            images.append({'name': name, 'data': img_data})

        # Return JSON with metrics, time, and images array
        response_data = {
            'metrics': metrics,
            'time': processing_time,
            'message': 'Image processed successfully',
            'images': images,
        }

        return jsonify(response_data)

    except Exception as e:
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up uploaded file
        if exists(image_path):
            remove(image_path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

# if __name__ == "__main__":
#     from waitress import serve
#     print("Starting production server...")
#     serve(app, host="0.0.0.0", port=5000, threads=4)