import intersection.url.url as url
from intersection import user, map

class Highscore:
    """A class representing an IC map highscore.
    """

    def __init__(self, userId, mapId, score, mapVersion, dateMade, objectId, username):
        self.userId = userId
        self.mapId = mapId, 
        self.score = score
        self.mapVersion = mapVersion
        self.dateMade = dateMade
        self.objectId = objectId
        self.username = username

    def get_author(self):
        return

    def get_map(self):
        return

def list_high_scores_on_map(**kwargs):
    """A function used to used to create a list of `Highscore` objects on a certain map.

    `mapId` - ID of map to get high scores for.

    `count` - Number of high scores to get.

    Usage::

    >>> import intersection
    >>> highscores = intersection.highscore.list_high_scores_on_map(mapId=413915, count=5)
    >>> for highscore in highscores: print(comment.comment)
    """

    data = url.list_high_scores_on_map(**kwargs)
    highscores = []
    for highscoredata in data:
        highscores.append(Highscore(
            highscoredata['userId'],
            highscoredata['mapId'],
            highscoredata['score'],
            highscoredata['mapVersion'],
            highscoredata['dateMade'],
            highscoredata['objectId'],
            highscoredata['username'],
        ))

    return highscores