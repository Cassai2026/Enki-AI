import os
import requests

def download_nircmd(destination_folder="D:/JARVIS AI/"):
    url = "https://www.nirsoft.net/utils/nircmd.zip"
    response = requests.get(url)

    # Ensure the destination folder exists
    os.makedirs(destination_folder, exist_ok=True)

    # Save the zip file
    zip_path = os.path.join(destination_folder, "nircmd.zip")
    with open(zip_path, "wb") as file:
        file.write(response.content)

    # Unzip the downloaded file
    from zipfile import ZipFile
    with ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(destination_folder)

    # Clean up by deleting the zip file
    os.remove(zip_path)

    # Confirm installation
    nircmd_path = os.path.join(destination_folder, "nircmd.exe")
    if os.path.exists(nircmd_path):
        print(f"nircmd.exe installed successfully at {nircmd_path}")
    else:
        print("Failed to install nircmd.exe.")

# Download nircmd to the specified folder
download_nircmd()