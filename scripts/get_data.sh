#!/bin/bash

URL="https://mtgjson.com/api/v5/AllPrintings.sqlite"
FILENAME="/app/data/data.json"

if ! type curl >/dev/null 2>&1; then
  echo "Error: curl is not installed. Please install curl before running this script."
  exit 1
fi

curl -s "$URL" -o "$FILENAME"

if [ $? -eq 0 ]; then
  echo "Data downloaded successfully and saved to: $FILENAME"
else
  echo "Error: Failed to download data from $URL"
fi

