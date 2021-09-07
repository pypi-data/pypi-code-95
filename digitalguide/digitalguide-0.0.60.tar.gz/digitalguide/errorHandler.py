from telegram import Update
from telegram.ext import CallbackContext

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
    
def error_handler(update: Update, context: CallbackContext):
    """Log the error to notify the developer."""
    logger.error(msg="Exception while handling an update:",
                 exc_info=context.error)