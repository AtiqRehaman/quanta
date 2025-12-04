// src/pages/Results.js
import React from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
// import "./App.css"
import "./results.css";

import img256 from "./assets/results/256_image.png";
import img512 from "./assets/results/512_image.jpg";
import img1024 from "./assets/results/1024_image.jpg";

const results = [
  {
    src: img256,
    resolution: "256 × 256",
    time: "03:46",
    qubits: "~1.05K qubits",
  },
  {
    src: img512,
    resolution: "512 × 512",
    time: "07:21",
    qubits: "~4.19K qubits",
  },
  {
    src: img1024,
    resolution: "1024 × 1024",
    time: "14:58",
    qubits: "~16.77K qubits",
  },
];

function Results() {
  return (
    <motion.div
      className="results-page"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.8 }}
    >
      <div className="results-header">
        <Link to="/" className="back-btn">
          ← Back to Home
        </Link>
        <h1>Transmission Results</h1>
        {/* <p className="subtitle">
          Quantum-Assisted Hybrid Image Communication<br />
          Block-Based Entropy Selection + Superdense Coding
        </p> */}
      </div>

      <div className="results-grid">
        {results.map((item, index) => (
          <motion.div
            key={index}
            className="result-card"
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.2, duration: 0.6 }}
            // whileHover={{ y: -10 }}
          >
            <div className="image-container">
              <img src={item.src} alt={`Result ${item.resolution}`} />
            </div>

            <div className="card-info">
              <h3>{item.resolution}</h3>
              <div className="stats">
                <div className="stat">
                  <span className="label">Transmission Time</span>
                  <span className="value time">{item.time}</span>
                </div>
                <div className="stat">
                  <span className="label">Quantum Resources</span>
                  <span className="value qubits">{item.qubits}</span>
                </div>
                
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <footer className="results-footer">
        <p>
          Amaravati Quantum Valley Hackathon 2025 • All images transmitted with
          PSNR - 38 dB and SSIM - 0.98
        </p>
      </footer>
    </motion.div>
  );
}

export default Results;