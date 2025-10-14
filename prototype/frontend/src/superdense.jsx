import React, { useState } from "react";
import CircuitDiagram from "./CircuitDiagram";
import styles from "./superdense.module.css";

function Superdense() {
  const [selectedMessage, setSelectedMessage] = useState("00");
  const [noiseMode, setNoiseMode] = useState(false);
  const [result, setResult] = useState("");
  const [counts, setCounts] = useState(null);
  const [errorRate, setErrorRate] = useState(null);
  const [histogramImage, setHistogramImage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleMessageSelect = (msg) => {
    setSelectedMessage(msg);
  };

  const handleRunSimulation = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(
        `http://127.0.0.1:5000/api/simulate?message=${selectedMessage}&noise=${noiseMode}`
      );
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to fetch simulation data");
      }

      setCounts(data.counts);
      setErrorRate(data.errorRate);
      setHistogramImage(data.image);
      setResult(`Bob received: ${data.message}`);
    } catch (error) {
      console.error("Error fetching simulation data:", error);
      setResult("Error running simulation");
      setCounts(null);
      setErrorRate(null);
      setHistogramImage(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setResult("");
    setCounts(null);
    setErrorRate(null);
    setHistogramImage(null);
    setNoiseMode(false);
    setSelectedMessage("00");
  };

  const messages = ["00", "01", "10", "11"];

  const bellStates = {
    "00": "Φ⁺ (phi-plus) = (|00⟩ + |11⟩)/√2",
    "01": "Φ⁻ (phi-minus) = (|00⟩ - |11⟩)/√2",
    "10": "Ψ⁺ (psi-plus) = (|01⟩ + |10⟩)/√2",
    "11": "Ψ⁻ (psi-minus) = (|01⟩ - |10⟩)/√2",
  };

  const steps = [
    "Alice and Bob share an entangled Bell state (Φ⁺).",
    "Alice encodes two classical bits into her qubit using quantum gates.",
    "Depending on the message, the Bell state changes (Φ⁺, Φ⁻, Ψ⁺, Ψ⁻).",
    "Alice sends her qubit to Bob.",
    "Bob applies decoding operations (CNOT + Hadamard) and measures.",
    "The measurement reveals Alice’s two-bit classical message.",
  ];

  return (
    <div className={styles.container}>
      <div className={styles.maxWidthContainer}>
        {/* Header Placeholder - Replace with actual Header component */}
        <header className={styles.header}>
          <h1>Superdense Coding Simulation</h1>
          <p>
            Learn how to send <span className="font-bold text-blue-300">two classical bits</span> using one qubit with quantum entanglement.
          </p>
        </header>

        {/* Step by Step */}
        <div className={styles.stepSection}>
          <h2>Step-by-Step Process</h2>
          <ol>
            {steps.map((step, index) => (
              <li key={index}>{step}</li>
            ))}
          </ol>
        </div>

        {/* Bell State */}
        <div className={styles.bellState}>
          <h2>Bell State Evolution</h2>
          <p>
            Initial shared state: <span className="font-mono text-blue-300">Φ⁺</span>
          </p>
          <p className={styles.bellStateText}>
            Current Message ({selectedMessage}) → {bellStates[selectedMessage]}
          </p>
        </div>

        {/* Controls */}
        <div className={styles.controls}>
          {/* Message Selection */}
          <div className={styles.messageSelect}>
            <h2>Select Message to Send:</h2>
            <div className={styles.messageButtons}>
              {messages.map((msg) => (
                <button
                  key={msg}
                  onClick={() => handleMessageSelect(msg)}
                  className={`${styles.button} ${
                    selectedMessage === msg ? styles.selected : ""
                  }`}
                  disabled={isLoading}
                >
                  {msg}
                </button>
              ))}
            </div>
          </div>

          {/* Noise Toggle */}
          <div className={styles.noiseToggle}>
            <input
              type="checkbox"
              id="noise"
              checked={noiseMode}
              onChange={(e) => setNoiseMode(e.target.checked)}
              disabled={isLoading}
            />
            <label htmlFor="noise">Enable Noise Mode</label>
            {noiseMode && <p className={styles.noiseWarning}>⚡ Noise may affect results</p>}
          </div>

          {/* Buttons */}
          <div className={styles.buttonGroup}>
            <button
              onClick={handleRunSimulation}
              className={`${styles.button} ${styles.run}`}
              disabled={isLoading}
            >
              {isLoading ? "Running..." : "Run Simulation"}
            </button>
            <button onClick={handleReset} className={`${styles.button} ${styles.reset}`}>
              Reset
            </button>
          </div>
        </div>

        {/* Results */}
        {result && (
          <div className={styles.results}>
            <h2>Results:</h2>
            <div>{result}</div>
          </div>
        )}

        {/* Visualization */}
        <div className={styles.visualization}>
          {/* Left */}
          <div className={`${styles.circuit} ${styles.visualizationItem}`}>
            <h2>Quantum Circuit Diagram</h2>
            <CircuitDiagram message={selectedMessage} />
            {counts && (
              <div>
                <p className="font-semibold">Counts:</p>
                <pre>{JSON.stringify(counts, null, 2)}</pre>
                <p className="font-semibold mt-2">Error Rate:</p>
                <p className="text-lg font-bold text-red-300">{errorRate}%</p>
              </div>
            )}
          </div>

          {/* Right */}
          <div className={`${styles.output} ${styles.visualizationItem}`}>
            <h2>Simulation Output</h2>
            <div className={styles.imageContainer}>
              {isLoading ? (
                <p>Loading simulation...</p>
              ) : histogramImage ? (
                <img
                  src={histogramImage}
                  alt="Histogram of measurement counts"
                  className={noiseMode ? "noise" : ""}
                />
              ) : (
                <p>Click "Run Simulation" to generate histogram</p>
              )}
              {noiseMode && histogramImage && (
                <p className={styles.noiseWarning}>⚡ Noise affecting qubit</p>
              )}
            </div>
          </div>
        </div>
      </div>
      {/* Footer Placeholder - Replace with actual Footer component */}
      <footer>
        <p>© 2025 Quantum Innovations</p>
      </footer>
    </div>
  );
}

export default Superdense;