import { apiCall } from '@/api/utils'
import type { ApiResponse } from '@/types/api'

export interface ReviewEfficiency {
  averageReviewTime: number
  totalCases: number
  minTime: number
  maxTime: number
}

export interface OverrideRate {
  overrideRate: number
  totalDecisions: number
  overrideCount: number
}

export interface PromptVersion {
  version: string
  totalCases: number
  approvedCases: number
  rejectedCases: number
  overrideCases: number
  approvalRate: number
  rejectionRate: number
  overrideRate: number
  averageReviewTime: number
}

export interface ChainHealthMetrics {
  window_size: number
  total_requests: number
  success_requests: number
  degraded_requests?: number
  failed_requests: number
  degraded_rate?: number
  failure_rate: number
  degraded?: boolean
  error_categories: Record<string, number>
  latency_ms: {
    avg: number
    p50: number
    p95: number
    max: number
  }
  stage_avg_ms: Record<string, number>
}

interface PromptComparisonData {
  versions: PromptVersion[]
}

const formatDateRange = (startDate: string, endDate: string) => ({
  startDate,
  endDate
})

export const getReviewEfficiencyApi = async (
  startDate: string,
  endDate: string
): Promise<ReviewEfficiency | null> => {
  const response = await apiCall<ApiResponse<ReviewEfficiency>>(
    'get',
    '/analytics/review-efficiency',
    undefined,
    { params: formatDateRange(startDate, endDate) }
  )
  return response.status === 'success' ? response.data || null : null
}

export const getOverrideRateApi = async (
  startDate: string,
  endDate: string
): Promise<OverrideRate | null> => {
  const response = await apiCall<ApiResponse<OverrideRate>>(
    'get',
    '/analytics/override-rate',
    undefined,
    { params: formatDateRange(startDate, endDate) }
  )
  return response.status === 'success' ? response.data || null : null
}

export const getPromptComparisonApi = async (
  startDate: string,
  endDate: string
): Promise<PromptVersion[]> => {
  const response = await apiCall<ApiResponse<PromptComparisonData>>(
    'get',
    '/analytics/prompt-comparison',
    undefined,
    { params: formatDateRange(startDate, endDate) }
  )
  return response.status === 'success' ? response.data?.versions || [] : []
}

export const getChainHealthApi = async (limit = 200): Promise<ChainHealthMetrics | null> => {
  const response = await apiCall<ApiResponse<ChainHealthMetrics>>(
    'get',
    '/analytics/chain-health',
    undefined,
    { params: { limit } }
  )
  return response.status === 'success' ? response.data || null : null
}
