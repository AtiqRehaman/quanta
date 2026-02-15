from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit_aer.noise import NoiseModel, depolarizing_error
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

# --- Build a simple noise model ---
noise_model = NoiseModel()
# Add depolarizing noise on 1-qubit and 2-qubit gates
noise_model.add_all_qubit_quantum_error(depolarizing_error(0.02, 1), ['h', 'x', 'z'])
noise_model.add_all_qubit_quantum_error(depolarizing_error(0.05, 2), ['cx'])

backend = Aer.get_backend("aer_simulator")

def superdense_qiskit(msg, shots=1024):
    qc = QuantumCircuit(2)

    # Step 1: Create entanglement
    qc.h(0)
    qc.cx(0, 1)

    # Step 2: Encode message on Alice's qubit
    if msg[0] == "1":
        qc.z(0)
    if msg[1] == "1":
        qc.x(0)

    # Step 3: Send qubit & decode (apply Bell basis measurement)
    qc.cx(0, 1)
    qc.h(0)

    # Step 4: Measure both qubits
    qc.measure_all()

    # Run on noisy simulator
    qc_t = transpile(qc, backend)
    result = backend.run(qc_t, shots=shots, noise_model=noise_model).result()
    counts = result.get_counts()
    return qc, counts

# --- Run for all messages ---
all_counts = []
labels = []

for msg in ["00", "01", "10", "11"]:
    qc, counts = superdense_qiskit(msg, shots=1024)
    all_counts.append(counts)
    labels.append(msg)

# Plot noisy histograms
fig = plot_histogram(all_counts, legend=labels)
#plt.title("Superdense Coding with Noise (Local Simulation)")
#plt.show()
display(fig)