#!/bin/bash
echo "🧪 Testing Vector Database..."

# Test 1: Health Check
echo "1. Health Check:"
HEALTH_RESPONSE=$(curl -s http://localhost:6333/health)
if [ $? -eq 0 ]; then
    echo "✅ Health check passed"
    echo "$HEALTH_RESPONSE"
else
    echo "❌ Health check failed"
    exit 1
fi

# Test 2: Collections API
echo ""
echo "2. Collections API:"
COLLECTIONS_RESPONSE=$(curl -s http://localhost:6333/collections)
if [ $? -eq 0 ]; then
    echo "✅ Collections API accessible"
    echo "$COLLECTIONS_RESPONSE"
else
    echo "❌ Collections API failed"
    exit 1
fi

# Test 3: Create Test Collection
echo ""
echo "3. Create Test Collection:"
curl -X PUT http://localhost:6333/collections/test_collection \
  -H "Content-Type: application/json" \
  -d '{
    "vectors": {
      "size": 384,
      "distance": "Cosine"
    }
  }'

if [ $? -eq 0 ]; then
    echo "✅ Test collection created successfully"
else
    echo "❌ Test collection creation failed"
    exit 1
fi

# Test 4: Delete Test Collection
echo ""
echo "4. Cleanup Test Collection:"
curl -X DELETE http://localhost:6333/collections/test_collection

if [ $? -eq 0 ]; then
    echo "✅ Test collection deleted successfully"
else
    echo "❌ Test collection deletion failed"
fi

echo ""
echo "🎉 All Vector Database tests passed!"
