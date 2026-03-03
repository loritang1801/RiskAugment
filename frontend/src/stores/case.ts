import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import caseApi from '@/api/caseApi'
import type { RiskCase, RiskCasePayload } from '@/types/case'

export const useCaseStore = defineStore('case', () => {
  // State
  const cases = ref<RiskCase[]>([])
  const currentCase = ref<RiskCase | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const pagination = ref({
    page: 0,
    size: 20,
    total: 0
  })

  // Computed
  const caseCount = computed(() => cases.value.length)
  const hasError = computed(() => error.value !== null)

  // Actions
  async function fetchCases(
    page: number = 0,
    size: number = 20,
    filters?: Record<string, unknown>
  ) {
    loading.value = true
    error.value = null
    try {
      const response = await caseApi.list(page, size, filters)
      if (response.status === 'success') {
        cases.value = response.data ?? []
        pagination.value = {
          page: response.page || page,
          size: response.size || size,
          total: response.total || (response.data?.length || 0)
        }
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  async function fetchCaseById(id: number) {
    loading.value = true
    error.value = null
    try {
      const response = await caseApi.getById(id)
      if (response.status === 'success' && response.data) {
        currentCase.value = response.data
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  async function createCase(data: RiskCasePayload) {
    loading.value = true
    error.value = null
    try {
      const response = await caseApi.create(data)
      if (response.status === 'success' && response.data) {
        cases.value.push(response.data)
        return response.data
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  async function updateCase(id: number, data: RiskCasePayload) {
    loading.value = true
    error.value = null
    try {
      const response = await caseApi.update(id, data)
      if (response.status === 'success' && response.data) {
        const index = cases.value.findIndex((c) => c.id === id)
        if (index !== -1) {
          cases.value[index] = response.data
        }
        return response.data
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  async function deleteCase(id: number) {
    loading.value = true
    error.value = null
    try {
      await caseApi.delete(id)
      cases.value = cases.value.filter((c) => c.id !== id)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    cases,
    currentCase,
    loading,
    error,
    pagination,
    // Computed
    caseCount,
    hasError,
    // Actions
    fetchCases,
    fetchCaseById,
    createCase,
    updateCase,
    deleteCase
  }
})
