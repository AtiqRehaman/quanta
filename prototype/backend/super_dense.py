from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError
from qiskit_aer.primitives import Sampler





def superdense_circuit_for_message():
    """
    Build a QuantumCircuit(2,2) that:
    - prepares Bell pair (q0 entangle q1)
    - Alice encodes msg2 on q0 (I, X, Z, XZ)
    - Bob decodes (CNOT, H) and measures both into two classical bits
    Returns the circuit (with measurement).
    """

    circuits = {}

    for msg2 in ['00', '01', '10', '11']:
      qc = QuantumCircuit(2, 2)
      # Entangle
      qc.h(0)
      qc.cx(0, 1)
      # Alice encode (on q0)
      if msg2 == '00':
          pass
      elif msg2 == '01':
          qc.x(0)
      elif msg2 == '10':
          qc.z(0)
      elif msg2 == '11':
          qc.z(0)
          qc.x(0)  # ZX
      else:
          raise ValueError("msg2 must be 2-bit string")
      # Bob decode
      qc.cx(0, 1)
      qc.h(0)
      qc.measure([0, 1], [0, 1])

      circuits[msg2] = qc

    return circuits

def build_noise_model(p1=0.01, p2=0.02, p_meas=0.01):
    """
    Build a simple depolarizing + readout noise model.
    p1: single-qubit depolarizing prob
    p2: two-qubit depolarizing prob
    p_meas: measurement error probability (symmetric)
    """
    nm = NoiseModel()
    e1 = depolarizing_error(p1, 1)
    e2 = depolarizing_error(p2, 2)
    nm.add_all_qubit_quantum_error(e1, ['x','z','h'])  # common single-qubit gate names
    nm.add_all_qubit_quantum_error(e2, ['cx'])
    # Simple symmetric readout error: flips 0<->1 with p_meas
    read_error = [[1 - p_meas, p_meas], [p_meas, 1 - p_meas]]
    nm.add_all_qubit_readout_error(ReadoutError(read_error))
    return nm

def transmit_bit_pairs(bit_pairs, circuits, shots_per_pair=200, noise_model=None, backend=None, batch_size=16):
    """
    Transmit a list of 2-bit strings (bit_pairs) using superdense circuits with noise model.
    For each pair, run many shots and take the most frequent measured 2-bit result (majority vote).
    Returns the decoded 2-bit strings (concatenated).
    """

    #backend = AerSimulator(noise_model=nm, method='density_matrix')

    if backend is None:
        backend = AerSimulator(noise_model=noise_model, method='density_matrix')


    qc = []

    for pair in bit_pairs:
      # circuits.append(superdense_circuit_for_message(pair))
      qc.append(circuits[pair])

        # transpile circuits
    t_circuits = transpile(qc, backend)
    decoded_pairs = []


      # run in batches to avoid huge job sizes
    for i in range(0, len(t_circuits), batch_size):
      batch = t_circuits[i:i+batch_size]
      # t_batch = transpile(batch, backend) # Already transpiled
      # run batch
      if noise_model is not None:
        job = backend.run(batch, shots=shots_per_pair, noise_model=noise_model)
      else:
          job = backend.run(batch, shots=shots_per_pair)
      res = job.result()


      # res = job.result()
      for idx in range(len(batch)):
        counts = res.get_counts(idx)
        # Qiskit counts strings in order 'c1c0'?? Qiskit returns bitstrings with c[n-1] ... c[0].
        # Our circuits measured [0,1] -> classical bits [0,1], so returned keys are like 'b1b0' with left-most bit c1
        # We'll trust that and use as-is.
        if len(counts) == 0:
          decoded = '00'
        else:
          # most frequent
          decoded = max(counts.items(), key=lambda kv: kv[1])[0]
            # decoded = max(counts, key=counts.get)
        # Qiskit returns string with left-most = c1 (most significant). We want same order b1 b0.
        decoded_pairs.append(decoded[::-1])

    # return "".join(decoded_pairs) # Return concatenated string
    return decoded_pairs