from telegram import Update
import yaml

from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, CallbackContext, PicklePersistence,
                          ConversationHandler, CallbackQueryHandler, PollAnswerHandler, PollHandler, TypeHandler)

def read_state_yml(filename, actions={}, prechecks:list=[]):
    with open(filename) as file:
        yaml_dict = yaml.load(file, Loader=yaml.FullLoader)

    states_dict = {}

    for state, handlers in yaml_dict.items():
        handler_list = prechecks[:]
        for handler in handlers:
            if handler["handler"] == "MessageHandler":
                if handler["filter"] == "regex":
                    newHandler = MessageHandler(Filters.regex(handler["regex"]), lambda update, context: actions[handler["action"]](update, context, state))
                elif handler["filter"] == "text":
                    newHandler = MessageHandler(Filters.text, lambda update, context: actions[handler["action"]](update, context, state))
                elif handler["filter"] == "photo":
                    newHandler = MessageHandler(Filters.photo, lambda update, context: actions[handler["action"]](update, context, state))
                elif handler["filter"] == "voice":
                    newHandler = MessageHandler(Filters.voice, lambda update, context: actions[handler["action"]](update, context, state))
                else:
                    raise NotImplementedError("This filter is not implemented: {}".format(handler["filter"]))
            elif handler["handler"] == "CommandHandler":
                newHandler = CommandHandler(handler["command"], lambda update, context: actions[handler["action"]](update, context, state))
            elif handler["handler"] == "PollAnswerHandler":
                newHandler = PollAnswerHandler(actions[handler["action"]])
            elif handler["handler"] == "TypeHandler":
                if handler["type"] == "Update":
                    type_ = Update
                newHandler = TypeHandler(type_, lambda update, context: actions[handler["action"]](update, context, state))
            else:
                raise NotImplementedError("This Handler is not implemented: {}".format(handler["handler"]))
                
            handler_list.append(newHandler)

        states_dict[state]= handler_list

    return states_dict