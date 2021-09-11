"""Defines global functions."""
from .labels import score_label

def reset_score():
    """Resets the user score to 0."""
    score_label.text = "Score: 0"

def increment_score():
    """Increments the users score."""
    score = int(score_label.text[7:])
    score_label.text = f"Score: {score + 20}"

def get_orientation(p1, p2, p3):
    """Determines the orientation between three points.
    Used in calculating whether a point lies within a polygon.

    Args:
        p1 (Vector2): A point in 2D space.
        p2 (Vector2): A point in 2D space.
        p3 (Vector2): A point in 2D space.

    Returns:
        int: -1 if the orientation is counter-clockwise, 1 if clockwise, and 0 if the three points are colinear.
    """
    val = (p2.y - p1.y) * (p3.x - p2.x) - (p2.x - p1.x) * (p3.y - p2.y)
    return -1 if val < 0 else 1 if val > 0 else 0