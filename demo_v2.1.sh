#!/bin/bash

echo "🌳 Tree Analysis Service v2.1 Demo"
echo "Enhanced UI with Image Thumbnails & Flexible ML Configuration"
echo "=================================================================="

BASE_URL="http://localhost"
COOKIE_FILE="cookies_v2.1.txt"
TEST_IMAGE="test_image.jpg"

# Create a dummy image for testing if it doesn't exist
if [ ! -f "$TEST_IMAGE" ]; then
    echo "Creating a dummy test image: $TEST_IMAGE"
    convert -size 320x200 xc:green "$TEST_IMAGE"
fi

# 1. Check service health
echo -e "\n1. Checking service health..."
HEALTH_RESPONSE=$(curl -s "$BASE_URL/")
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "✓ Service is running"
    echo "  Response: $HEALTH_RESPONSE"
else
    echo "✗ Service is NOT running"
    echo "  Response: $HEALTH_RESPONSE"
    exit 1
fi

# 2. Get user session
echo -e "\n2. Getting user session..."
SESSION_RESPONSE=$(curl -s -c "$COOKIE_FILE" "$BASE_URL/api/get-session")
if echo "$SESSION_RESPONSE" | grep -q "user_id"; then
    echo "✓ Session created"
    echo "  Response: $SESSION_RESPONSE"
else
    echo "✗ Failed to get session"
    echo "  Response: $SESSION_RESPONSE"
    exit 1
fi

# 3. Upload multiple images for enhanced UI demo
echo -e "\n3. Uploading multiple tree images for enhanced UI demo..."
UPLOAD_RESPONSE=$(curl -s -b "$COOKIE_FILE" -F "files=@$TEST_IMAGE" -F "files=@$TEST_IMAGE" -F "files=@$TEST_IMAGE" "$BASE_URL/api/newTasks")
TASK_IDS=$(echo "$UPLOAD_RESPONSE" | grep -o '"task_ids":\[[^]]*\]' | grep -o '[0-9,]*' | tr ',' ' ')

if [ -n "$TASK_IDS" ]; then
    echo "✓ Successfully uploaded multiple images!"
    echo "  Response: $UPLOAD_RESPONSE"
    echo "  Task IDs: $TASK_IDS"
    echo "  Note: New tasks will appear at the top of the list"
else
    echo "✗ Failed to upload images"
    echo "  Response: $UPLOAD_RESPONSE"
    exit 1
fi

# 4. Check task list with new sorting
echo -e "\n4. Checking task list (newest first)..."
TASKS_RESPONSE=$(curl -s -b "$COOKIE_FILE" "$BASE_URL/api/tasks?per_page=10")
if echo "$TASKS_RESPONSE" | grep -q "tasks"; then
    echo "✓ Task list retrieved"
    echo "  Task order (newest first):"
    echo "$TASKS_RESPONSE" | grep -o '"id":[0-9]*' | head -4 | while read line; do
        TASK_ID=$(echo "$line" | grep -o '[0-9]*')
        echo "    - Task $TASK_ID"
    done
else
    echo "✗ Failed to get task list"
    echo "  Response: $TASKS_RESPONSE"
fi

# 5. Check processing status for first task
FIRST_TASK_ID=$(echo "$TASK_IDS" | awk '{print $1}')
echo -e "\n5. Checking processing status for Task $FIRST_TASK_ID..."
STATUS="pending"
ATTEMPTS=0
MAX_ATTEMPTS=10

while [ "$STATUS" != "completed" ] && [ "$ATTEMPTS" -lt "$MAX_ATTEMPTS" ]; do
    ATTEMPTS=$((ATTEMPTS+1))
    echo "  Attempt $ATTEMPTS: Status = $STATUS"
    TASK_STATUS_RESPONSE=$(curl -s -b "$COOKIE_FILE" "$BASE_URL/api/isReady/$FIRST_TASK_ID")
    STATUS=$(echo "$TASK_STATUS_RESPONSE" | grep -o '"status":"[^"]*"' | cut -d':' -f2 | tr -d '"')
    
    if [ "$STATUS" == "completed" ]; then
        echo "✓ Image processing completed!"
        echo "  Full response: $TASK_STATUS_RESPONSE"
        
        # Extract ML results
        TREE_TYPE=$(echo "$TASK_STATUS_RESPONSE" | grep -o '"tree_type":"[^"]*"' | cut -d':' -f2 | tr -d '"')
        HEALTH_SCORE=$(echo "$TASK_STATUS_RESPONSE" | grep -o '"overall_health_score":[0-9.]*' | cut -d':' -f2)
        
        if [ -n "$TREE_TYPE" ]; then
            echo "  🌳 Tree Type: $TREE_TYPE"
            echo "  💚 Health Score: $HEALTH_SCORE"
        fi
    elif [ "$STATUS" == "failed" ]; then
        echo "✗ Image processing failed"
        echo "  Response: $TASK_STATUS_RESPONSE"
        exit 1
    else
        sleep 3
    fi
done

if [ "$STATUS" != "completed" ]; then
    echo "✗ Image processing did NOT complete within $MAX_ATTEMPTS attempts. Current status: $STATUS"
    exit 1
fi

# 6. Show final task list with image information
echo -e "\n6. Final task list with image thumbnails..."
TASKS_RESPONSE=$(curl -s -b "$COOKIE_FILE" "$BASE_URL/api/tasks?per_page=10")
if echo "$TASKS_RESPONSE" | grep -q "tasks"; then
    echo "✓ Final task list retrieved"
    echo "  Features demonstrated:"
    echo "  - Image thumbnails next to each task"
    echo "  - Newest tasks appear at the top"
    echo "  - Flexible ML configuration with comments"
    echo "  - Database-compatible ML field changes"
fi

echo -e "\n🎉 Enhanced UI Demo completed successfully!"
echo -e "\n🌐 Access the enhanced web interface at: $BASE_URL/frontend/"
echo "📚 API documentation at: $BASE_URL/docs"
echo "🔍 Celery monitoring at: $BASE_URL/flower/"

# Clean up
rm -f "$COOKIE_FILE"
