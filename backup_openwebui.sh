#!/bin/bash

# Create a timestamped backup filename
timestamp=$(date +"%Y-%m-%d_%H-%M-%S")
backup_file="openwebui_backup_$timestamp.tar.gz"

# Define the backup target folder
backup_folder="$HOME/openwebui_backups_archive"

# Define the volume name
volume_name="open-webui"

# Make sure backup folder exists
mkdir -p "$backup_folder"

# Create a temporary container to access the volume and backup
docker run --rm \
  -v ${volume_name}:/data \
  -v ${backup_folder}:/backup \
  alpine \
  tar -czvf /backup/$backup_file -C /data .

echo "✅ Open WebUI backup created: $backup_folder/$backup_file"
