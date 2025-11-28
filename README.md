# Discord Role Manager Bot

A powerful and simple Discord bot designed to backup, strip, and restore user roles within a specific guild.

## Features

-   **Backup**: Saves all member roles to a JSON file (`role_backup.json`).
-   **HTML Report**: Generates a readable HTML file (`role_backup.html`) listing all members, their nicknames, and roles.
-   **Strip**: Removes all manually assigned roles from all members (preserves @everyone and managed roles).
-   **Restore**: Restores roles to members based on the backup file.
-   **Smart Handling**: Uses user nicknames and handles role hierarchy checks.

## Setup

1.  **Prerequisites**:
    -   Python 3.12+
    -   `uv` package manager (recommended)

2.  **Installation**:
    ```bash
    pip install uv
    uv pip install discord.py python-dotenv
    ```

3.  **Configuration**:
    -   Open `bot.py`.
    -   Ensure `BOT_TOKEN` is set to your Discord Bot Token.
    -   Ensure `GUILD_ID` is set to the ID of the server you want to manage.

## Usage

Run the bot using `uv run bot.py [mode]`.

### 1. Backup Roles
Saves member roles and generates the HTML report.
```bash
uv run bot.py backup
```
*Output files: `role_backup.json`, `role_backup.html`*

### 2. Strip Roles
**WARNING**: This will remove all roles from all members in the configured guild.
```bash
uv run bot.py strip
```

### 3. Restore Roles
Restores roles from `role_backup.json` to members.
```bash
uv run bot.py restore
```

## Important Notes

-   **Intents**: The bot requires **Server Members Intent** and **Message Content Intent** enabled in the Discord Developer Portal.
-   **Permissions**: The bot must have the **Manage Roles** permission in the server.
-   **Hierarchy**: The bot's role must be **higher** in the role list than the roles it is trying to add or remove.
