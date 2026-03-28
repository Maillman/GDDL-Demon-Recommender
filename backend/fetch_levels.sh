#!/bin/bash

# NOTE:
# # # This bash script is only used to test the API and it's rate limits.
# # # I don't intend to use this script to actually retrieve levels for the backend.
# Script to fetch all levels from GDDL API by paginating through results
# Usage: ./fetch_levels.sh <num_pages>
# Example: ./fetch_levels.sh 5

if [ $# -eq 0 ]; then
    echo "Usage: $0 <num_pages>"
    echo "Example: $0 5"
    exit 1
fi

NUM_PAGES=$1
BASE_URL="https://gdladder.com/api/level/search"

echo "Fetching $NUM_PAGES pages from GDDL API..."
echo "Note: API rate limit is 100 requests per minute"
echo ""

for ((page=0; page<NUM_PAGES; page++))
do
    echo "===== Page $page ====="
    curl -X 'GET' \
      "${BASE_URL}?limit=25&page=${page}&sort=ID&sortDirection=asc" \
      -H 'accept: application/json'
    echo ""
    echo ""
done

echo "Finished fetching all $NUM_PAGES pages"
