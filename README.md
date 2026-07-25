<p align="center">
  <img src="assets/logo.png" alt="Ban Complements logo" width="220">
</p>

# Ban Complements

Moderation plugin for [Endstone](https://endstone.dev/) (Bedrock Dedicated Server): permanent/temporary bans, IP bans,
mutes, kicks and player reports, with Discord webhook logging.

Built and tested against **Endstone 0.11.6**.

## Features

- Permanent and temporary player bans
- Permanent and temporary IP bans (IP is captured on join)
- Temporary mutes that block chat and a configurable set of commands
- Kick with a custom message
- Player-submitted reports, broadcast to staff online
- Discord webhook logging per action (ban, IP ban, mute, report)
- Persistent JSON storage with automatic background purge of expired entries
- Fully configurable messages and prefix via `config.toml`

## Installation

1. Download the `.whl` from [Releases](../../releases) (or build it yourself, see below).
2. Install it into the same Python environment your Endstone server uses:

   ```bash
   pip install endstone_ban_complements-1.0.0-py3-none-any.whl
   ```

3. Start (or restart) the server. The plugin registers itself automatically via the
   `endstone` entry point — no extra setup required.

## Build from source

```bash
git clone <this-repo>
cd endstone-ban-complements
pip install hatchling
python -m build
```

The resulting `.whl` will be in `dist/`.

## Configuration

On first run, `plugins/BanComplements/config.toml` is created in the server's plugin data folder:

```toml
[webhooks]
ban = ""
ban_ip = ""
mute = ""
report = ""

[messages]
prefix = "§8(§6BanComplements§8) §7"
permanent_ban = "..."
temporary_ban = "..."
permanent_ip_ban = "..."
temporary_ip_ban = "..."
temporary_mute = "..."
kick = "..."
```

Paste a Discord webhook URL into any `[webhooks]` entry to enable logging for that category; leave it empty to
disable it. Message templates support the placeholders `{STAFF}`, `{DATE}`, `{REASON}` and `{TIME}`, and use
Minecraft `§` color codes.

If a webhook request fails (bad URL, no outbound internet access, Discord rejecting the payload, etc.), the error
is logged to the server console instead of failing silently.

## Commands

All commands are prefixed with `t` to avoid collisions with commands from other plugins.

| Command | Usage | Permission |
|---|---|---|
| `/tban` | `/tban <player> <reason>` | `ban_complements.command.ban` |
| `/ttempban` (`/ttban`) | `/ttempban <player> <duration> <reason>` | `ban_complements.command.tempban` |
| `/tunban` | `/tunban <player>` | `ban_complements.command.unban` |
| `/tkick` | `/tkick <player> <reason>` | `ban_complements.command.kick` |
| `/tbanip` (`/tipban`) | `/tbanip <player> <reason>` | `ban_complements.command.banip` |
| `/ttempbanip` (`/ttbanip`) | `/ttempbanip <player> <duration> <reason>` | `ban_complements.command.tempbanip` |
| `/tunbanip` | `/tunbanip <player>` | `ban_complements.command.unbanip` |
| `/tmute` | `/tmute <player> <duration> <reason>` | `ban_complements.command.mute` |
| `/tunmute` | `/tunmute <player>` | `ban_complements.command.unmute` |
| `/tbanlist` | `/tbanlist` | `ban_complements.command.banlist` |
| `/tmutelist` | `/tmutelist` | `ban_complements.command.mutelist` |
| `/treport` | `/treport <player> <reason>` | `ban_complements.command.report` (default: everyone) |

Durations use a single suffix — `s`, `m`, `h` or `d` (e.g. `30s`, `10m`, `2h`, `3d`).

IP bans require the target to have joined the server at least once, since the IP is looked up from the locally
cached join records.

Muted players are blocked from chatting and from a small set of commands (`me`, `tell`, `msg`, `w`).

## Permissions

| Permission | Default | Description |
|---|---|---|
| `ban_complements.command.ban` | op | Allows banning players |
| `ban_complements.command.tempban` | op | Allows temporarily banning players |
| `ban_complements.command.unban` | op | Allows unbanning players |
| `ban_complements.command.kick` | op | Allows kicking players |
| `ban_complements.command.banip` | op | Allows IP banning players |
| `ban_complements.command.tempbanip` | op | Allows temporarily IP banning players |
| `ban_complements.command.unbanip` | op | Allows removing IP bans |
| `ban_complements.command.mute` | op | Allows muting players |
| `ban_complements.command.unmute` | op | Allows unmuting players |
| `ban_complements.command.banlist` | op | Allows viewing the ban list |
| `ban_complements.command.mutelist` | op | Allows viewing the mute list |
| `ban_complements.command.report` | everyone | Allows reporting players |
| `ban_complements.notify.report` | op | Receives report notifications |

## License

Add your license of choice here.
