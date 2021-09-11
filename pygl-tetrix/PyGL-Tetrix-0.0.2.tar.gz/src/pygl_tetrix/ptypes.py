"""Defines the PTYPES constant which describes the separate Tetrix pieces."""
PTYPES = {
    'I': {
        'squares': ([5, 14], [5, 13], [5, 12], [5, 11]),
        'rotate_pt': [4.5, 12.5]
    },
    'J': {
        'squares': ([4, 14], [4, 13], [4, 12], [5, 14]),
        'rotate_pt': [4, 13]
    },
    'L': {
        'squares': ([4, 14], [5, 14], [5, 13], [5, 12]),
        'rotate_pt': [5, 13]
    },
    'O': {
        'squares': ([4, 14], [4, 13], [5, 14], [5, 13]),
        'rotate_pt': [4.5, 13.5]
    },
    'S': {
        'squares': ([5, 14], [4, 14], [4, 13], [3, 13]),
        'rotate_pt': [4, 13]
    },
    'T': {
        'squares': ([4, 14], [4, 13], [3, 14], [5, 14]),
        'rotate_pt': [4, 14]
    },
    'Z': {
        'squares': ([3, 14], [4, 14], [4, 13], [5, 13]),
        'rotate_pt': [4, 13]
    }
}