Cages = list[tuple[int, list[tuple[int, int]]]]

Board = list[list[int]]

MinMaxCache = list[list[tuple[int, int]]]

combinations_tried = 0


def find_cage_index(cages: Cages, x: int, y: int) -> int:
    """Find the index of the cage at coordinate (x, y)."""
    index = 0
    for total, fields in cages:
        if (x, y) in fields:
            return index
        index += 1


def is_same_cage(cages: Cages, x1: int, y1: int, x2: int, y2: int) -> bool:
    """Returns true if two coordinates belong to the same cage."""
    return find_cage_index(cages, x1, y1) == find_cage_index(cages, x2, y2)


def print_board(board: Board, cages: Cages) -> None:

    print("+" + "---+" * 9)
    for y in range(9):
        print("|", end="")
        sep_line = "|"
        for x in range(9):
            value = board[y][x]
            end_char = "|"
            if x < 8 and is_same_cage(cages, x, y, x + 1, y):
                end_char = " "
            if y < 8 and is_same_cage(cages, x, y, x, y + 1):
                sep_line += "   +"
            else:
                sep_line += "---+"
            print(f" {value if  value > 0 else ' '} {end_char}", end="")
        print()
        print(sep_line)


def find_taken_value(
    board: Board, cages: Cages, cage_cache: Board, x: int, y: int
) -> list[int]:
    """Find values taken, that will not be available at the cell at coordinate (x, y)."""
    taken_values = []

    # Values taken in the square
    for ty in find_square_range(y):
        for tx in find_square_range(x):
            if board[ty][tx] != 0:
                taken_values.append(board[ty][tx])

    # Values taken in cage
    total, fields = cages[cage_cache[y][x]]
    field_count = len(fields)
    for fx, fy in fields:
        val = board[fy][fx]
        if val != 0:
            total -= val
            field_count -= 1
            taken_values.append(val)

    max_value = min(total - sum([i for i in range(1, 10)][: field_count - 1]), 9)
    if max_value < 9:
        taken_values.extend(range(max_value + 1, 10))
    min_value = max(total - sum([i for i in range(9, 0, -1)][: field_count - 1]), 1)
    if min_value > 1:
        taken_values.extend(range(1, min(min_value, 10)))

    for pos in range(9):
        if board[y][pos] > 0:
            taken_values.append(board[y][pos])
        if board[pos][x] > 0:
            taken_values.append(board[pos][x])

    return taken_values


def find_minmax_value(cages: Cages, x: int, y: int) -> tuple[int, int]:
    """Find minimum and maximum possible values for a cell on the board"""
    cage_index = find_cage_index(cages, x, y)
    total, fields = cages[cage_index]
    field_count = len(fields)
    min_val = max(total - sum([i for i in range(9, 0, -1)][: field_count - 1]), 1)
    max_val = min(total - sum([i for i in range(1, 10)][: field_count - 1]), 9)
    return min_val, max_val


def find_square_range(coord: int) -> range:
    """Find the range of a square along a single axis."""
    if coord < 3:
        return range(0, 3)
    if coord < 6:
        return range(3, 6)
    return range(6, 9)


def find_next_cell(
    board: Board, cages: Cages, cage_cache: Board, previousX: int, previousY: int
) -> tuple[int, int]:
    """Find next unoccupied cell by MRV in the board, or return (-1, -1)."""

    mrv = 10
    next_cell = None
    for y in range(9):
        for x in range(9):
            if y != previousY or x != previousX:
                if board[y][x] == 0:
                    temp = 9 - len(find_taken_value(board, cages, cage_cache, x, y))
                    if temp < mrv:
                        mrv = temp
                        next_cell = (x, y)
    if not next_cell:
        return -1, -1
    return next_cell


def validate_rows(board: Board) -> bool:
    """Validates rows on the board, verifying that no duplicates exist on a single row."""
    for col in range(9):
        row_set = set()
        for row in range(9):
            value = board[row][col]
            if value != 0:
                if value in row_set:
                    return False
                row_set.add(value)
    return True


def validate_cols(board: Board) -> bool:
    """Validates columns on the board, verifying that no duplicates exist on a single column."""
    for row in range(9):
        col_set = set()
        for value in board[row]:
            if value != 0:
                if value in col_set:
                    return False
                col_set.add(value)
    return True


def validate_squares(board: Board) -> bool:
    """Validates squares on the board, verifying that no duplicates exist on a square."""
    for nonet_x in range(0, 9, 3):
        range_x = find_square_range(nonet_x)
        for nonet_y in range(0, 9, 3):
            nonet_set = set()
            for y in find_square_range(nonet_y):
                for x in range_x:
                    value = board[y][x]
                    if value != 0:
                        if value in nonet_set:
                            return False
                        nonet_set.add(value)
    return True


def validate_cages(board: Board, cages: Cages) -> bool:
    """Validates all cages, verifying that no duplicates exist in these, and that the sum equals
    cage desired total.

    """
    for total, fields in cages:
        cage_set = set()
        for x, y in fields:
            value = board[y][x]
            if value != 0:
                if value in cage_set:
                    return False
                cage_set.add(value)
        if len(cage_set) == len(fields):
            if sum(cage_set) != total:
                return False
    return True


def validate(board: Board, cages: Cages) -> bool:
    """Validate the columns, rows, squares and cages on the board."""

    return (
        validate_cols(board)
        and validate_rows(board)
        and validate_squares(board)
        and validate_cages(board, cages)
    )


def fill_out_next(
    board: Board,
    cages: Cages,
    cage_cache: Board,
    minmax_cache: MinMaxCache,
    x: int,
    y: int,
) -> bool:
    """Fill out the next value on the board, and if all values are filled out validate the board."""

    global combinations_tried
    combinations_tried += 1

    next_x, next_y = find_next_cell(board, cages, cage_cache, x, y)
    taken_values = find_taken_value(board, cages, cage_cache, x, y)

    min_value, max_value = minmax_cache[y][x]
    for value in range(min_value, max_value + 1):
        if value not in taken_values:
            board[y][x] = value
            if next_x == -1:
                success = validate(board, cages)
                if not success:
                    board[y][x] = 0
                return success
            if fill_out_next(board, cages, cage_cache, minmax_cache, next_x, next_y):
                return True
    board[y][x] = 0
    return False


def solve(board: Board, cages: Cages) -> bool:
    """Solve Sudoku from board and cages"""

    cage_cache = []
    minmax_cache = []
    for y in range(9):
        cage_row = []
        minmax_row = []
        for x in range(9):
            cage_row.append(find_cage_index(cages, x, y))
            minmax_row.append(find_minmax_value(cages, x, y))
        cage_cache.append(cage_row)
        minmax_cache.append(minmax_row)

    for total, fields in cages:
        if len(fields) == 1:
            x, y = fields[0]
            board[y][x] = total

    next_x, next_y = find_next_cell(board, cages, cage_cache, x, y)

    return fill_out_next(board, cages, cage_cache, minmax_cache, next_x, next_y)


def run_solver(board, cages) -> None:
    """Run the board solver for a list files."""

    global combinations_tried
    combinations_tried = 0

    print("Calculating...")
    success = solve(board, cages)
    if success:
        print("SUCCESS")
        print_board(board, cages)
    else:
        print("NO")

    print(combinations_tried)
