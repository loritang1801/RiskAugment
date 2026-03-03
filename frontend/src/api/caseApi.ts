import apiClient from './utils'
import type { ApiResponse, PaginatedApiResponse } from '@/types/api'
import type { RiskCase, RiskCasePayload } from '@/types/case'

class CaseAPI {
  // CRUD operations
  async list(
    page: number = 0,
    size: number = 20,
    filters?: Record<string, unknown>
  ): Promise<PaginatedApiResponse<RiskCase>> {
    try {
      const params: Record<string, unknown> = { page, size }
      
      // Add filter parameters if provided
      if (filters) {
        if (filters.bizTransactionId) params.bizTransactionId = filters.bizTransactionId
        if (filters.status) params.status = filters.status
        if (filters.riskLevel) params.riskLevel = filters.riskLevel
        if (filters.country) params.country = filters.country
      }
      
      const response = await apiClient.get('/cases', { params })
      return response as unknown as PaginatedApiResponse<RiskCase>
    } catch (error) {
      console.error('Error fetching cases:', error)
      throw error
    }
  }

  async getById(id: number): Promise<ApiResponse<RiskCase>> {
    return await apiClient.get(`/cases/${id}`) as unknown as ApiResponse<RiskCase>
  }

  async create(data: RiskCasePayload): Promise<ApiResponse<RiskCase>> {
    return await apiClient.post('/cases', data) as unknown as ApiResponse<RiskCase>
  }

  async update(id: number, data: RiskCasePayload): Promise<ApiResponse<RiskCase>> {
    return await apiClient.put(`/cases/${id}`, data) as unknown as ApiResponse<RiskCase>
  }

  async delete(id: number): Promise<ApiResponse<null>> {
    return await apiClient.delete(`/cases/${id}`) as unknown as ApiResponse<null>
  }

  // Additional operations
  async getByStatus(
    status: string,
    page: number = 0,
    size: number = 20
  ): Promise<PaginatedApiResponse<RiskCase>> {
    return await apiClient.get(`/cases/status/${status}`, { params: { page, size } }) as unknown as PaginatedApiResponse<RiskCase>
  }

  async getPending(page: number = 0, size: number = 20): Promise<PaginatedApiResponse<RiskCase>> {
    return await apiClient.get('/cases/pending', { params: { page, size } }) as unknown as PaginatedApiResponse<RiskCase>
  }

  async approve(id: number): Promise<ApiResponse<RiskCase>> {
    return await apiClient.put(`/cases/${id}/approve`) as unknown as ApiResponse<RiskCase>
  }

  async reject(id: number): Promise<ApiResponse<RiskCase>> {
    return await apiClient.put(`/cases/${id}/reject`) as unknown as ApiResponse<RiskCase>
  }

  async analyze(id: number, promptVersion?: string): Promise<ApiResponse<Record<string, unknown>>> {
    const params: Record<string, string> = {}
    if (promptVersion) params.promptVersion = promptVersion
    return await apiClient.post(
      `/cases/${id}/analyze`,
      {},
      {
        params,
        timeout: 120000
      }
    ) as unknown as ApiResponse<Record<string, unknown>>
  }

  async getAIDecision(caseId: number): Promise<ApiResponse<Record<string, unknown> | null>> {
    return await apiClient.get(`/ai-decisions/case/${caseId}`) as unknown as ApiResponse<Record<string, unknown> | null>
  }
}

export default new CaseAPI()
