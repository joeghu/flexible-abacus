FLEXIBLE ABACUS: STOCHASTIC VM & EVOLUTIONARY COMPUTING ENGINE

Flexible Abacus is a lightweight Python runtime that executes a custom stochastic Virtual Machine (VM) and optimizes programs using a genetic evolutionary algorithm. It replaces standard gradient descent with direct parameter mutations to evolve algorithms for targeted mathematical functions, such as square root estimation.

SYSTEM ARCHITECTURE

Memory Architecture: Features dynamic register banks (Cart), memory-mapped input (InTray: 256 uint8 array), and output (OutTray: 4 uint8 array).

Instruction Fetch & Execution: Uses a probabilistic selection mechanism (WhoIsNext) to fetch instructions and routing blocks (Processor, Flipper, Writer) to perform operations and state updates.

Evolutionary Optimization: Employs a challenger-based genetic loop (NewChallenger) that applies stochastic mutations to the memory state, persisting higher-scoring programs via NumPy (.npy) files.

TECHNICAL STACK

Language: Python 3

Core Libraries: NumPy (array operations, structural unpacking), Matplotlib (real-time performance tracking)

GETTING STARTED

Install dependencies: pip install numpy matplotlib

Run simulation: python flexible_abacus.py

This project demonstrates expertise in low-level memory handling, custom ISA execution pipeline design, and non-gradient optimization.
