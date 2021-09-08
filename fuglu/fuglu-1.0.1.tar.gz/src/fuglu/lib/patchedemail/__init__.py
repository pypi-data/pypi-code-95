from .message import PatchedMIMEMultipart
import sys
if sys.version_info > (3, 9, 1):
    from email.message import EmailMessage as PatchedMessage
else:
    from .message_rfc5322 import PatchedMessage
#from .message import PatchedMessage
