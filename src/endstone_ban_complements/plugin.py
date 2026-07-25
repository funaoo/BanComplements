from endstone.command import Command, CommandSender
from endstone.plugin import Plugin

from endstone_ban_complements import commands as cmd
from endstone_ban_complements.listeners import EventListener
from endstone_ban_complements.storage import Storage

COMMAND_HANDLERS = {
    "tban": cmd.ban,
    "ttempban": cmd.tempban,
    "tunban": cmd.unban,
    "tkick": cmd.kick,
    "tbanip": cmd.banip,
    "ttempbanip": cmd.tempbanip,
    "tunbanip": cmd.unbanip,
    "tmute": cmd.mute,
    "tunmute": cmd.unmute,
    "tbanlist": cmd.banlist,
    "tmutelist": cmd.mutelist,
    "treport": cmd.report,
}


class BanComplements(Plugin):
    api_version = "0.11"

    commands = {
        "tban": {
            "description": "Permanently ban a player.",
            "usages": ["/tban <player: str> <reason: message>"],
            "permissions": ["ban_complements.command.ban"],
        },
        "ttempban": {
            "description": "Temporarily ban a player.",
            "usages": ["/ttempban <player: str> <duration: str> <reason: message>"],
            "aliases": ["ttban"],
            "permissions": ["ban_complements.command.tempban"],
        },
        "tunban": {
            "description": "Remove a player's ban.",
            "usages": ["/tunban <player: str>"],
            "permissions": ["ban_complements.command.unban"],
        },
        "tkick": {
            "description": "Kick an online player.",
            "usages": ["/tkick <player: str> <reason: message>"],
            "permissions": ["ban_complements.command.kick"],
        },
        "tbanip": {
            "description": "Permanently ban a player's IP address.",
            "usages": ["/tbanip <player: str> <reason: message>"],
            "aliases": ["tipban"],
            "permissions": ["ban_complements.command.banip"],
        },
        "ttempbanip": {
            "description": "Temporarily ban a player's IP address.",
            "usages": ["/ttempbanip <player: str> <duration: str> <reason: message>"],
            "aliases": ["ttbanip"],
            "permissions": ["ban_complements.command.tempbanip"],
        },
        "tunbanip": {
            "description": "Remove a player's IP ban.",
            "usages": ["/tunbanip <player: str>"],
            "permissions": ["ban_complements.command.unbanip"],
        },
        "tmute": {
            "description": "Temporarily mute a player.",
            "usages": ["/tmute <player: str> <duration: str> <reason: message>"],
            "permissions": ["ban_complements.command.mute"],
        },
        "tunmute": {
            "description": "Remove a player's mute.",
            "usages": ["/tunmute <player: str>"],
            "permissions": ["ban_complements.command.unmute"],
        },
        "tbanlist": {
            "description": "List all banned players.",
            "usages": ["/tbanlist"],
            "permissions": ["ban_complements.command.banlist"],
        },
        "tmutelist": {
            "description": "List all muted players.",
            "usages": ["/tmutelist"],
            "permissions": ["ban_complements.command.mutelist"],
        },
        "treport": {
            "description": "Report a player to online staff.",
            "usages": ["/treport <player: str> <reason: message>"],
            "permissions": ["ban_complements.command.report"],
        },
    }

    permissions = {
        "ban_complements.command.ban": {"description": "Allows banning players.", "default": "op"},
        "ban_complements.command.tempban": {"description": "Allows temporarily banning players.", "default": "op"},
        "ban_complements.command.unban": {"description": "Allows unbanning players.", "default": "op"},
        "ban_complements.command.kick": {"description": "Allows kicking players.", "default": "op"},
        "ban_complements.command.banip": {"description": "Allows IP banning players.", "default": "op"},
        "ban_complements.command.tempbanip": {"description": "Allows temporarily IP banning players.", "default": "op"},
        "ban_complements.command.unbanip": {"description": "Allows removing IP bans.", "default": "op"},
        "ban_complements.command.mute": {"description": "Allows muting players.", "default": "op"},
        "ban_complements.command.unmute": {"description": "Allows unmuting players.", "default": "op"},
        "ban_complements.command.banlist": {"description": "Allows viewing the ban list.", "default": "op"},
        "ban_complements.command.mutelist": {"description": "Allows viewing the mute list.", "default": "op"},
        "ban_complements.command.report": {"description": "Allows reporting players.", "default": True},
        "ban_complements.notify.report": {"description": "Receives report notifications.", "default": "op"},
    }

    def on_load(self) -> None:
        self.save_default_config()

    def on_enable(self) -> None:
        config = self.config
        self.webhooks_config = config.get("webhooks", {})
        self.messages_config = config.get("messages", {})
        self.prefix = self.messages_config.get("prefix", "")
        self.storage = Storage(self.data_folder)
        self.register_events(EventListener(self))
        self.server.scheduler.run_task(self, self.storage.purge_expired, delay=1200, period=1200)

    def broadcast(self, message: str) -> None:
        for player in self.server.online_players:
            player.send_message(message)
        self.logger.info(message)

    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        handler = COMMAND_HANDLERS.get(command.name)
        if handler is None:
            return False
        return handler(self, sender, args)
