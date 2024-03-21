import asyncio
import os

import dotenv
import discord
from google.cloud import bigquery
from google.oauth2 import service_account


dotenv.load_dotenv()

DISCORD_TOKEN = os.environ['DISCORD_BOT_TOKEN']
SERVER_ID = os.environ['DISCORD_SERVER_ID']
CHANNEL_ID = os.environ['DISCORD_CHANNEL_ID']
GCP_CREDENTIALS_FILE = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
DATASET_ID = os.environ['BIGQUERY_DATASET_ID']
TABLE_ID = os.environ['BIGQUERY_TABLE_ID']

# Initialize BigQuery client
credentials = service_account.Credentials.from_service_account_file(
    GCP_CREDENTIALS_FILE,
)
bigquery_client = bigquery.Client(credentials=credentials)

# Initialize Discord client with intents
intents = discord.Intents.all()
discord_client = discord.Client(intents=intents)


async def retrieve_data():
    # Retrieve data from Discord server
    channel = await discord_client.fetch_channel(CHANNEL_ID)
    if channel is None:
        print(f"Could not find channel with ID: {CHANNEL_ID}")
        return
    
    transformed_data = []
    async for message in channel.history(limit=10):
        transformed_data.append({
            'event_id': str(message.id),
            'user_id': str(message.author.id),
            'event_type': 'message',  
            'attachment': str(message.attachments[0].url) if message.attachments else None,
            'created_at': message.created_at.isoformat(),
            'channel_name': channel.name,
            'event_content': message.content
        })

    print(transformed_data)

    ## Insert data into BigQuery
    # errors = await bigquery_client.insert_rows_json(f'{DATASET_ID}.{TABLE_ID}', transformed_data)

    # Handle insertion errors
    # if errors:
    #     print('Errors occurred during data insertion:', errors)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(discord_client.start(DISCORD_TOKEN))
    loop.run_until_complete(retrieve_data())

# async def init():
#     discord.utils.setup_logging()
#     client_task = asyncio.create_task(discord_client.start(DISCORD_TOKEN))
#     await retrieve_data()
#     await client_task


# if __name__ == '__main__':
#     asyncio.run(init())
