import numpy as np
from app.ml_models import get_top_product_pairs


def generate_store_layout(
        shape: str,
        width: int,
        height: int,
        include_butcher=True,
        include_fruits_vegetables=True,
        include_spices=True,
        include_staff_room=True
):
    layout = _initialize_base_layout(shape, width, height)
    metadata = {}

    metadata["door_position"] = _place_door(layout)
    metadata["cashier_positions"] = _place_cashiers(layout)

    if include_staff_room:
        metadata["staff_room_position"] = _place_section(layout, "StaffRoom", min_walkways=1)
    if include_butcher:
        metadata["butcher_position"] = _place_section(layout, "Butcher", min_walkways=3)
    if include_fruits_vegetables:
        metadata["fruits_vegetables_position"] = _place_section(layout, "FruitsVeg", min_walkways=3)
    if include_spices:
        metadata["spices_position"] = _place_section(layout, "Spices", min_walkways=3)

    _ensure_walkways(layout)
    metadata["layout"] = layout
    return metadata


def _initialize_base_layout(shape: str, width: int, height: int):
    if shape == 'rectangle':
        return _generate_rectangle_layout(width, height)
    elif shape == 'L-shape':
        return _generate_l_shape_layout(width, height)
    else:
        return _generate_default_layout(width, height)


def _generate_rectangle_layout(width: int, height: int):
    return [
        ['Aisle' if row % 2 == 0 else 'Walkway'] * width
        for row in range(height)
    ]


def _generate_l_shape_layout(width: int, height: int):
    layout = [['Walkway'] * width for _ in range(height)]
    for i in range(height):
        if i < height // 2 or i == height - 1:
            for j in range(width // 2):
                layout[i][j] = 'Aisle'
    for j in range(width):
        layout[height - 1][j] = 'Aisle'
    return layout


def _generate_default_layout(width: int, height: int):
    return [['Aisle'] * width for _ in range(height)]


def _place_door(layout):
    layout[0][0] = 'Door'
    return (0, 0)


def _place_cashiers(layout, n_cashiers=2):
    h, w = len(layout), len(layout[0])
    positions = []
    for i in range(n_cashiers):
        row = h - 1
        col = min(i, w - 1)
        layout[row][col] = 'Cashier'
        if row > 0: layout[row - 1][col] = 'Walkway'
        positions.append((row, col))
    return positions


def _place_section(layout, label, min_walkways=1):
    h, w = len(layout), len(layout[0])
    for row in range(h - 1, -1, -1):
        for col in range(w - 1, -1, -1):
            if layout[row][col] in ('Aisle', 'Walkway') and _has_min_walkways(layout, row, col, min_walkways):
                layout[row][col] = label
                return (row, col)
    return None


def _has_min_walkways(layout, row, col, min_count):
    h, w = len(layout), len(layout[0])
    count = 0
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        r, c = row + dr, col + dc
        if 0 <= r < h and 0 <= c < w and layout[r][c] == 'Walkway':
            count += 1
    return count >= min_count


def _ensure_walkways(layout):
    h, w = len(layout), len(layout[0])
    for row in range(h):
        if 'Walkway' not in layout[row]:
            layout[row][0] = 'Walkway'
    for col in range(w):
        if all(layout[row][col] != 'Walkway' for row in range(h)):
            layout[0][col] = 'Walkway'


def arrange_products(layout: list, max_pairs=20):
    top_pairs = get_top_product_pairs(max_pairs)
    aisle_positions = [
        (r, c)
        for r, row in enumerate(layout)
        for c, cell in enumerate(row)
        if cell == 'Aisle'
    ]
    arrangement = []
    i = 0
    while i + 1 < len(aisle_positions) and i // 2 < len(top_pairs):
        pair = top_pairs[i // 2]
        pos1 = aisle_positions[i]
        pos2 = aisle_positions[i + 1]
        arrangement.append({
            "product1": pair['product1_name'],
            "product2": pair['product2_name'],
            "score": pair['score'],
            "product1_position": pos1,
            "product2_position": pos2
        })
        i += 2
    return arrangement
