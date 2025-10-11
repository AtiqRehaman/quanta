import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./App.css";

function About() {
  const [openIndex, setOpenIndex] = useState(null);
  const navigate = useNavigate();

  const cards = [
    {
      title: "Superdense Coding",
      short: "Quantum technique allowing two classical bits to be sent using one qubit.",
      long: "Superdense Coding is a fundamental quantum communication protocol that exploits the phenomenon of quantum entanglement to enhance information transfer efficiency. In this scheme, an entangled qubit pair is pre-shared between the sender and receiver. By applying one of four distinct unitary operations to their qubit, the sender can encode two classical bits of information into a single qubit. Upon transmission, the receiver performs a joint measurement on the two entangled qubits to decode the message."
    },
    {
      title: "Problem Statement",
      short: "Transmitting images efficiently across hybrid (quantum + classical) networks.",
      long: "Classical communication networks often encounter bandwidth and performance limitations when transmitting large or complex datasets, particularly high-entropy information such as detailed images or videos. Quantum communication, in contrast, provides exceptional efficiency, parallelism, and data security by utilizing principles like superposition and entanglement. However, the technology is still in its developmental phase and not yet feasible for complete real-world replacement of classical systems."
    },
    {
      title: "Proposed Solution",
      short: "A hybrid model using block-wise entropy analysis and quantum-assisted transmission.",
      long: ` The image is divided into small blocks for efficient processing and localized analysis.
 Entropy is calculated for each block to measure its information content.
 High-entropy blocks represent complex and information-rich regions of the image.
 These high-entropy blocks are transmitted using Superdense Coding (SDC) via quantum channels.
 Low-entropy blocks with simple or repetitive data are sent through classical channels.
 This hybrid model combines the strengths of both quantum and classical communication.
 It ensures optimized bandwidth utilization and faster data transfer.
 The approach enhances overall reliability, efficiency, and error resilience across networks.`
    }
  ];

  const toggleCard = (index) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <div className="about-wrap">
      <div className="about-header">
        <h1>About Our Project</h1>
        <p className="about-sub">
          Hybrid Quantum-Classical Communication for Efficient Image Transmission
        </p>
      </div>

      <div className="cards-grid">
        {cards.map((card, index) => (
          <div
            key={index}
            className={`card ${openIndex === index ? "is-open" : ""}`}
          >
            <div className="card-body">
              <h3 className="card-title">{card.title}</h3>
              <p className="card-short">{card.short}</p>

              {openIndex === index && (
                <div className="card-more">
                  {card.title === "Proposed Solution" ? (
                    <ul className="card-long">
                      {card.long.split("\n").map((point, i) => (
                        <li key={i}>{point.trim()}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className="card-long" style={{ whiteSpace: "pre-line" }}>
                      {card.long}
                    </p>
                  )}
                </div>
              )}

              <button className="card-btn" onClick={() => toggleCard(index)}>
                {openIndex === index ? "Read Less ▲" : "Read More ▼"}
              </button>
            </div>
          </div>
        ))}
      </div>

      <div style={{ marginTop: "40px" }}>
        <button className="card-btn" onClick={() => navigate("/dv")}>
          Explore More ▶
        </button>
      </div>
    </div>
  );
}

export default About;
