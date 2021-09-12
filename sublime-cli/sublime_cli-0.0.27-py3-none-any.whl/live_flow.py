import sublime

MESSAGE_SOURCE_ID = "eb287a84-48e9-48b7-9c6f-844a5d3889cf"
API_KEY = "h6qbgqgtw0iw7cv6337phht8hwwpno45cczwycokgrd6tyo4jmjfl201vxrjp2hy"
sublime_client = sublime.Sublime(api_key=API_KEY)
sublime_client._BASE_URL = "http://localhost:8000"

# load raw messages (EMLs, MSGs)
raw_message_eml = sublime.util.load_eml("/Users/josh/code/sublime/test-files/emls/punycode.eml")

response = sublime_client.process_raw_message_live_flow(
        raw_message=raw_message_eml,
        mailbox_email_address="foobar@sublimesecurity.com",
        message_source_id=MESSAGE_SOURCE_ID)

print(response)
