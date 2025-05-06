# app/layout_optimizer.py

import random
from collections import deque


def generate_layout_template(width, height, cell_size):
    """
    Generate a basic layout grid template for the store.
    """
    try:
        rows = int(height / cell_size)
        cols = int(width / cell_size)
        layout = [[{'type': 'Walkway', 'x': x, 'y': y} for x in range(cols)] for y in range(rows)]

        # Example: Add default entrance in top-left
        layout[0][0]['type'] = 'Door'

        return {
            'grid': layout,
            'rows': rows,
            'cols': cols,
            'cell_size': cell_size
        }
    except Exception as e:
        return {'error': str(e)}


def is_within_bounds(x, y, rows, cols):
    return 0 <= x < cols and 0 <= y < rows


def get_neighbors(x, y):
    return [(x + dx, y + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]


def count_adjacent_type(layout, x, y, rows, cols, target_type):
    return sum(
        1 for nx, ny in get_neighbors(x, y)
        if is_within_bounds(nx, ny, rows, cols) and layout[ny][nx]['type'] == target_type
    )


def ensure_walkways(layout, rows, cols):
    for y in range(1, rows - 1):
        if all(layout[y][x]['type'] != 'Walkway' for x in range(cols)):
            x = random.randint(1, cols - 2)
            layout[y][x]['type'] = 'Walkway'
    for x in range(1, cols - 1):
        if all(layout[y][x]['type'] != 'Walkway' for y in range(rows)):
            y = random.randint(1, rows - 2)
            layout[y][x]['type'] = 'Walkway'


def find_door_locations(layout, rows, cols):
    return [(x, y) for y in range(rows) for x in range(cols) if layout[y][x]['type'] == 'Door']


def get_adjacent_cells(x, y, rows, cols):
    return [(nx, ny) for nx, ny in get_neighbors(x, y) if is_within_bounds(nx, ny, rows, cols)]


def is_walkway_connected(layout, rows, cols):
    visited = set()
    walkways = [(x, y) for y in range(rows) for x in range(cols) if layout[y][x]['type'] == 'Walkway']
    if not walkways:
        return True

    queue = deque([walkways[0]])
    visited.add(walkways[0])

    while queue:
        x, y = queue.popleft()
        for nx, ny in get_neighbors(x, y):
            if is_within_bounds(nx, ny, rows, cols):
                if layout[ny][nx]['type'] == 'Walkway' and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))

    return len(visited) == len(walkways)


def find_valid_cashier_spots(layout, door_locs, rows, cols):
    cashier_spots = []
    for dx, dy in door_locs:
        for x, y in get_adjacent_cells(dx, dy, rows, cols):
            if layout[y][x]['type'] == 'Walkway':
                # Ensure surrounding cells are only Door/Walkway/Cashier
                valid = True
                for nx, ny in get_neighbors(x, y):
                    if is_within_bounds(nx, ny, rows, cols):
                        ntype = layout[ny][nx]['type']
                        if ntype not in ['Door', 'Walkway', 'Cashier']:
                            valid = False
                            break
                if valid:
                    cashier_spots.append((x, y))
    return cashier_spots


def place_cashiers(layout, door_locs, rows, cols):
    cashier_spots = find_valid_cashier_spots(layout, door_locs, rows, cols)
    used = set()
    for x, y in cashier_spots:
        if (x, y) not in used:
            layout[y][x]['type'] = 'Cashier'
            used.add((x, y))
            if len(used) >= 2:
                break


def is_valid_zone_placement(layout, x, y, rows, cols, avoid_types):
    return all(
        is_within_bounds(nx, ny, rows, cols) and layout[ny][nx]['type'] not in avoid_types
        for nx, ny in get_neighbors(x, y)
    )


def place_zone(layout, rows, cols, zone_type, avoid_types, size=1, connected=False):
    tries = 1000
    while tries > 0:
        tries -= 1
        x = random.randint(1, cols - 2)
        y = random.randint(1, rows - 2)

        if layout[y][x]['type'] != 'Walkway':
            continue
        if count_adjacent_type(layout, x, y, rows, cols, 'Walkway') < 3:
            continue
        if not is_valid_zone_placement(layout, x, y, rows, cols, avoid_types):
            continue

        if connected and size > 1:
            cluster = [(x, y)]
            for _ in range(size - 1):
                candidates = [
                    (nx, ny) for cx, cy in cluster
                    for nx, ny in get_neighbors(cx, cy)
                    if is_within_bounds(nx, ny, rows, cols)
                       and layout[ny][nx]['type'] == 'Walkway'
                       and (nx, ny) not in cluster
                       and is_valid_zone_placement(layout, nx, ny, rows, cols, avoid_types)
                ]
                if not candidates:
                    break
                cluster.append(random.choice(candidates))
            if len(cluster) == size:
                for cx, cy in cluster:
                    layout[cy][cx]['type'] = zone_type
                return True
        else:
            layout[y][x]['type'] = zone_type
            return True
    return False


def place_aisles(layout, rows, cols):
    row_walkways = {y: None for y in range(1, rows - 1)}
    col_walkways = {x: None for x in range(1, cols - 1)}

    # Reserve 1 walkway per row and column
    for y in range(1, rows - 2):
        for x in range(1, cols - 2):
            if layout[y][x]['type'] == 'Walkway':
                if row_walkways[y] is None:
                    row_walkways[y] = (x, y)
                if col_walkways[x] is None:
                    col_walkways[x] = (x, y)

    reserved = set(row_walkways.values()) | set(col_walkways.values())

    # Convert other walkways to aisles (only if adjacent to walkway AND skip a row vertically)
    candidates = []
    blocked = set()  # Tracks cells blocked by vertical adjacency
    for x in range(1, cols - 2):
        for y in range(1, rows - 2):
            if (x, y) in blocked:
                continue
            if layout[y][x]['type'] == 'Walkway' and (x, y) not in reserved:
                if count_adjacent_type(layout, x, y, rows, cols, 'Walkway') >= 1:
                    candidates.append((x, y))
                    blocked.add((x, y + 1))  # block row below

    # Greedy convert candidates and check connectivity
    for x, y in candidates:
        layout[y][x]['type'] = 'Aisle'
        if not is_walkway_connected(layout, rows, cols):
            layout[y][x]['type'] = 'Walkway'  # revert if disconnects


def optimize_layout(layout, rows, cols, cell_size):
    door_locs = find_door_locations(layout, rows, cols)

    ensure_walkways(layout, rows, cols)
    place_aisles(layout, rows, cols)
    place_cashiers(layout, door_locs, rows, cols)

    place_zone(layout, rows, cols, 'Butcher', avoid_types=['FruitsVeg', 'Spices'], size=1)
    place_zone(layout, rows, cols, 'Spices', avoid_types=['FruitsVeg', 'Butcher'], size=1)
    fruitsveg_size = random.randint(2, 8)
    place_zone(layout, rows, cols, 'FruitsVeg', avoid_types=['Spices', 'Butcher'], size=fruitsveg_size, connected=True)

    return {
        'grid': layout,
        'rows': rows,
        'cols': cols,
        'cell_size': cell_size
    }
