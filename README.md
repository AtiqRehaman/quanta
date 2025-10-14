## 🧠 Hybrid Image Transmission using Superdense Coding (SDC)



**A Quantum–Classical Hybrid Communication System for Efficient and Secure Image Transmission**  
Developed for **Amaravati Quantum Valley Hackathon 2025**

---

## 🚀 Overview



This project demonstrates a **hybrid image transmission system** that intelligently combines **classical communication** with **quantum superdense coding (SDC)**.  
High-information (entropy-rich) image blocks are transmitted through a simulated quantum channel, while low-entropy blocks are sent classically.  
The receiver reconstructs the image using metadata and block information, achieving reduced bandwidth usage with preserved visual fidelity.

The project includes:

* A **Python backend** (Flask + Qiskit) for hybrid transmission simulation
* A **React frontend** for uploading images and visualizing outputs
* Parallelized quantum transmission, noise simulation, and quality metrics (PSNR, SSIM, Fidelity)

---

## 🧩 Key Features



✅ Hybrid classical–quantum image transmission  
✅ Superdense coding–based quantum block encoding  
✅ Parallel processing \& automatic batch size tuning  
✅ Realistic noise model simulation using **Qiskit Aer**  
✅ Dynamic image resizing and sharpening  
✅ Image quality evaluation: **PSNR**, **SSIM**, **Fidelity**  
✅ Visual outputs: reconstructed image, error heatmap, histogram  
✅ Full-stack demo with Flask backend and React frontend

---



---

## ⚙️ Installation \& Setup

### 🔹 Backend (Flask + Qiskit)



1. Clone the repository:

```bash
   git clone https://github.com/<your-username>/Hybrid\_Image\_Transmission.git
   cd Hybrid\_Image\_Transmission/backend
```

2. Create a virtual environment and install dependencies:
```bash
   python -m venv venv
   source venv/bin/activate  # or venv\\Scripts\\activate (Windows)
   pip install -r requirements.txt
```
3. Run the backend API:
```bash
   python app.py
```
### 🔹 Frontend (React)

1. Open another terminal:
   cd ../frontend
   npm install
   npm start
2. The frontend will run at http://localhost:3000
   Flask backend runs at http://localhost:5000

Total bit pairs transmitted: 503,040
Classical image size: 707,460 bytes
Quantum image size: 122,584 bytes
PSNR: 39.37 dB
SSIM: 0.993
Image Fidelity: 99.34%

# 📉 Limitations \& Future Work

## ⚠️ Current Limitations

* Full image quantum transmission not yet practical (limited qubits)
* SSIM may not detect localized quantum noise differences
* Real device runs limited to <16×16 pixels

## 🚀 Future Enhancements

* Integrate real IBM Quantum backend for small images
* Add block-wise fidelity metrics
* Implement entanglement purification and quantum error correction
* Extend bandwidth–fidelity optimization analysis

# 🙌 Authors \& Acknowledgements

## Authors (Students)

Sk. Atiq Rehaman · M. Surendra Reddy · J. Roja · K. Mounika · G. Sreshta Charitha · S.T.V. Mohan Reddy
**Institution**: Lakireddy Bali Reddy College of Engineering, Mylavaram

## Special Thanks To:

Faculty Mentor — Dr Y Amar Babu

Hackathon Organizer — Prof K Madhu Murthy, Chairman, APSCHE

