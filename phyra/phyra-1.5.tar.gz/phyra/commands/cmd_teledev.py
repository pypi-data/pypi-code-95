import click
import pyrogram

@click.group()
def cli():
    '''Telegram Utilities for bot developer'''

@cli.command()
def ss():
    '''Session String Scraper'''
    print()
    print('WARNING !')
    print("Make sure you have API ID and API HASH.")
    print("if you haven't API ID and API HASH, you can type 'phyra telegram tutorial'")
    print()

    make_sure = input('Continue? [y/N] ')
    
    if make_sure == 'y':
        APP_ID = int(input("Enter APP ID here: "))
        API_HASH = input("Enter API HASH here: ")
        with pyrogram.Client(":memory:", api_id=APP_ID, api_hash=API_HASH) as app:
            session_str = app.export_session_string()
            if app.get_me().is_bot:
                user_name = input("Enter the username: ")
                msg = app.send_message(user_name, session_str)
            else:
                msg = app.send_message("me", session_str)
            msg.reply_text(
                "== This String Session is generated using Phyra CLI ==\n\nInstall Phyra : `pip install phyra`\nOpen Source : https://github.com/EterNomm/Phyra-CLI ",
                quote=True,
            )
            print()
            print(
                "Done! please check your Telegram Saved Messages/user's PM for the String Session "
            )
            print()

    else:
        print('Aborted!')


@cli.command()
def tutorial():
    '''Basic tutorial for Phyra Teledev'''
    print('======= Tutorial =======')
    print('Get your API ID and API HASH')
    print('Step :')
    print('1. Goto https://my.telegram.org/apps')
    print('2. Login to your Telegram account with the phone number of the developer account to use.')
    print('3. A Create new application window will appear. Fill in your application details. There is no need to enter any URL, and only the first two fields (App title and Short name) can currently be changed later.')
    print('4. Click on Create application at the end. Remember that your API hash is secret and Telegram won’t let you revoke it.')