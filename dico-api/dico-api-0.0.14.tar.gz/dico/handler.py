from .utils import ensure_coro
from .model.event import *


class EventHandler:
    def __init__(self, client):
        self.events = {}
        self.client = client

    def add(self, event, func):
        if event not in self.events:
            self.events[event] = []

        self.events[event].append(func)

    def remove(self, event, func):
        self.events[event].remove(func)

    def get(self, event) -> list:
        return [ensure_coro(x) for x in self.events.get(event, [])]

    def process_response(self, name, resp):
        model_dict = {
            "READY": Ready,
            "APPLICATION_COMMAND_CREATE": ApplicationCommandCreate,
            "APPLICATION_COMMAND_UPDATE": ApplicationCommandUpdate,
            "APPLICATION_COMMAND_DELETE": ApplicationCommandDelete,
            "CHANNEL_CREATE": ChannelCreate,
            "CHANNEL_UPDATE": ChannelUpdate,
            "CHANNEL_DELETE": ChannelDelete,
            "CHANNEL_PINS_UPDATE": ChannelPinsUpdate,
            "THREAD_CREATE": ThreadCreate,
            "THREAD_UPDATE": ThreadUpdate,
            "THREAD_DELETE": ThreadDelete,
            "THREAD_LIST_SYNC": ThreadListSync,
            "THREAD_MEMBER_UPDATE": ThreadMemberUpdate,
            "THREAD_MEMBERS_UPDATE": ThreadMembersUpdate,
            "GUILD_CREATE": GuildCreate,
            "GUILD_UPDATE": GuildUpdate,
            "GUILD_DELETE": GuildDelete,
            "GUILD_BAN_ADD": GuildBanAdd,
            "GUILD_BAN_REMOVE": GuildBanRemove,
            "GUILD_EMOJIS_UPDATE": GuildEmojisUpdate,
            "GUILD_INTEGRATIONS_UPDATE": GuildIntegrationsUpdate,
            "GUILD_MEMBER_ADD": GuildMemberAdd,
            "GUILD_MEMBER_REMOVE": GuildBanRemove,
            "GUILD_MEMBER_UPDATE": GuildMemberUpdate,
            "GUILD_ROLE_CREATE": GuildRoleCreate,
            "GUILD_ROLE_UPDATE": GuildRoleUpdate,
            "GUILD_ROLE_DELETE": GuildRoleDelete,
            "INTERACTION_CREATE": InteractionCreate,
            "INVITE_CREATE": InviteCreate,
            "INVITE_DELETE": InviteDelete,
            "MESSAGE_CREATE": MessageCreate,
            "MESSAGE_UPDATE": MessageUpdate,
            "MESSAGE_DELETE": MessageDelete,
            "MESSAGE_DELETE_BULK": MessageDeleteBulk,
            "MESSAGE_REACTION_ADD": MessageReactionAdd,
            "MESSAGE_REACTION_REMOVE": MessageReactionRemove,
            "MESSAGE_REACTION_REMOVE_ALL": MessageReactionRemoveAll,
            "MESSAGE_REACTION_REMOVE_EMOJI": MessageReactionRemoveEmoji,
            "PRESENCE_UPDATE": PresenceUpdate,
            "STAGE_INSTANCE_CREATE": StageInstanceCreate,
            "STAGE_INSTANCE_DELETE": StageInstanceDelete,
            "STAGE_INSTANCE_UPDATE": StageInstanceUpdate,
            "TYPING_START": TypingStart,
            "USER_UPDATE": UserUpdate,
            "VOICE_STATE_UPDATE": VoiceStateUpdate
        }
        if name in model_dict:
            ret = model_dict[name].create(self.client, resp)
        else:
            ret = resp
        return ret

    def dispatch_from_raw(self, name, resp):
        ret = self.process_response(name, resp)
        if hasattr(ret, "_dont_dispatch") and ret._dont_dispatch:
            return
        self.client.dispatch(name, ret)
