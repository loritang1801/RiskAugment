export interface ApiResponse<T> {
  status: 'success' | 'error'
  data?: T
  message?: string
  code?: string
  details?: Record<string, unknown>
  path?: string
  timestamp?: string
  traceId?: string
}

export interface PaginatedApiResponse<T> extends ApiResponse<T[]> {
  page?: number
  size?: number
  total?: number
  totalPages?: number
}
