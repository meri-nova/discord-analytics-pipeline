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

async def process_channel(channel, data):
    print(f"Processing channel {channel.name}...")
    messages = [message async for message in channel.history(limit=None)]
    print(f"Total messages fetched: {len(messages)}")
    print("Processing message data...")

    for message in messages:
        message_data = {
                'message_id': message.id,
                'user_id': message.author.id,
                'username': message.author.name,
                'channel_id': channel.id,
                'channel_name': channel.name,
                'chanel_type': channel.type,
                'content': message.content,
                'clean_content': message.clean_content,
                'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'edited_at': message.edited_at.strftime('%Y-%m-%d %H:%M:%S') if message.edited_at else None,
                'attachments': [attachment.url for attachment in message.attachments],
                'embeds': len(message.embeds),
                'reactions': [{reaction.emoji: reaction.count} for reaction in message.reactions],
                'stickers': [{sticker.name: sticker.url} for sticker in message.stickers],
                'is_pinned': message.pinned,
                'mention_everyone': message.mention_everyone,
                'jump_url': message.jump_url
            }
        data.append(message_data)


async def fetch_messages_data(guild):
    data = []
    for channel in guild.channels:
        if isinstance(channel, discord.TextChannel) or isinstance(channel, discord.VoiceChannel) or isinstance(channel, discord.StageChannel):
            await process_channel(channel, data)
        elif isinstance(channel, discord.ForumChannel):
            for thread in channel.threads:
                await process_channel(thread, data)
    
    print(f"Total messages processed: {len(data)} and Total channels processed: {len(guild.channels)}")
    return pd.DataFrame(data)


@discord_client.event
async def on_ready():
    print(f'Logged in as {discord_client.user}!')
    guild = discord.utils.get(discord_client.guilds, id=int(SERVER_ID))
    messages_df = await fetch_messages_data(guild)
    messages_df.to_csv('discord_messages.csv', index=False)
    print("Messages data collection complete!")
    await discord_client.close()


if __name__ == '__main__':
    discord_client.run(DISCORD_TOKEN)
