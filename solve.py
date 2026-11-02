import time
import solver

from input import sudoku, cages

time1 = time.time()
solver.run_solver(sudoku, cages)

print(time.time() - time1)
