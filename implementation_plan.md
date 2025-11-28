# Discord Role Backup/Restore Bot Plan

## Goal
Create a Discord bot that performs three main functions based on command-line arguments:
1.  **Backup**: Save member details (name, ID, roles) to a file.
2.  **Strip**: Remove all roles from members.
3.  **Restore**: Restore roles from the backup file.

## User Review Required
> [!IMPORTANT]
> **Privileged Intents**: This bot requires `Server Members Intent` and `Message Content Intent` (if commands are used, though this seems to be a script-style bot) to be enabled in the Discord Developer Portal.
> **Permissions**: The bot needs `Manage Roles` permission and its role must be higher than the roles it is trying to manage.
> **Token**: You will need to provide your Discord Bot Token. I will set it up to read from an environment variable `DISCORD_TOKEN` or a `.env` file.

## Proposed Changes

### Project Structure
#### [NEW] [requirements.txt](file:///d:/Documents/GitHub/roleCache/requirements.txt)
- `discord.py`
- `python-dotenv`

#### [NEW] [bot.py](file:///d:/Documents/GitHub/roleCache/bot.py)
- Main script containing the logic.
- Uses `argparse` to select the mode.
- Implements `on_ready` to execute the selected task and then exit (or stay running if needed, but "chosen in cmd" implies a one-off task execution usually, or a specific mode of operation).
- **Logic**:
    - **Backup**: `guild.members` -> filter roles -> save to `role_backup.json`.
    - **Strip**: `guild.members` -> `member.edit(roles=[])` (keeping only @everyone).
    - **Restore**: Load `role_backup.json` -> `guild.get_member` -> `member.edit(roles=[...])`.

### Data Format
`role_backup.json`:
```json
{
  "guild_id": {
    "member_id": {
      "name": "username",
      "roles": [123456789, 987654321]
    }
  }
}
```

## Verification Plan
### Automated Tests
- None planned for this simple script.

### Manual Verification
1.  **Setup**: Install requirements.
2.  **Backup**: Run `python bot.py --mode backup`. Check `role_backup.json`.
3.  **Strip**: Run `python bot.py --mode strip`. Check Discord server to see roles removed.
4.  **Restore**: Run `python bot.py --mode restore`. Check Discord server to see roles returned.
