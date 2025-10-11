import React from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import "./App.css";

function Home() {
  return (
    <motion.div
      className="container"
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8 }}
    >
      <h1>Amaravati Quantum Valley Hackathon 2025</h1>
      <h2> Quantum-Assisted Hybrid Image Communication with Block-Based Entropy Selection</h2>
      <p>
       A hybrid image transmission system combining quantum Superdense Coding (SDC) and classical channels for efficient, reliable, and secure image delivery.
      </p>
      <Link to="/About">
        <button>About ➤</button>
      </Link>
    </motion.div>
  );
}

export default Home;
