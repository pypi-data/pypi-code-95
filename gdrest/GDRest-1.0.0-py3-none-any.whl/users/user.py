import gd
import typesystem


class User(typesystem.Schema):
    name = typesystem.String()
    playerID = typesystem.Integer()
    accountID = typesystem.Integer()
    rank = typesystem.Integer(allow_null=True)
    stars = typesystem.Integer()
    diamonds = typesystem.Integer()
    coins = typesystem.Integer()
    userCoins = typesystem.Integer()
    demons = typesystem.Integer()
    cp = typesystem.Integer()
    mod = typesystem.Object(properties=dict(isMod=typesystem.Boolean(), elder=typesystem.Boolean()))
    social = typesystem.Object(
        properties={'youtube': typesystem.String(), 'twitter': typesystem.String(), 'twitch': typesystem.String()})

    @classmethod
    def from_user_object(cls, user: gd.User):
        """
        Validates a user schema from a gd.Level object

        :param user:gd.User
        :return:User
        """
        data = {
            "name": user.name,
            "playerID": user.id,
            "accountID": user.account_id,
            "rank": user.rank,
            "stars": user.stars,
            "diamonds": user.diamonds,
            "coins": user.coins,
            "userCoins": user.user_coins,
            "demons": user.demons,
            "cp": user.cp,
            "mod": {
                "isMod": user.is_mod(),
                "elder": user.is_mod(gd.Role.ELDER_MODERATOR)
            },
            "social": {
                "youtube": user.youtube_link,
                "twitter": user.twitter_link,
                "twitch": user.twitch_link
            }
        }
        return cls.validate(data)
