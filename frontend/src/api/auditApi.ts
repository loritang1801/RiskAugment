import { apiCall } from '@/api/utils'
import type { ApiResponse } from '@/types/api'

export interface AuditLog {
  id: number
  caseId: number
  operation: string
  operatorId?: number
  operatorName?: string
  oldValue?: Record<string, unknown>
  newValue?: Record<string, unknown>
  createdAt: string
}

export interface AuditCaseInfo {
  id: number
  bizTransactionId: string
  amount: number
  currency: string
  riskLevel: string
  riskStatus: string
  createdAt: string
}

interface ExecutionChainData {
  case: AuditCaseInfo
  auditLogs: AuditLog[]
}

export const getExecutionChainApi = async (
  caseId: number
): Promise<ExecutionChainData | null> => {
  const response = await apiCall<ApiResponse<ExecutionChainData>>(
    'get',
    `/cases/${caseId}/execution-chain`
  )
  return response.status === 'success' ? response.data || null : null
}
