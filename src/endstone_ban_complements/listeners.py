from endstone.event import (
    PlayerChatEvent,
    PlayerCommandEvent,
    PlayerJoinEvent,
    PlayerLoginEvent,
    event_handler,
)

from endstone_ban_complements import messages
from endstone_ban_complements.timeutil import format_remaining

MUTED_COMMANDS = {"me", "tell", "msg", "w"}


class EventListener:
    def __init__(self, plugin) -> None:
        self._plugin = plugin

    @event_handler
    def on_player_login(self, event: PlayerLoginEvent) -> None:
        player = event.player
        storage = self._plugin.storage

        ban_entry = storage.is_banned(player.name)
        if ban_entry is not None:
            time_left = "Never" if ban_entry["expires_at"] is None else format_remaining(ban_entry["expires_at"])
            key = "permanent_ban" if ban_entry["expires_at"] is None else "temporary_ban"
            event.kick_message = messages.render(
                self._plugin.messages_config[key],
                staff=ban_entry["staff"],
                date=ban_entry["date"],
                reason=ban_entry["reason"],
                time_left=time_left,
            )
            event.is_cancelled = True
            return

        ip_ban_entry = storage.is_ip_banned(player.address.hostname)
        if ip_ban_entry is not None:
            time_left = "Never" if ip_ban_entry["expires_at"] is None else format_remaining(ip_ban_entry["expires_at"])
            key = "permanent_ip_ban" if ip_ban_entry["expires_at"] is None else "temporary_ip_ban"
            event.kick_message = messages.render(
                self._plugin.messages_config[key],
                staff=ip_ban_entry["staff"],
                date=ip_ban_entry["date"],
                reason=ip_ban_entry["reason"],
                time_left=time_left,
            )
            event.is_cancelled = True

    @event_handler
    def on_player_join(self, event: PlayerJoinEvent) -> None:
        self._plugin.storage.register_player(event.player.name, event.player.address.hostname)

    @event_handler
    def on_player_chat(self, event: PlayerChatEvent) -> None:
        mute_entry = self._plugin.storage.is_muted(event.player.name)
        if mute_entry is None:
            return

        time_left = format_remaining(mute_entry["expires_at"])
        event.player.send_message(
            messages.render(
                self._plugin.messages_config["temporary_mute"],
                staff=mute_entry["staff"],
                date=mute_entry["date"],
                reason=mute_entry["reason"],
                time_left=time_left,
            )
        )
        event.is_cancelled = True

    @event_handler
    def on_player_command(self, event: PlayerCommandEvent) -> None:
        name = event.command.strip("/ ").split(" ")[0].split(":")[-1]
        if name not in MUTED_COMMANDS:
            return

        if self._plugin.storage.is_muted(event.player.name) is not None:
            event.player.send_message(f"{self._plugin.prefix}§7You are muted")
            event.is_cancelled = True
