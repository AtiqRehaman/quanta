from flask import Flask, jsonify, request
from flask_cors import CORS
import base64
from io import BytesIO
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
from qiskit.visualization import plot_histogram
from qiskit.quantum_info import Statevector

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

def add_noise():
    # ----- Noise model -----
    noise_model = NoiseModel()
    # 5% depolarizing error on 1-qubit gates
    error1 = depolarizing_error(0.1, 1)

    # 10% depolarizing error on 2-qubit gates
    error2 = depolarizing_error(0.2, 2)

    noise_model.add_all_qubit_quantum_error(error1, ['h', 'x', 'z'])
    noise_model.add_all_qubit_quantum_error(error2, ['cx'])

    # Measurement error
    meas_error = depolarizing_error(0.01, 1)  # 1% measurement error
    noise_model.add_all_qubit_quantum_error(meas_error, ['measure'])
    
    return noise_model
    

def superdense_qiskit(bits: str, shots: int = 1024, noise=False):
  """
  Simulate superdense coding for a given 2-bit string using Qiskit.
  Returns: (QuantumCircuit, counts dict)
  """
  if bits not in {"00", "01", "10", "11"}:
      raise ValueError("bits must be one of '00','01','10','11'")

  qc = QuantumCircuit(2, 2)  # qubits: [A, B], classical: [cA, cB]


  # 1) Create |Φ+> = (|00> + |11>)/√2
  qc.h(0)
  qc.cx(0, 1)

  # ----------- STEP 2: Alice's Encoding Circuit ----------

  # 2) Alice encodes b1 b0 on qubit A (qubit 0)
  if bits == "00":
      pass
  elif bits == "01":
      qc.x(0)
  elif bits == "10":
      qc.z(0)
  elif bits == "11":
      qc.x(0)
      qc.z(0)


  # 3) Alice -> Bob (conceptual; in sim it’s just the same circuit)

  # 4) Bob decodes
  qc.cx(0, 1)
  state = Statevector.from_instruction(qc)
  # state = partial_trace(state, [1])
  qc.h(0)


  # Measure to two classical bits [cA, cB].
  # Convention here: cA holds b1, cB holds b0 after decoding.
  qc.measure([0, 1], [1, 0])

#   print(qc.draw())

  noise_model = add_noise() if noise else None

  # Run with Aer qasm_simulator
  sim = AerSimulator(noise_model=noise_model, method='density_matrix')
#   qc.save_density_matrix()
  tqc = transpile(qc, sim)
  result = sim.run(tqc, shots=shots).result()
  rho = result.data(0)["density_matrix"]
  counts = result.get_counts()

  return qc, counts, state, rho

# @app.route('/api/simulate', methods=['GET'])
def simulate():
    try:
        message = request.args.get('message', '00')
        noise_str = request.args.get('noise', 'true')
        noise = noise_str.lower() == 'true'
        shots = 1024  # Fixed shots as in the code

        qc, counts, state, rho = superdense_qiskit(message, shots=shots, noise=noise)

        # Calculate error rate
        correct = counts.get(message, 0)
        error_rate = (1 - correct / shots) * 100  # As percentage

        # Generate histogram plot
        fig, ax = plt.subplots()
        plot_histogram(counts, ax=ax, title=f"Superdense Coding Histogram for Message {message} (Noise: {noise})")

        # Save plot to BytesIO and encode to Base64
        buf = BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)  # Close to free memory

        return jsonify({
            'message': message,
            'counts': counts,
            'errorRate': round(error_rate, 2),
            'image': f'data:image/png;base64,{img_base64}',
            'noise': noise
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '_main_':
    app.run(port=5000, debug=True)