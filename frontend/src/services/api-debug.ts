// Debug version of API service with enhanced error handling and logging
const API_BASE_URL = 'http://localhost:8003/api/v1'

export class DebugApiService {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
    console.log('🔧 Debug API Service initialized with base URL:', this.baseUrl)
  }

  async uploadDocument(file: File): Promise<any> {
    console.log('📤 Starting file upload...')
    console.log('📄 File details:', {
      name: file.name,
      size: file.size,
      type: file.type,
      lastModified: file.lastModified
    })

    const formData = new FormData()
    formData.append('file', file)
    
    console.log('📋 FormData created')
    
    const url = `${this.baseUrl}/documents/upload`
    console.log('🎯 Upload URL:', url)

    try {
      console.log('🚀 Making fetch request...')
      
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
      })

      console.log('📡 Response received:')
      console.log('  Status:', response.status)
      console.log('  Status Text:', response.statusText)
      console.log('  Headers:', Object.fromEntries(response.headers.entries()))

      if (!response.ok) {
        const errorText = await response.text()
        console.error('❌ Upload failed with error response:', errorText)
        throw new Error(`Upload failed: ${response.statusText} - ${errorText}`)
      }

      const result = await response.json()
      console.log('✅ Upload successful:', result)
      return result

    } catch (error) {
      console.error('💥 Fetch error occurred:')
      console.error('  Error type:', error.constructor.name)
      console.error('  Error message:', error.message)
      console.error('  Full error:', error)
      
      // Additional debugging for different error types
      if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
        console.error('🔍 This is a "Failed to fetch" error. Possible causes:')
        console.error('  1. CORS policy blocking the request')
        console.error('  2. Backend server not running or not accessible')
        console.error('  3. Network connectivity issues')
        console.error('  4. Browser security policy')
        console.error('  5. Firewall blocking the connection')
      }
      
      throw error
    }
  }

  async testConnection(): Promise<boolean> {
    console.log('🔄 Testing connection to backend...')
    
    try {
      const response = await fetch(`${this.baseUrl}/health`)
      console.log('🏥 Health check response:', response.status)
      
      if (response.ok) {
        const data = await response.json()
        console.log('✅ Backend is healthy:', data)
        return true
      } else {
        console.warn('⚠️ Health check failed:', response.statusText)
        return false
      }
    } catch (error) {
      console.error('❌ Health check failed:', error)
      return false
    }
  }
}

export const debugApiService = new DebugApiService()