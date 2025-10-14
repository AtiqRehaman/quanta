import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import { motion } from "framer-motion";
import Home from "./Home";
import About from "./About"; 
import Demo from "./Demo";
import Dv from "./Dv";
import "./App.css";
import Superdense from "./superdense";


function App() {
  return (
    <Router>

      <motion.nav
        initial={{ y: -80, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8 }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <img src="/logo.png" alt="Hackathon Logo" />
          <h3>Hybrid Image Processor</h3>
        </div>

        <div className="nav-links">
          <Link to="/">Home</Link> &nbsp; | &nbsp;
          <Link to="/about">About</Link> &nbsp; | &nbsp;
          <Link to="/demo">Demo</Link>
        </div>
      </motion.nav>

      {/* 🌟 Page Routes */}
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} /> 
        <Route path="/dv" element={<Dv />} />
        <Route path="/demo" element={<Demo />} />
        <Route path="/superdense" element={<Superdense />} />
      </Routes>

      {/* 👣 Footer Section */}
      <motion.div
        className="footer"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
      >
        <p>
          Made with ❤️ by <strong>Team Quanta – AQVH 2025</strong> <br />
          Members: Sk. Atiq Rehaman | G. Sreshta Charitha | M. Surendra Reddy | J. Roja | K. Mounika | S.T.V Mohan Reddy <br />
          <em>Lakireddy Bali Reddy College of Engineering, Mylavaram</em>
        </p>
      </motion.div>
    </Router>
  );
}

export default App;
