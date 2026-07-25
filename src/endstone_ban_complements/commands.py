import time

from endstone.command import CommandSender

from endstone_ban_complements import messages, webhook
from endstone_ban_complements.timeutil import format_remaining, format_seconds, parse_duration


def _prefixed(plugin, text: str) -> str:
    return f"{plugin.prefix}{text}"


def _reply(sender: CommandSender, text: str) -> None:
    sender.send_message(text)


def _kick_message(plugin, key: str, staff: str, reason: str, time_left: str) -> str:
    template = plugin.messages_config[key]
    return messages.render(template, staff=staff, reason=reason, time_left=time_left)


def ban(plugin, sender: CommandSender, args: list[str]) -> bool:
    name, reason = args[0], args[1]

    if plugin.storage.is_banned(name):
        _reply(sender, _prefixed(plugin, f"§e{name} §7is already banned"))
        return True

    plugin.storage.ban(name, sender.name, reason, expires_at=None)
    plugin.broadcast(_prefixed(plugin, f"§a{name} §7was permanently banned for §e{reason}"))
    webhook.send_embed(
        plugin.webhooks_config["ban"],
        "Ban Log",
        [("Player", name), ("Staff", sender.name), ("Reason", reason), ("Duration", "Permanent")],
        logger=plugin.logger,
    )

    victim = plugin.server.get_player(name)
    if victim is not None:
        victim.kick(_kick_message(plugin, "permanent_ban", sender.name, reason, "Never"))

    return True


def tempban(plugin, sender: CommandSender, args: list[str]) -> bool:
    name, duration_text, reason = args[0], args[1], args[2]
    duration = parse_duration(duration_text)

    if duration is None:
        _reply(sender, _prefixed(plugin, "§7Please provide a valid duration, e.g. §e10m§7, §e2h§7, §e3d"))
        return True

    if plugin.storage.is_banned(name):
        _reply(sender, _prefixed(plugin, f"§e{name} §7is already banned"))
        return True

    expires_at = time.time() + duration
    plugin.storage.ban(name, sender.name, reason, expires_at)
    time_left = format_seconds(duration)
    plugin.broadcast(_prefixed(plugin, f"§a{name} §7was temporarily banned for §e{reason} §7({time_left})"))
    webhook.send_embed(
        plugin.webhooks_config["ban"],
        "Ban Log",
        [("Player", name), ("Staff", sender.name), ("Reason", reason), ("Duration", time_left)],
        logger=plugin.logger,
    )

    victim = plugin.server.get_player(name)
    if victim is not None:
        victim.kick(_kick_message(plugin, "temporary_ban", sender.name, reason, time_left))

    return True


def unban(plugin, sender: CommandSender, args: list[str]) -> bool:
    name = args[0]
    if plugin.storage.unban(name):
        _reply(sender, _prefixed(plugin, f"§e{name} §7was unbanned"))
    else:
        _reply(sender, _prefixed(plugin, f"§e{name} §7is not banned"))
    return True


def kick(plugin, sender: CommandSender, args: list[str]) -> bool:
    name, reason = args[0], args[1]
    victim = plugin.server.get_player(name)

    if victim is None:
        _reply(sender, _prefixed(plugin, f"§e{name} §7is not online"))
        return True

    victim.kick(_kick_message(plugin, "kick", sender.name, reason, "Never"))
    plugin.broadcast(_prefixed(plugin, f"§e{name} §7was kicked for §e{reason}"))
    return True


def banip(plugin, sender: CommandSender, args: list[str]) -> bool:
    name, reason = args[0], args[1]
    address = plugin.storage.get_player_address(name)

    if address is None:
        _reply(sender, _prefixed(plugin, f"§e{name} §7has never joined this server"))
        return True

    if plugin.storage.is_ip_banned(address):
        _reply(sender, _prefixed(plugin, f"§e{name}§7's IP is already banned"))
        return True

    plugin.storage.ban_ip(address, name, sender.name, reason, expires_at=None)
    plugin.broadcast(_prefixed(plugin, f"§a{name} §7received a permanent IP ban for §e{reason}"))
    webhook.send_embed(
        plugin.webhooks_config["ban_ip"],
        "IP Ban Log",
        [("Player", name), ("Staff", sender.name), ("Reason", reason), ("Duration", "Permanent")],
        logger=plugin.logger,
    )

    victim = plugin.server.get_player(name)
    if victim is not None:
        victim.kick(_kick_message(plugin, "permanent_ip_ban", sender.name, reason, "Never"))

    return True


def tempbanip(plugin, sender: CommandSender, args: list[str]) -> bool:
    name, duration_text, reason = args[0], args[1], args[2]
    duration = parse_duration(duration_text)

    if duration is None:
        _reply(sender, _prefixed(plugin, "§7Please provide a valid duration, e.g. §e10m§7, §e2h§7, §e3d"))
        return True

    address = plugin.storage.get_player_address(name)
    if address is None:
        _reply(sender, _prefixed(plugin, f"§e{name} §7has never joined this server"))
        return True

    if plugin.storage.is_ip_banned(address):
        _reply(sender, _prefixed(plugin, f"§e{name}§7's IP is already banned"))
        return True

    expires_at = time.time() + duration
    plugin.storage.ban_ip(address, name, sender.name, reason, expires_at)
    time_left = format_seconds(duration)
    plugin.broadcast(_prefixed(plugin, f"§a{name} §7received a temporary IP ban for §e{reason} §7({time_left})"))
    webhook.send_embed(
        plugin.webhooks_config["ban_ip"],
        "IP Ban Log",
        [("Player", name), ("Staff", sender.name), ("Reason", reason), ("Duration", time_left)],
        logger=plugin.logger,
    )

    victim = plugin.server.get_player(name)
    if victim is not None:
        victim.kick(_kick_message(plugin, "temporary_ip_ban", sender.name, reason, time_left))

    return True


def unbanip(plugin, sender: CommandSender, args: list[str]) -> bool:
    name = args[0]
    address = plugin.storage.get_player_address(name)

    if address is None or not plugin.storage.unban_ip(address):
        _reply(sender, _prefixed(plugin, f"§e{name}§7's IP is not banned"))
        return True

    _reply(sender, _prefixed(plugin, f"§e{name}§7's IP was unbanned"))
    return True


def mute(plugin, sender: CommandSender, args: list[str]) -> bool:
    name, duration_text, reason = args[0], args[1], args[2]
    duration = parse_duration(duration_text)

    if duration is None:
        _reply(sender, _prefixed(plugin, "§7Please provide a valid duration, e.g. §e10m§7, §e2h§7, §e3d"))
        return True

    if plugin.storage.is_muted(name):
        _reply(sender, _prefixed(plugin, f"§e{name} §7is already muted"))
        return True

    expires_at = time.time() + duration
    plugin.storage.mute(name, sender.name, reason, expires_at)
    time_left = format_seconds(duration)
    plugin.broadcast(_prefixed(plugin, f"§e{name} §7was muted for §e{reason} §7({time_left})"))
    webhook.send_embed(
        plugin.webhooks_config["mute"],
        "Mute Log",
        [("Player", name), ("Staff", sender.name), ("Reason", reason), ("Duration", time_left)],
        logger=plugin.logger,
    )

    victim = plugin.server.get_player(name)
    if victim is not None:
        victim.send_message(_kick_message(plugin, "temporary_mute", sender.name, reason, time_left))

    return True


def unmute(plugin, sender: CommandSender, args: list[str]) -> bool:
    name = args[0]
    if plugin.storage.unmute(name):
        _reply(sender, _prefixed(plugin, f"§e{name} §7was unmuted"))
    else:
        _reply(sender, _prefixed(plugin, f"§e{name} §7is not muted"))
    return True


def banlist(plugin, sender: CommandSender, args: list[str]) -> bool:
    entries = plugin.storage.all_bans()
    _reply(sender, _prefixed(plugin, f"There are §e{len(entries)} §7banned players"))
    for name, entry in entries.items():
        time_left = "Never" if entry["expires_at"] is None else format_remaining(entry["expires_at"])
        _reply(sender, f"§7{name} §7banned on §e{entry['date']} §7for §e{entry['reason']} §7({time_left})")
    return True


def mutelist(plugin, sender: CommandSender, args: list[str]) -> bool:
    entries = plugin.storage.all_mutes()
    if not entries:
        _reply(sender, _prefixed(plugin, "§7There are no muted players at the moment"))
        return True

    _reply(sender, _prefixed(plugin, f"There are §e{len(entries)} §7muted players"))
    for name, entry in entries.items():
        time_left = format_remaining(entry["expires_at"])
        _reply(sender, f"§7{name} §7muted on §e{entry['date']} §7for §e{entry['reason']} §7({time_left})")
    return True


def report(plugin, sender: CommandSender, args: list[str]) -> bool:
    name, reason = args[0], args[1]
    victim = plugin.server.get_player(name)

    if victim is None:
        _reply(sender, _prefixed(plugin, f"§e{name} §7is not online"))
        return True

    _reply(sender, _prefixed(plugin, f"Your report against §e{name} §7was sent to staff"))
    webhook.send_embed(
        plugin.webhooks_config["report"],
        "Report Log",
        [("Reporter", sender.name), ("Target", name), ("Reason", reason)],
        logger=plugin.logger,
    )

    for online in plugin.server.online_players:
        if online.has_permission("ban_complements.notify.report"):
            online.send_message(
                f"§l§4NEW REPORT\n§r§7Reporter: §e{sender.name}\n§7Target: §e{name}\n§7Reason: §e{reason}"
            )

    return True
