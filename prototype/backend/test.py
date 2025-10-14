from super_dense import transmit_bit_pairs, superdense_circuit_for_message, build_noise_model
from qiskit_aer import AerSimulator

pairs = ['00','01','10','11'] * 10
circuits = superdense_circuit_for_message()
backend = AerSimulator()
nm = build_noise_model(0,0,0)

received = transmit_bit_pairs(pairs, circuits, backend=backend, noise_model=nm, shots_per_pair=100)

errors = sum(p1 != p2 for p1, p2 in zip(pairs, received))
print(f"Bit errors: {errors}/{len(pairs)}")