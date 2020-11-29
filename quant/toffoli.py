import numpy as np
from qiskit import(
  QuantumCircuit,
  execute,
  Aer)

#simulator = Aer.get_backend('qasm_simulator')
simulator = Aer.get_backend('unitary_simulator')
circuit = QuantumCircuit(2, 2)

circuit.t(1)
circuit.cx(0, 1)
for i in range(7):
   circuit.t(1)
circuit.t(0)
circuit.cx(0,1)

print("\nCircuit:\n%s" % circuit)

#circuit.measure([0,1], [0,1])

#job = execute(circuit, simulator, shots=10)
job = execute(circuit, simulator)
result = job.result()
#counts = result.get_counts(circuit)
#print("\nTotal count for 00 and 11 are:",counts)
print("\n%s" % result.get_unitary(circuit, decimals=3))
