#!/bin/bash

echo "🧪 Testing New Frontend API Integration"
echo "========================================"
echo ""

# Test 1: Check if frontend is accessible
echo "1️⃣ Checking if frontend is accessible..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/)
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo "   ✅ Frontend is accessible (HTTP $FRONTEND_STATUS)"
else
    echo "   ❌ Frontend is NOT accessible (HTTP $FRONTEND_STATUS)"
    exit 1
fi
echo ""

# Test 2: Check if health endpoint works
echo "2️⃣ Checking health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost/health)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "   ✅ Health endpoint works: $HEALTH_RESPONSE"
else
    echo "   ❌ Health endpoint failed: $HEALTH_RESPONSE"
    exit 1
fi
echo ""

# Test 3: Test API analyze endpoint with a real image
echo "3️⃣ Testing /api/analyze endpoint with real image..."
IMAGE_PATH="uploads/original/3db34894-8c1b-4fac-bc65-66995bab6580.jpg"

if [ ! -f "$IMAGE_PATH" ]; then
    echo "   ⚠️  Test image not found at $IMAGE_PATH"
    # Try to find any image in uploads
    IMAGE_PATH=$(find uploads/original -name "*.jpg" -type f | head -1)
    if [ -z "$IMAGE_PATH" ]; then
        echo "   ❌ No images found in uploads/original/"
        exit 1
    fi
    echo "   ℹ️  Using alternative image: $IMAGE_PATH"
fi

echo "   📤 Uploading image to /api/analyze..."
ANALYZE_RESPONSE=$(curl -s -X POST http://localhost/api/analyze \
    -F "image=@$IMAGE_PATH" \
    -w "\n%{http_code}")

HTTP_CODE=$(echo "$ANALYZE_RESPONSE" | tail -1)
RESPONSE_BODY=$(echo "$ANALYZE_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ API returned HTTP $HTTP_CODE"
    echo ""
    echo "   📊 Response Summary:"
    
    # Parse JSON response
    PHOTO_ID=$(echo "$RESPONSE_BODY" | grep -o '"id_фото":"[^"]*"' | cut -d'"' -f4)
    TREES_COUNT=$(echo "$RESPONSE_BODY" | grep -o '"n":[0-9]*' | cut -d':' -f2)
    
    echo "      Photo ID: $PHOTO_ID"
    echo "      Trees detected: $TREES_COUNT"
    
    # Check if trees array exists
    if echo "$RESPONSE_BODY" | grep -q '"trees":\['; then
        echo "      ✅ Trees array present in response"
        
        # Show first tree details
        FIRST_TREE=$(echo "$RESPONSE_BODY" | grep -o '"вид":"[^"]*"' | head -1 | cut -d'"' -f4)
        CONFIDENCE=$(echo "$RESPONSE_BODY" | grep -o '"достоверность_предсказания":[0-9.]*' | head -1 | cut -d':' -f2)
        
        if [ ! -z "$FIRST_TREE" ]; then
            echo "      First tree species: $FIRST_TREE"
            echo "      Confidence: $(echo "$CONFIDENCE * 100" | bc | cut -d'.' -f1)%"
        fi
    else
        echo "      ⚠️  No trees array in response"
    fi
    
    echo ""
    echo "   📄 Full Response (first 500 chars):"
    echo "$RESPONSE_BODY" | head -c 500
    echo ""
    echo "   ..."
else
    echo "   ❌ API returned HTTP $HTTP_CODE"
    echo "   Response: $RESPONSE_BODY"
    exit 1
fi

echo ""
echo "========================================"
echo "✅ All tests passed! New frontend integration works correctly!"
echo ""
echo "🌐 Open http://localhost/ in your browser to test the UI"
echo "🔍 Debug page available at http://localhost/debug.html"

