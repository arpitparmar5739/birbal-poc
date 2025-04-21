#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "Starting knowledge base initialization..."

# Clear existing data
curl -s -X POST "http://localhost:8000/knowledge/clear"
sleep 2

DATA_DIR="$(dirname "$0")/data"

for file in "$DATA_DIR"/*.json; do
    filename=$(basename "$file")
    echo -e "\n${GREEN}Processing $filename...${NC}"
    
    # Get objects from file (handles both array and single object)
    objects=$(jq -c '.[]?' "$file")
    
    # Process each object with controlled parallelism
    active_jobs=0
    echo "$objects" | while read -r object; do
        # Limit concurrent jobs
        if [ $active_jobs -ge 5 ]; then
            wait $(jobs -p | head -1)
            active_jobs=$((active_jobs - 1))
        fi
        
        (
            response=$(curl -s -X POST "http://localhost:8000/knowledge/add" \
                -H "Content-Type: application/json" \
                -d "$object")
            echo "Added: [ID: $(echo "$object" | jq -r '.metadata.ticket_id // "-"')] [Category: $(echo "$object" | jq -r '.metadata.category')] [Preview: $(echo "$object" | jq -r '.text' | cut -c1-30)...]"
        ) &
        
        active_jobs=$((active_jobs + 1))
    done
    
    # Wait for all jobs in this file to complete
    wait
done

echo -e "\n${GREEN}Knowledge base initialization complete!${NC}"
