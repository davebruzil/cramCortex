// Test script to run in browser console
// This replicates the exact same fetch call that the frontend is making

const testFetch = async () => {
    console.log('Testing fetch to backend...');
    
    // Test 1: Simple health check
    try {
        const healthResponse = await fetch('http://localhost:8000/api/v1/health');
        console.log('Health check status:', healthResponse.status);
        const healthData = await healthResponse.json();
        console.log('Health data:', healthData);
    } catch (error) {
        console.error('Health check failed:', error);
        return;
    }
    
    // Test 2: Create a simple test file for upload
    const testContent = 'Test PDF content';
    const testBlob = new Blob([testContent], { type: 'application/pdf' });
    const testFile = new File([testBlob], 'test.pdf', { type: 'application/pdf' });
    
    console.log('Created test file:', testFile);
    
    // Test 3: Try the exact same fetch call as the frontend
    try {
        const formData = new FormData();
        formData.append('file', testFile);
        
        console.log('Making upload request...');
        const response = await fetch('http://localhost:8000/api/v1/documents/upload', {
            method: 'POST',
            body: formData,
        });
        
        console.log('Upload response status:', response.status);
        console.log('Upload response headers:', [...response.headers.entries()]);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Upload failed with error:', errorText);
        } else {
            const result = await response.json();
            console.log('Upload successful:', result);
        }
    } catch (error) {
        console.error('Upload request failed:', error);
        console.error('Error type:', error.constructor.name);
        console.error('Error message:', error.message);
    }
};

// Run the test
testFetch();