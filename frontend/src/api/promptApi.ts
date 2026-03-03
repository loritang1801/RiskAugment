import { apiCall } from './utils'
import type { ApiResponse } from '@/types/api'

export interface PromptDto {
  id: number
  version: string
  system_prompt: string
  user_prompt_template: string
  description?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

type PromptListResponse = ApiResponse<PromptDto[]> & { total?: number }

export const getAllPrompts = async (): Promise<PromptListResponse> => {
  return await apiCall<PromptListResponse>('get', '/prompts')
}

export const getPromptByVersion = async (version: string): Promise<ApiResponse<PromptDto>> => {
  return await apiCall<ApiResponse<PromptDto>>('get', `/prompts/${version}`)
}

export const getActivePrompt = async (): Promise<ApiResponse<PromptDto>> => {
  return await apiCall<ApiResponse<PromptDto>>('get', '/prompts/active')
}

export const createPrompt = async (data: {
  version: string
  system_prompt: string
  user_prompt_template: string
  description?: string
}): Promise<ApiResponse<PromptDto>> => {
  return await apiCall<ApiResponse<PromptDto>>('post', '/prompts', data)
}

export const updatePrompt = async (version: string, data: {
  system_prompt?: string
  user_prompt_template?: string
  description?: string
}): Promise<ApiResponse<PromptDto>> => {
  return await apiCall<ApiResponse<PromptDto>>('put', `/prompts/${version}`, data)
}

export const activatePrompt = async (version: string): Promise<ApiResponse<PromptDto>> => {
  return await apiCall<ApiResponse<PromptDto>>('put', `/prompts/${version}/activate`, {})
}

export const deletePrompt = async (version: string): Promise<ApiResponse<null>> => {
  return await apiCall<ApiResponse<null>>('delete', `/prompts/${version}`)
}
