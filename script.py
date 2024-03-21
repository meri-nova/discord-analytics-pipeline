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
    channel = discord_client.get_channel('CHANNEL_ID')
    messages = await channel.history(limit=1).flatten()

    # Transform data as needed
    transformed_data = [{
        'event_id': str(message.id),
        'user_id': str(message.author.id),
        'event_type': 'message',  
        'attachment': str(message.attachments[0].url) if message.attachments else None,
        'created_at': message.created_at.isoformat(),
        'channel_name': channel.name,
        'event_content': message.content
    } for message in messages]

    # Insert data into BigQuery
    #print(transformed_data)
    errors = bigquery_client.insert_rows_json(DATASET_ID, TABLE_ID, transformed_data)

    # Handle insertion errors
    if errors:
        print('Errors occurred during data insertion:', errors)

# Run the retrieval and insertion process
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(discord_client.start(DISCORD_TOKEN))
    loop.run_until_complete(retrieve_data())
