import apiClient from './utils'
import type { ApiResponse, PaginatedApiResponse } from '@/types/api'
import type { User, CreateUserRequest, UpdateUserRequest } from '@/types/user'

const userApi = {
  async list(page = 0, size = 20): Promise<PaginatedApiResponse<User>> {
    const response = await apiClient.get('/users', { params: { page, size } })
    return response as unknown as PaginatedApiResponse<User>
  },

  async listByRole(role: 'ADMIN' | 'REVIEWER' | 'ANALYST', page = 0, size = 20): Promise<PaginatedApiResponse<User>> {
    const response = await apiClient.get(`/users/role/${role}`, { params: { page, size } })
    return response as unknown as PaginatedApiResponse<User>
  },

  async create(data: CreateUserRequest): Promise<ApiResponse<User>> {
    const response = await apiClient.post('/users', data)
    return response as unknown as ApiResponse<User>
  },

  async update(id: number, data: UpdateUserRequest): Promise<ApiResponse<User>> {
    const response = await apiClient.put(`/users/${id}`, data)
    return response as unknown as ApiResponse<User>
  },

  async deactivate(id: number): Promise<ApiResponse<User>> {
    const response = await apiClient.put(`/users/${id}/deactivate`)
    return response as unknown as ApiResponse<User>
  },

  async delete(id: number): Promise<ApiResponse<null>> {
    const response = await apiClient.delete(`/users/${id}`)
    return response as unknown as ApiResponse<null>
  }
}

export default userApi
