import React from 'react';
import PropTypes from 'prop-types';

function Gate({ label, x, y, color, tooltip }) {
  return (
    <g className="group">
      <rect
        x={x}
        y={y}
        width="20"
        height="20"
        fill="none"
        stroke={color}
        strokeWidth="2"
      />
      <text
        x={x + 10}
        y={y + 15}
        fontSize="12"
        fill={color}
        textAnchor="middle"
      >
        {label}
      </text>
      <title>{tooltip}</title>
    </g>
  );
}

Gate.propTypes = {
  label: PropTypes.string.isRequired,
  x: PropTypes.number.isRequired,
  y: PropTypes.number.isRequired,
  color: PropTypes.string.isRequired,
  tooltip: PropTypes.string.isRequired,
};

function CircuitDiagram({ message }) {
  const getEncodingGates = (msg) => {
    switch (msg) {
      case '00':
        return [{ type: 'I', label: 'I', tooltip: 'Identity: No operation' }];
      case '01':
        return [{ type: 'X', label: 'X', tooltip: 'Pauli-X: Bit flip' }];
      case '10':
        return [{ type: 'Z', label: 'Z', tooltip: 'Pauli-Z: Phase flip' }];
      case '11':
        return [
          { type: 'Z', label: 'Z', tooltip: 'Pauli-Z: Phase flip' },
          { type: 'X', label: 'X', tooltip: 'Pauli-X: Bit flip' },
        ];
      default:
        return [{ type: 'I', label: 'I', tooltip: 'Identity: No operation' }];
    }
  };

  const encodingGates = getEncodingGates(message);

  return (
    <svg
      viewBox="0 0 800 200"
      className="w-full h-auto border border-gray-300 rounded"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Qubit lines */}
      <line x1="50" y1="50" x2="750" y2="50" stroke="#3B82F6" strokeWidth="2" />
      <line x1="50" y1="150" x2="750" y2="150" stroke="#10B981" strokeWidth="2" />

      {/* Labels */}
      <text x="10" y="55" fontSize="12" fill="black">Alice</text>
      <text x="10" y="155" fontSize="12" fill="black">Bob</text>

      {/* Time axis */}
      <line x1="50" y1="30" x2="50" y2="170" stroke="gray" strokeWidth="1" strokeDasharray="2" />
      <text x="40" y="25" fontSize="10" fill="gray">t</text>

      {/* Bell State Creation: H on Alice */}
      <Gate
        type="H"
        label="H"
        x={100}
        y={40}
        color="#3B82F6"
        tooltip="Hadamard: Creates superposition"
      />

      {/* CNOT: Control on Alice, Target on Bob */}
      <circle cx="150" cy="50" r="3" fill="black" />
      <line x1="150" y1="50" x2="150" y2="150" stroke="black" strokeWidth="1" strokeDasharray="3" />
      <Gate
        type="X"
        label="X"
        x={145}
        y={140}
        color="#3B82F6"
        tooltip="CNOT: Entangles qubits"
      />

      {/* Alice's Encoding */}
      {encodingGates.map((gate, index) => {
        if (gate.type === 'I') return null;
        const gateX = 250 + index * 50;
        return (
          <Gate
            key={index}
            type={gate.type}
            label={gate.label}
            x={gateX}
            y={40}
            color={gate.type === 'X' ? '#EF4444' : '#10B981'}
            tooltip={gate.tooltip}
          />
        );
      })}

      {/* Transmission: Squiggly line */}
      <path
        d="M 350 50 Q 360 45 370 55 Q 380 45 390 55 Q 400 50 400 50"
        stroke="orange"
        strokeWidth="2"
        fill="none"
        strokeDasharray="5"
      />

      {/* Bob's Decoding: CNOT */}
      <circle cx="450" cy="50" r="3" fill="black" />
      <line x1="450" y1="50" x2="450" y2="150" stroke="black" strokeWidth="1" strokeDasharray="3" />
      <Gate
        type="X"
        label="X"
        x={445}
        y={140}
        color="#3B82F6"
        tooltip="CNOT: Part of decoding"
      />

      {/* H on Alice */}
      <Gate
        type="H"
        label="H"
        x={500}
        y={40}
        color="#3B82F6"
        tooltip="Hadamard: Part of decoding"
      />

      {/* Measurements */}
      <rect x="580" y="35" width="40" height="30" fill="none" stroke="red" strokeWidth="1" />
      <text x="600" y="55" fontSize="10" fill="red" textAnchor="middle">M</text>
      <rect x="580" y="135" width="40" height="30" fill="none" stroke="red" strokeWidth="1" />
      <text x="600" y="155" fontSize="10" fill="red" textAnchor="middle">M</text>

      {/* Section Labels */}
      <text x="125" y="25" fontSize="10" fill="gray">Bell State</text>
      <text x="275" y="25" fontSize="10" fill="gray">Encoding</text>
      <text x="375" y="25" fontSize="10" fill="gray">Transmit</text>
      <text x="475" y="25" fontSize="10" fill="gray">Decoding</text>
      <text x="575" y="25" fontSize="10" fill="gray">Measure</text>
    </svg>
  );
}

CircuitDiagram.propTypes = {
  message: PropTypes.string.isRequired,
};

export default CircuitDiagram;