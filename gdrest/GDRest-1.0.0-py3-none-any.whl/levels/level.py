import gd
import typesystem

from gdrest.songs.song import Song


class Level(typesystem.Schema):
    name = typesystem.String()
    id = typesystem.Integer()
    description = typesystem.String(allow_blank=True)
    author = typesystem.Object(properties={"name": typesystem.String(), "id": typesystem.Integer()})
    difficulty = typesystem.String()
    downloads = typesystem.Integer()
    length = typesystem.String()
    stars = typesystem.Integer(maximum=10)
    rated = typesystem.Boolean()
    featured = typesystem.Boolean()
    epic = typesystem.Boolean()
    objects = typesystem.Integer()
    overload = typesystem.Boolean()
    song = typesystem.Reference(to=Song)

    @classmethod
    def from_lvl_object(cls, lvl: gd.Level):
        data = {
            "name": lvl.name,
            "id": lvl.id,
            "description": lvl.description,
            "author": {
                "name": lvl.creator.name,
                "id": lvl.creator.id
            },
            "difficulty": lvl.difficulty.name.replace("_", " ").title(),
            "downloads": lvl.downloads,
            "length": lvl.length.name,
            "stars": lvl.stars,
            "rated": lvl.is_rated(),
            "featured": lvl.is_featured(),
            "epic": lvl.is_epic(),
            "objects": lvl.objects,
            "overload": lvl.objects > 40000,
            "song": Song.from_level(lvl)
        }
        return cls.validate(data)
