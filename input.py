def get_sudoku():
    sudoku = []

    for _ in range(9):
        row = input().split()
        row = [int(value) for value in row]
        sudoku.append(row)
    return sudoku


def get_cages():
    cages = []
    numberOfCages = int(input())
    for _ in range(numberOfCages):
        cells, value = input().split(" > ")
        cells = cells.split()

        cells = [(int(cell[1]) - 1, int(cell[0]) - 1) for cell in cells]
        cage = (int(value), cells)
        cages.append(cage)

    return cages


sudoku = get_sudoku()
cages = get_cages()
