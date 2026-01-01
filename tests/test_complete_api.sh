#!/bin/bash

# Complete API Test Script for Nwassik
# Tests all endpoints with proper HTTP methods and authentication

# Disable AWS pager
export AWS_PAGER=""

# Load configuration from .env file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "Error: .env file not found at $ENV_FILE"
    exit 1
fi

# Source .env file (exports all variables)
set -a  # automatically export all variables
source "$ENV_FILE"
set +a

# Configuration from .env
USER_POOL_ID="$COGNITO_USER_POOL_ID"
CLIENT_ID="$COGNITO_APP_CLIENT_ID"
# API_ENDPOINT, AWS_REGION, and AWS_PROFILE are already loaded from .env

# Test user credentials (unique email per run)
TEST_USERNAME="testuser_$(date +%s)"
TEST_EMAIL="testuser-$(date +%s)@example.com"
TEST_PASSWORD="TestPassword123!"

# Global variables
ID_TOKEN=""
USER_ID=""
REQUEST_ID=""
FAVORITE_ID=""

# Helper functions
print_separator() {
    echo "=========================================="
}

print_header() {
    echo ""
    print_separator
    echo "$1"
    print_separator
    echo ""
}

# Setup: Create and confirm user
setup_test_user() {
    print_header "SETUP: Creating Test User"

    echo "Creating user: $TEST_USERNAME (email: $TEST_EMAIL)"
    aws cognito-idp admin-create-user \
        --user-pool-id "$USER_POOL_ID" \
        --username "$TEST_USERNAME" \
        --user-attributes Name=email,Value="$TEST_EMAIL" Name=email_verified,Value=true Name=phone_number,Value="+33630633814" Name=phone_number_verified,Value=true \
        --message-action SUPPRESS \
        --region "$AWS_REGION" \
        --profile "$AWS_PROFILE" \
        --output json > /dev/null

    echo "Setting password..."
    aws cognito-idp admin-set-user-password \
        --user-pool-id "$USER_POOL_ID" \
        --username "$TEST_USERNAME" \
        --password "$TEST_PASSWORD" \
        --permanent \
        --region "$AWS_REGION" \
        --profile "$AWS_PROFILE" \
        --output json > /dev/null

    echo "✓ User created and confirmed"
}

# Get JWT tokens
get_jwt_tokens() {
    print_header "AUTHENTICATION: Getting JWT Tokens"

    aws cognito-idp admin-initiate-auth \
        --user-pool-id "$USER_POOL_ID" \
        --client-id "$CLIENT_ID" \
        --auth-flow ADMIN_USER_PASSWORD_AUTH \
        --auth-parameters USERNAME="$TEST_EMAIL",PASSWORD="$TEST_PASSWORD" \
        --region "$AWS_REGION" \
        --profile "$AWS_PROFILE" \
        --output json > /tmp/auth_response.json 2>/dev/null

    ID_TOKEN=$(jq -r '.AuthenticationResult.IdToken' /tmp/auth_response.json 2>/dev/null)
    USER_ID=$(echo "$ID_TOKEN" | cut -d. -f2 | base64 -D 2>/dev/null | jq -r '.sub' 2>/dev/null)

    rm -f /tmp/auth_response.json

    echo "User ID: $USER_ID"
    echo "Token: ${ID_TOKEN:0:50}..."
    echo "✓ Authentication successful"
}

# Test 1: Health Check (Public)
test_health_check() {
    print_header "TEST 1: Health Check (GET /health - Public)"

    local response=$(curl -s -w '\n%{http_code}' "$API_ENDPOINT/health")
    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')

    echo "Response: $body"
    echo "HTTP Status: $http_code"
}

# Test 2: List All Requests (Public)
test_list_requests() {
    print_header "TEST 2: List All Requests (GET /v0/requests - Public)"

    local response=$(curl -s -w '\n%{http_code}' "$API_ENDPOINT/v0/requests")
    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')

    echo "Response: $body"
    echo "HTTP Status: $http_code"
}

# Test 3: Create Request (Authenticated)
test_create_request() {
    print_header "TEST 3: Create Request (POST /v0/requests - Authenticated)"

    local payload='{
        "type": "buy_and_deliver",
        "title": "Test iPhone 16 Pro",
        "description": "Need iPhone 16 Pro from Paris",
        "dropoff_latitude": 36.8065,
        "dropoff_longitude": 10.1815
    }'

    local response=$(curl -s -w '\n%{http_code}' -X POST "$API_ENDPOINT/v0/requests" \
        -H "Authorization: Bearer $ID_TOKEN" \
        -H "Content-Type: application/json" \
        -d "$payload")

    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')

    echo "Response: $body"
    echo "HTTP Status: $http_code"

    if [[ $http_code == "201" ]]; then
        REQUEST_ID=$(echo "$body" | jq -r '.request_id')
        echo "Request ID: $REQUEST_ID"
    fi
}

# Test 4: Get Single Request (Public)
test_get_request() {
    print_header "TEST 4: Get Single Request (GET /v0/requests/{id} - Public)"

    if [ -z "$REQUEST_ID" ]; then
        echo "⚠ No request ID available, skipping test"
        return
    fi

    local response=$(curl -s -w '\n%{http_code}' "$API_ENDPOINT/v0/requests/$REQUEST_ID")
    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')

    echo "Response: $body"
    echo "HTTP Status: $http_code"
}

# Test 5: Update Request (Authenticated)
test_update_request() {
    print_header "TEST 5: Update Request (PATCH /v0/requests/{id} - Authenticated)"

    if [ -z "$REQUEST_ID" ]; then
        echo "⚠ No request ID available, skipping test"
        return
    fi

    local payload='{
        "title": "Updated: iPhone 16 Pro Max",
        "description": "Updated - need it urgently"
    }'

    local response=$(curl -s -w '\n%{http_code}' -X PATCH "$API_ENDPOINT/v0/requests/$REQUEST_ID" \
        -H "Authorization: Bearer $ID_TOKEN" \
        -H "Content-Type: application/json" \
        -d "$payload")

    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')

    echo "Response: $body"
    echo "HTTP Status: $http_code"
}

# Test 6: List User Requests (Authenticated)
test_list_user_requests() {
    print_header "TEST 6: List User Requests (GET /v0/users/{id}/requests - Authenticated)"

    if [ -z "$USER_ID" ]; then
        echo "⚠ No user ID available, skipping test"
        return
    fi

    local response=$(curl -s -w '\n%{http_code}' "$API_ENDPOINT/v0/users/$USER_ID/requests" \
        -H "Authorization: Bearer $ID_TOKEN")

    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')

    echo "Response: $body"
    echo "HTTP Status: $http_code"
}

# Test 7: Create Favorite (Authenticated)
test_create_favorite() {
    print_header "TEST 7: Create Favorite (POST /v0/favorites - Authenticated)"

    if [ -z "$REQUEST_ID" ]; then
        echo "⚠ No request ID available, skipping test"
        return
    fi

    local payload="{\"request_id\": \"$REQUEST_ID\"}"

    local response=$(curl -s -w '\n%{http_code}' -X POST "$API_ENDPOINT/v0/favorites" \
        -H "Authorization: Bearer $ID_TOKEN" \
        -H "Content-Type: application/json" \
        -d "$payload")

    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')

    echo "Response: $body"
    echo "HTTP Status: $http_code"

    if [[ $http_code == "200" ]]; then
        FAVORITE_ID=$(echo "$body" | jq -r '.favorite_id')
        echo "Favorite ID: $FAVORITE_ID"
    fi
}

# Test 8: List Favorites (Authenticated)
test_list_favorites() {
    print_header "TEST 8: List Favorites (GET /v0/favorites - Authenticated)"

    local response=$(curl -s -w '\n%{http_code}' "$API_ENDPOINT/v0/favorites" \
        -H "Authorization: Bearer $ID_TOKEN")

    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')

    echo "Response: $body"
    echo "HTTP Status: $http_code"
}

# Test 9: Delete Favorite (Authenticated)
test_delete_favorite() {
    print_header "TEST 9: Delete Favorite (DELETE /v0/favorites/{id} - Authenticated)"

    if [ -z "$FAVORITE_ID" ]; then
        echo "⚠ No favorite ID available, skipping test"
        return
    fi

    local response=$(curl -s -w '\n%{http_code}' -X DELETE "$API_ENDPOINT/v0/favorites/$FAVORITE_ID" \
        -H "Authorization: Bearer $ID_TOKEN")

    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')

    echo "Response: $body"
    echo "HTTP Status: $http_code"
}

# Test 10: Delete Request (Authenticated)
test_delete_request() {
    print_header "TEST 10: Delete Request (DELETE /v0/requests/{id} - Authenticated)"

    if [ -z "$REQUEST_ID" ]; then
        echo "⚠ No request ID available, skipping test"
        return
    fi

    local response=$(curl -s -w '\n%{http_code}' -X DELETE "$API_ENDPOINT/v0/requests/$REQUEST_ID" \
        -H "Authorization: Bearer $ID_TOKEN")

    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')

    echo "Response: $body"
    echo "HTTP Status: $http_code"
}

# Cleanup: Delete test user
cleanup_test_user() {
    print_header "CLEANUP: Deleting Test User"

    echo "Deleting user: $TEST_USERNAME"
    aws cognito-idp admin-delete-user \
        --user-pool-id "$USER_POOL_ID" \
        --username "$TEST_USERNAME" \
        --region "$AWS_REGION" \
        --profile "$AWS_PROFILE" \
        --output json > /dev/null 2>&1 || true

    echo "✓ Test user deleted"
}

# Main execution
main() {
    print_header "Nwassik API Complete Test Suite"

    echo "API Endpoint: $API_ENDPOINT"
    echo "Test User: $TEST_EMAIL"
    echo ""

    # Setup
    setup_test_user
    get_jwt_tokens

    # Run all tests
    test_health_check
    test_list_requests
    test_create_request
    test_get_request
    test_update_request
    test_list_user_requests
    test_create_favorite
    test_list_favorites
    test_delete_favorite
    test_delete_request

    # Cleanup
    # Uncomment the line below to pause before cleanup (useful to check AWS console)
    read -p "Press Enter to cleanup test user..."
    cleanup_test_user

    print_header "All Tests Completed"
    echo "Summary:"
    echo "  User: $TEST_EMAIL"
    echo "  User ID: $USER_ID"
    echo "  Request ID: $REQUEST_ID"
    echo "  Favorite ID: $FAVORITE_ID"
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main
fi