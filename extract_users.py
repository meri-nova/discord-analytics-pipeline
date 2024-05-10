import os

import dotenv
import discord
import pandas as pd


dotenv.load_dotenv()

DISCORD_TOKEN = os.environ['DISCORD_BOT_TOKEN']
SERVER_ID = os.environ['DISCORD_SERVER_ID']


# Initialize Discord client with intents
intents = discord.Intents.all()
discord_client = discord.Client(intents=intents)

async def fetch_user_data(guild):
    data = []
    members = guild.members
    print(f"Total members fetched: {len(members)}")
    print("Processing user data...")
 
    for member in members:
        user_data = {
            'user_id': member.id,
            'username': member.name,
            'global_name': member.global_name,
            'is_bot': member.bot,
            'join_date': member.joined_at.strftime('%Y-%m-%d %H:%M:%S') if member.joined_at else 'N/A',
            'created_at': member.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'top_role': member.top_role.name,
            'roles': ', '.join([role.name for role in member.roles if role.name != '@everyone']),
            'premium_since': member.premium_since.strftime('%Y-%m-%d %H:%M:%S') if member.premium_since else 'N/A'
        }
        data.append(user_data)
    return pd.DataFrame(data)


@discord_client.event
async def on_ready():
    print(f'Logged in as {discord_client.user}!')
    guild = discord.utils.get(discord_client.guilds, id=int(SERVER_ID))
    user_df = await fetch_user_data(guild)
    user_df.to_csv('discord_users.csv', index=False)
    print("User data collection complete!")
    await discord_client.close()


if __name__ == '__main__':
    discord_client.run(DISCORD_TOKEN)
