#!/bin/bash

# Create a timestamped backup filename
timestamp=$(date +"%Y-%m-%d_%H-%M-%S")
backup_file="openwebui_backup_$timestamp.tar.gz"

# Define the volume name
volume_name="open-webui"

# Create a temporary container to access the volume
docker run --rm \
  -v ${volume_name}:/data \
  -v $(pwd):/backup \
  alpine \
  tar -czvf /backup/$backup_file -C /data .

echo "✅ Open WebUI backup created: $backup_file"
