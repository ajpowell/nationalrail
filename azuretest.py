import os, uuid
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

from dotenv import load_dotenv

try:
    load_dotenv()

    print("Azure Blob Storage Python quickstart sample")

    # Quickstart code goes here
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    # Create a unique name for the container
    # container_name = str(uuid.uuid4())
    container_name = 'nationalrail'

    # Create the container
    # container_client = blob_service_client.create_container(container_name)

    # Connect to existing container
    container_client = blob_service_client.get_container_client(container_name)

    local_path = './'
    local_file_name = 'README.md'

    remote_path = 'raw/2024/01/14'

    local_file_path = os.path.join(local_path, local_file_name)
    remote_file_path = os.path.join(remote_path, local_file_name)

    # Create a blob client using the local file name as the name for the blob
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=remote_file_path)

    print("\nUploading to Azure Storage as blob:\n\t" + local_file_name)

    # Upload the created file
    with open(file=local_file_path, mode="rb") as data:
        blob_client.upload_blob(data)

    print("\nListing blobs...")

    # List the blobs in the container
    blob_list = container_client.list_blobs()
    for blob in blob_list:
        print("\t" + blob.name)

except Exception as ex:
    print('Exception:')
    print(ex)
