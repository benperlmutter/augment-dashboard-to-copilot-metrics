# Finding the Dashboard API Endpoint

The dashboard is a Remix.js React app that loads data dynamically. Here's how to find the API endpoint:

## Step-by-Step Instructions

### 1. Open the Dashboard with DevTools

1. Open Chrome/Firefox
2. Press **F12** (or Cmd+Option+I on Mac) to open DevTools
3. Go to the **Network** tab
4. Check the box **"Preserve log"** (important!)
5. Navigate to your dashboard URL

### 2. Filter for API Requests

In the Network tab:
- Click the **"Fetch/XHR"** filter button (this shows only API calls)
- Look for requests that happen AFTER the page loads
- Common patterns to look for:
  - URLs containing: `api`, `trpc`, `graphql`, `query`, `metrics`, `usage`, `dashboard`
  - Requests to the same domain as your application

### 3. Identify the Metrics API Call

Look for a request that:
- Returns JSON data
- Contains metrics/usage information
- Might have query parameters like:
  - `filter=30` or `days=30` or `period=30`
  - Date ranges
  - User IDs

### 4. Inspect the Request

Click on the API request and check:

**Request URL**: Copy the full URL
Example: `https://app.augmentcode.com/api/trpc/dashboard.getMetrics?input=...`

**Request Method**: Usually GET or POST

**Query Parameters** (if GET):
- Look at the "Payload" or "Query String Parameters" section
- Note the parameter names and format

**Request Payload** (if POST):
- Look at the "Payload" or "Request" tab
- Copy the JSON structure

**Response**:
- Click the "Preview" or "Response" tab
- This shows the data structure we need to parse

### 5. Common Patterns

#### Pattern A: tRPC (most likely for Remix apps)
```
URL: https://app.augmentcode.com/api/trpc/dashboard.getMetrics
Method: GET
Query: ?input={"json":{"filter":"30d"}}
```

#### Pattern B: REST API
```
URL: https://app.augmentcode.com/api/v1/metrics
Method: GET
Query: ?period=30&type=usage
```

#### Pattern C: GraphQL
```
URL: https://app.augmentcode.com/graphql
Method: POST
Body: {"query": "query { metrics { ... } }"}
```

### 6. Test the Endpoint

Once you find it, copy:
1. The full URL
2. The method (GET/POST)
3. Any query parameters or request body
4. The response structure

Then tell me what you found, and I'll update the scraper!

## Quick Test

You can also test the endpoint directly using curl:

```bash
# Replace with your actual URL and cookie
curl 'https://app.augmentcode.com/api/ENDPOINT_HERE' \
  -H 'Cookie: your_cookie_here' \
  | jq .
```

## What to Share

Please share:
1. **Request URL**: The full URL of the API call
2. **Method**: GET or POST
3. **Parameters**: Any query params or request body
4. **Response sample**: First few lines of the JSON response (sanitize if needed)

