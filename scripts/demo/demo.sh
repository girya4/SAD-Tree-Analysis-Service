#!/bin/bash

# Demo script for Image Processing Service
echo "🚀 Image Processing Service Demo"
echo "=================================================="

BASE_URL="http://localhost"
API_BASE="$BASE_URL/api"

# Check if service is running
echo ""
echo "1. Checking service health..."
HEALTH_RESPONSE=$(curl -s "$BASE_URL/")
if [[ $? -eq 0 ]]; then
    echo "✓ Service is running"
    echo "  Response: $HEALTH_RESPONSE"
else
    echo "✗ Service is not running. Please start it with:"
    echo "  docker-compose up -d"
    exit 1
fi

# Get session
echo ""
echo "2. Getting user session..."
SESSION_RESPONSE=$(curl -s -c cookies.txt "$API_BASE/get-session")
if [[ $? -eq 0 ]]; then
    echo "✓ Session created"
    echo "  Response: $SESSION_RESPONSE"
else
    echo "✗ Failed to get session"
    exit 1
fi

# Check if test image exists
if [[ ! -f "test_image.jpg" ]]; then
    echo ""
    echo "✗ Test image not found. Please create test_image.jpg first"
    exit 1
fi

# Upload image
echo ""
echo "3. Uploading image..."
UPLOAD_RESPONSE=$(curl -s -b cookies.txt -X POST -F "file=@test_image.jpg" "$API_BASE/newTask")
if [[ $? -eq 0 ]]; then
    echo "✓ Image uploaded successfully"
    echo "  Response: $UPLOAD_RESPONSE"
    
    # Extract task ID
    TASK_ID=$(echo "$UPLOAD_RESPONSE" | grep -o '"task_id":[0-9]*' | grep -o '[0-9]*')
    echo "  Task ID: $TASK_ID"
else
    echo "✗ Upload failed"
    exit 1
fi

# Check status
echo ""
echo "4. Checking processing status..."
MAX_ATTEMPTS=10
for i in $(seq 1 $MAX_ATTEMPTS); do
    STATUS_RESPONSE=$(curl -s -b cookies.txt "$API_BASE/isReady/$TASK_ID")
    if [[ $? -eq 0 ]]; then
        STATUS=$(echo "$STATUS_RESPONSE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
        echo "  Attempt $i: Status = $STATUS"
        
        if [[ "$STATUS" == "completed" ]]; then
            echo "✓ Image processing completed!"
            echo "  Full response: $STATUS_RESPONSE"
            break
        elif [[ "$STATUS" == "failed" ]]; then
            echo "✗ Image processing failed!"
            break
        else
            sleep 2
        fi
    else
        echo "✗ Status check failed"
        break
    fi
done

echo ""
echo "🎉 Demo completed!"
echo ""
echo "🌐 Access the web interface at: $BASE_URL/frontend/"
echo "📚 API documentation at: $BASE_URL/docs"
echo "🔍 Celery monitoring at: $BASE_URL/flower/"

# Clean up
rm -f cookies.txt
