import React from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import "./App.css";

function Dv() {
  const navigate = useNavigate();

  return (
    <motion.div
      className="container"
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8 }}
    >
      <h2>Project Demonstration</h2>
      <p>
        Watch the short demo video below showcasing how quantum and classical
        channels work together in our hybrid image transmission system.
      </p>

      <div style={{ margin: "30px 0" }}>
        <video width="80%" controls style={{ borderRadius: "12px" }}>
          <source src="/demo-video.mp4" type="video/mp4" />
          Your browser does not support the video tag.
        </video>
      </div>

      <button className="card-btn" onClick={() => navigate("/demo")}>
        Try the Demo 
      </button>
    </motion.div>
  );
}

export default Dv;
