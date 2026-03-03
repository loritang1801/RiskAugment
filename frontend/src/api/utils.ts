import axios, { AxiosError, AxiosRequestConfig } from 'axios'
import type { ApiResponse } from '@/types/api'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

// Create axios instance with timeout
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add request interceptor to include Authorization header
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Add response interceptor
apiClient.interceptors.response.use(
  (response) => response.data,
  (error: AxiosError<ApiResponse<unknown>>) => {
    const traceId = error.response?.headers?.['x-trace-id'] as string | undefined
    const apiMessage = error.response?.data?.message
    const finalMessage = apiMessage || error.message || 'API request failed'
    const enhancedError = new Error(traceId ? `${finalMessage} (traceId: ${traceId})` : finalMessage)
    console.error('API Error:', enhancedError.message)
    throw enhancedError
  }
)

/**
 * Generic API call - uses real backend data only
 */
export async function apiCall<T>(
  method: 'get' | 'post' | 'put' | 'delete',
  url: string,
  data?: any,
  config?: AxiosRequestConfig
): Promise<T> {
  if (method === 'get') {
    return await apiClient.get(url, config)
  } else if (method === 'post') {
    return await apiClient.post(url, data, config)
  } else if (method === 'put') {
    return await apiClient.put(url, data, config)
  } else if (method === 'delete') {
    return await apiClient.delete(url, config)
  }
  throw new Error('Invalid method')
}

export default apiClient
