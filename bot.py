import discord
import asyncio
import json
import os
import argparse
import sys
from discord.ext import commands

# ==========================================
# CONFIGURATION
# ==========================================
# PUT YOUR BOT TOKEN HERE
BOT_TOKEN = "X" 
GUILD_ID = 0

# File to store role backups
BACKUP_FILE = "role_backup.json"
HTML_FILE = "role_backup.html"

# ==========================================
# SETUP
# ==========================================

# Parse command line arguments
parser = argparse.ArgumentParser(description="Discord Role Backup/Restore Bot")
parser.add_argument("mode", choices=["backup", "strip", "restore"], help="Mode of operation: backup, strip, or restore")

# We need to parse args before starting the bot to know what to do, 
# but discord.py also uses args. We'll parse known args.
args, unknown = parser.parse_known_args()

# ==========================================
intents = discord.Intents.default()
intents.members = True  # Required to read member roles
intents.message_content = True # Good practice generally, though not strictly needed for this logic if not using commands

client = discord.Client(intents=intents)

# ==========================================
# LOGIC
# ==========================================

async def save_roles(guild):
    print(f"Starting backup for guild: {guild.name} ({guild.id})")
    await client.change_presence(activity=discord.Game(name=f"Backing up {guild.name}"))
    
    backup_data = {}
    
    # Load existing data if file exists to merge/update
    if os.path.exists(BACKUP_FILE):
        try:
            with open(BACKUP_FILE, "r") as f:
                backup_data = json.load(f)
        except json.JSONDecodeError:
            print("Backup file corrupted, starting fresh.")
            backup_data = {}

    guild_data = {}
    
    for member in guild.members:
        if member.bot:
            continue
        
        # Get roles (exclude @everyone, managed, premium)
        # We store both ID and Name for readability
        roles = [{"id": r.id, "name": r.name} for r in member.roles if not r.is_default() and not r.is_premium_subscriber() and not r.managed]
        
        if roles:
            guild_data[str(member.id)] = {
                "name": member.display_name, # Use nickname if available
                "username": member.name,     # Keep username for reference
                "roles": roles
            }
            
    backup_data[str(guild.id)] = guild_data
    
    with open(BACKUP_FILE, "w") as f:
        json.dump(backup_data, f, indent=4)
        
    # Generate HTML
    generate_html(guild.name, guild_data)
        
    print(f"Backup complete for {guild.name}. Saved {len(guild_data)} members.")

def generate_html(guild_name, guild_data):
    html_content = f"""
    <html>
    <head>
        <title>Role Backup - {guild_name}</title>
        <style>
            body {{ font-family: sans-serif; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .role {{ display: inline-block; background: #e0e0e0; border-radius: 4px; padding: 2px 6px; margin: 2px; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <h1>Role Backup for {guild_name}</h1>
        <table>
            <tr>
                <th>Member ID</th>
                <th>Nickname</th>
                <th>Username</th>
                <th>Roles</th>
            </tr>
    """
    
    for member_id, data in guild_data.items():
        roles_html = "".join([f'<span class="role">{r["name"]} ({r["id"]})</span>' for r in data["roles"]])
        html_content += f"""
            <tr>
                <td>{member_id}</td>
                <td>{data['name']}</td>
                <td>{data.get('username', 'N/A')}</td>
                <td>{roles_html}</td>
            </tr>
        """
        
    html_content += """
        </table>
    </body>
    </html>
    """
    
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"HTML backup generated at {HTML_FILE}")

async def strip_roles(guild):
    print(f"Starting role strip for guild: {guild.name} ({guild.id})")
    await client.change_presence(activity=discord.Game(name=f"Stripping roles in {guild.name}"))
    
    count = 0
    for member in guild.members:
        if member.bot:
            continue
            
        # Get roles that can be removed (exclude @everyone and managed roles)
        roles_to_remove = [r for r in member.roles if not r.is_default() and not r.managed and not r.is_premium_subscriber()]
        
        if not roles_to_remove:
            continue
            
        try:
            await member.remove_roles(*roles_to_remove, reason="Mass strip command")
            count += 1
            if count % 10 == 0:
                print(f"Stripped roles from {count} members...")
        except discord.Forbidden:
            print(f"Failed to remove roles from {member.name} (Permission Denied)")
        except discord.HTTPException as e:
            print(f"Failed to remove roles from {member.name} ({e})")
            
    print(f"Strip complete for {guild.name}. Affected {count} members.")

async def restore_roles(guild):
    print(f"Starting role restore for guild: {guild.name} ({guild.id})")
    await client.change_presence(activity=discord.Game(name=f"Restoring roles in {guild.name}"))
    
    if not os.path.exists(BACKUP_FILE):
        print("No backup file found!")
        return

    with open(BACKUP_FILE, "r") as f:
        backup_data = json.load(f)
        
    guild_data = backup_data.get(str(guild.id))
    if not guild_data:
        print(f"No backup data found for guild {guild.name}")
        return
        
    count = 0
    for member_id_str, data in guild_data.items():
        member = guild.get_member(int(member_id_str))
        if not member:
            print(f"Member {data['name']} ({member_id_str}) not found in guild.")
            continue
            
        roles_to_add = []
        for role_info in data["roles"]:
            # Handle both old format (list of IDs) and new format (list of dicts)
            if isinstance(role_info, dict):
                role_id = role_info["id"]
            else:
                role_id = role_info
                
            role = guild.get_role(role_id)
            if role:
                roles_to_add.append(role)
            else:
                print(f"Role ID {role_id} not found in guild.")
        
        if roles_to_add:
            try:
                await member.add_roles(*roles_to_add, reason="Mass restore command")
                count += 1
                if count % 10 == 0:
                    print(f"Restored roles for {count} members...")
            except discord.Forbidden:
                print(f"Failed to add roles to {data['name']} (Permission Denied)")
            except discord.HTTPException as e:
                print(f"Failed to add roles to {data['name']} ({e})")
                
    print(f"Restore complete for {guild.name}. Restored {count} members.")

@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    
    target_guild = client.get_guild(GUILD_ID)
    if not target_guild:
        print(f"Error: Bot is not in the specified guild (ID: {GUILD_ID})")
        await client.close()
        return

    if args.mode == "backup":
        await save_roles(target_guild)
    elif args.mode == "strip":
        await strip_roles(target_guild)
    elif args.mode == "restore":
        await restore_roles(target_guild)
            
    print("All tasks finished. Shutting down.")
    await client.close()

if __name__ == "__main__":
    if BOT_TOKEN == "YOUR_TOKEN_HERE":
        # check env var as fallback
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            print("Error: Please set BOT_TOKEN in the script or DISCORD_TOKEN environment variable.")
            sys.exit(1)
        client.run(token)
    else:
        client.run(BOT_TOKEN)
