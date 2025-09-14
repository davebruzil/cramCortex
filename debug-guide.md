# Frontend "Failed to fetch" Debugging Guide

## Current Status
- ✅ Backend running on http://localhost:8000
- ✅ Frontend running on http://localhost:5175  
- ✅ CORS configured for port 5175
- ✅ Backend endpoints responding correctly via curl
- ❌ Frontend still getting "TypeError: Failed to fetch"

## Root Cause Analysis

**Most Likely Cause**: Port mismatch - Frontend moved to port 5175 but CORS was initially only configured for 5174. **FIXED** - CORS now includes 5175.

**Other Possible Causes**:
1. **Browser Security Policy**: Some browsers block localhost cross-origin requests
2. **Network/Firewall**: Windows firewall or antivirus blocking requests
3. **Content Type Issues**: The multipart/form-data might not be handled correctly
4. **Browser Cache**: Old CORS preflight responses cached
5. **Request Headers**: Missing or incorrect headers in fetch request

## Debugging Steps

### Step 1: Test in Browser Console
1. Open frontend at http://localhost:5175
2. Open Browser Developer Tools (F12)
3. Go to Console tab
4. Copy and paste the content from `test-fetch.js`
5. Check the exact error message and network response

### Step 2: Check Network Tab
1. Open Network tab in Developer Tools
2. Try uploading a file through the UI
3. Look for:
   - OPTIONS request (preflight) - should return 200
   - POST request to /documents/upload - check status code
   - Any CORS errors in console
   - Request/Response headers

### Step 3: Browser-specific Tests
Try in different browsers:
- Chrome/Edge (Chromium-based)
- Firefox
- Check if error is browser-specific

### Step 4: Clear Browser Cache
1. Clear all browser cache and cookies for localhost
2. Hard refresh (Ctrl+Shift+R)
3. Disable browser extensions temporarily

### Step 5: Test with Simple Request First
Before testing file upload, test a simple GET request:
```javascript
fetch('http://localhost:8000/api/v1/health')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
```

### Step 6: Alternative API Base URL
Try using 127.0.0.1 instead of localhost:
1. Temporarily change API_BASE_URL in `frontend/src/services/api.ts`
2. From: `'http://localhost:8000/api/v1'`
3. To: `'http://127.0.0.1:8000/api/v1'`

### Step 7: Backend Request Logging
Check backend console for incoming requests:
- If no requests appear in backend logs, issue is client-side
- If requests appear but fail, issue is server-side

### Step 8: Windows Firewall Check
1. Check if Windows Firewall is blocking Python/Node connections
2. Temporarily disable Windows Defender Firewall for testing
3. Add exceptions for Python and Node.js if needed

## Expected Results After Fix
- ✅ OPTIONS preflight request: 200 OK with correct CORS headers
- ✅ POST upload request: 200 OK (for valid PDF) or 400 (for invalid files)  
- ✅ No CORS errors in browser console
- ✅ File upload works end-to-end

## Next Steps
1. Run through debugging steps systematically
2. Identify exact failure point
3. Apply appropriate fix based on findings

---
*This guide should help identify and resolve the persistent "Failed to fetch" error.*