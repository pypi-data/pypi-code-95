import intersection

my_user = intersection.user.get_details_for_user(userId=2452411)
print(my_user.name)

my_maps = my_user.get_user_maps()

for map in my_maps:
    print(map.name)

    comment = map.get_comments(limit=1)
    print("Latest comment: " + comment[0].comment)

    if map.gameModeGroup == 2:
        highscore = map.get_highscores(count=1)
        print("Highscore: " + highscore[0].score)