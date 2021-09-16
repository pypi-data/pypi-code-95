ATOM = [
    ((0, 0), None, 'model_id'),  # special empty column to add model id
    ((6, 11), int, 'id'),
    ((12, 16), str, 'name'),
    ((16, 17), str, 'loc_indicator'),
    ((17, 20), str, 'resname'),
    ((21, 22), str, 'chain'),
    ((22, 26), int, 'resid'),
    ((26, 27), str, 'res_icode'),
    ((30, 38), float, 'x'),
    ((38, 46), float, 'y'),
    ((46, 54), float, 'z'),
    ((54, 60), float, 'occupancy'),
    ((60, 66), float, 'b_factor'),
    ((72, 76), str, 'segment'),
    ((76, 78), str, 'element'),
    ((78, 80), str, 'charge'),
]

CONECT = [
    ((6, 11), int, 'parent'),
    ((11, 61), list, 'bonds'),
]

MODEL = [
    ((11, 14), int, 'model_id'),
]

HELIX = [
    ((7, 10), int, 'seq'),
    ((11, 14), str, 'helix_id'),
    ((15, 18), str, 'init_resname'),
    ((19, 20), str, 'init_chain'),
    ((21, 25), int, 'init_resid'),
    ((25, 26), str, 'init_icode'),
    ((27, 30), str, 'end_resname'),
    ((31, 32), str, 'end_chain'),
    ((33, 37), int, 'end_resid'),
    ((37, 38), str, 'end_icode'),
    ((38, 40), int, 'class'),
    ((40, 70), str, 'comment'),
    ((71, 76), int, 'length'),
]

SHEET = [
    ((7, 10), int, 'seq'),
    ((11, 14), str, 'sheet_id'),
    ((14, 16), int, 'num_strands'),
    ((17, 20), str, 'init_resname'),
    ((21, 22), str, 'init_chain'),
    ((22, 26), int, 'init_resid'),
    ((26, 27), str, 'init_icode'),
    ((28, 31), str, 'end_resname'),
    ((32, 33), str, 'end_chain'),
    ((33, 37), int, 'end_resid'),
    ((37, 38), str, 'end_icode'),
    ((38, 40), int, 'sense'),
    ((41, 45), str, 'curr_atom'),
    ((45, 48), str, 'curr_resname'),
    ((49, 50), str, 'curr_chain'),
    ((50, 54), int, 'curr_resid'),
    ((54, 55), str, 'curr_icode'),
    ((56, 60), str, 'prev_atom'),
    ((60, 63), str, 'prev_resname'),
    ((64, 65), str, 'prev_chain'),
    ((65, 69), int, 'prev_resid'),
    ((69, 70), str, 'prev_icode'),
]

TURN = [
    ((7, 10), int, 'seq'),
    ((11, 14), str, 'turn_id'),
    ((15, 18), str, 'init_resname'),
    ((19, 20), str, 'init_chain'),
    ((20, 24), int, 'init_resid'),
    ((24, 25), str, 'init_icode'),
    ((26, 29), str, 'end_resname'),
    ((30, 31), str, 'end_chain'),
    ((31, 35), int, 'end_resid'),
    ((35, 36), str, 'end_icode'),
    ((40, 70), str, 'comment'),
]

SPECIFICATION = {
    'ATOM': ATOM,
    'HETATM': ATOM,
    'CONECT': CONECT,
    'MODEL': MODEL,
    'HELIX': HELIX,
    'SHEET': SHEET,
    'TURN': TURN,
    'ENDMDL': [],
}
