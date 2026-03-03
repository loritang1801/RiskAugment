<template>
  <div class="case-detail-page">
    <a-card class="header-card" :bordered="false">
      <div class="header-top">
        <div>
          <div class="page-title">案件详情</div>
          <div class="page-subtitle">Case ID: {{ caseId }}</div>
        </div>
        <a-space wrap>
          <a-button @click="$router.back()">返回</a-button>
          <a-button type="primary" :loading="analyzing" @click="handleAnalyze">分析</a-button>
          <a-button type="primary" danger @click="handleReject">拒绝</a-button>
          <a-button type="primary" @click="handleApprove">批准</a-button>
          <a-button @click="goToAuditTrail">审计轨迹</a-button>
        </a-space>
      </div>
    </a-card>

    <a-row :gutter="[16, 16]">
      <a-col :xs="24" :xl="16">
        <a-card title="案件基础信息" :bordered="false">
          <a-spin :spinning="loading">
            <a-descriptions :column="2" bordered size="small">
              <a-descriptions-item label="交易 ID">{{ currentCase?.bizTransactionId || '-' }}</a-descriptions-item>
              <a-descriptions-item label="金额">{{ currentCase?.amount }} {{ currentCase?.currency }}</a-descriptions-item>
              <a-descriptions-item label="国家">{{ currentCase?.country || '-' }}</a-descriptions-item>
              <a-descriptions-item label="设备风险">{{ currentCase?.deviceRisk || '-' }}</a-descriptions-item>
              <a-descriptions-item label="用户标签">{{ currentCase?.userLabel || '-' }}</a-descriptions-item>
              <a-descriptions-item label="风险等级">
                <a-tag :color="getRiskLevelColor(currentCase?.riskLevel)">{{ riskLevelLabel(currentCase?.riskLevel) }}</a-tag>
              </a-descriptions-item>
              <a-descriptions-item label="案件状态">
                <a-tag :color="getStatusColor(currentCase?.riskStatus)">{{ getStatusLabel(currentCase?.riskStatus) }}</a-tag>
              </a-descriptions-item>
              <a-descriptions-item label="风险评分">{{ currentCase?.riskScore ?? '-' }}</a-descriptions-item>
              <a-descriptions-item label="创建时间">{{ formatDate(currentCase?.createdAt) }}</a-descriptions-item>
              <a-descriptions-item label="更新时间">{{ formatDate(currentCase?.updatedAt) }}</a-descriptions-item>
            </a-descriptions>
          </a-spin>
        </a-card>

        <a-card class="section-card" title="AI 分析结果" :bordered="false">
          <a-empty v-if="!normalizedAIDecision" description="暂无 AI 分析结果" />
          <template v-else>
            <div class="analysis-top-grid">
              <div class="metric-card">
                <div class="metric-label">分析来源</div>
                <div class="metric-value">{{ normalizedAIDecision.analysisSource || '-' }}</div>
                <div class="metric-sub">{{ normalizedAIDecision.analysisModel || '-' }}</div>
              </div>
              <div class="metric-card">
                <div class="metric-label">建议操作</div>
                <div class="metric-value">
                  <a-tag :color="getActionColor(normalizedAIDecision.suggestedAction)">
                    {{ actionLabel(normalizedAIDecision.suggestedAction) }}
                  </a-tag>
                </div>
              </div>
              <div class="metric-card">
                <div class="metric-label">风险等级</div>
                <div class="metric-value">
                  <a-tag :color="getRiskLevelColor(normalizedAIDecision.riskLevel)">
                    {{ riskLevelLabel(normalizedAIDecision.riskLevel) }}
                  </a-tag>
                </div>
              </div>
              <div class="metric-card">
                <div class="metric-label">置信度 / 耗时</div>
                <div class="metric-value">{{ normalizedAIDecision.confidenceScore ?? '-' }}</div>
                <div class="metric-sub">{{ normalizedAIDecision.totalTimeMs ?? '-' }} ms</div>
              </div>
            </div>

            <a-divider />
            <h4 class="block-title">分析理由</h4>
            <div class="text-block">{{ normalizedAIDecision.reasoning || '-' }}</div>

            <h4 class="block-title">关键风险点</h4>
            <div v-if="Array.isArray(normalizedAIDecision.keyRiskPoints)" class="risk-points">
              <div v-for="(point, index) in normalizedAIDecision.keyRiskPoints" :key="index">- {{ point }}</div>
            </div>
            <div v-else class="text-block">{{ normalizedAIDecision.keyRiskPoints || '-' }}</div>

            <h4 class="block-title">规则引擎对齐</h4>
            <div class="text-block">{{ normalizedAIDecision.ruleEngineAlignment || '-' }}</div>

            <a-divider />
            <h4 class="block-title">相似案件分析</h4>
            <div class="text-block">{{ normalizedAIDecision.similarCasesAnalysis || '-' }}</div>

            <div v-if="similarCaseStats" class="summary-grid">
              <div class="summary-box">
                <span>样本数</span>
                <strong>{{ similarCaseStats.total }}</strong>
              </div>
              <div class="summary-box">
                <span>平均相似度</span>
                <strong>{{ similarCaseStats.avgSimilarity }}</strong>
              </div>
              <div class="summary-box">
                <span>历史通过率</span>
                <strong>{{ similarCaseStats.approvalRate }}</strong>
              </div>
              <div class="summary-box">
                <span>历史拒绝率</span>
                <strong>{{ similarCaseStats.rejectionRate }}</strong>
              </div>
              <div class="summary-box wide">
                <span>来源分布</span>
                <strong>{{ similarCaseStats.sourceSummary }}</strong>
              </div>
            </div>

            <h4 class="block-title">相似案件明细（可点击跳转）</h4>
            <a-empty v-if="!similarCasesForDisplay.length" description="暂无相似案件明细" />
            <div v-else class="table-wrap">
              <a-table
                :columns="similarCasesColumns"
                :data-source="similarCasesForDisplay"
                :pagination="false"
                :scroll="{ x: 1700, y: 420 }"
                size="middle"
                row-key="rowKey"
              />
            </div>
          </template>
        </a-card>
      </a-col>

      <a-col :xs="24" :xl="8">
        <a-card title="风险特征详情" :bordered="false">
          <div v-if="riskFeaturesDisplay" class="feature-list">
            <div v-for="(value, key) in riskFeaturesDisplay" :key="key" class="feature-row">
              <span class="feature-key">{{ key }}</span>
              <span class="feature-value">{{ value }}</span>
            </div>
          </div>
          <a-empty v-else description="暂无风险特征数据" />
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup lang="ts">
import { computed, h, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { useCaseStore } from '@/stores/case'
import caseApi from '@/api/caseApi'
import type { RiskFeatures } from '@/types/case'

const route = useRoute()
const router = useRouter()
const caseStore = useCaseStore()

const caseId = computed(() => String(route.params.id ?? ''))
const currentCase = computed(() => caseStore.currentCase)
const loading = computed(() => caseStore.loading)
const analyzing = ref(false)
const aiDecision = ref<Record<string, unknown> | null>(null)

interface SimilarCaseDetail {
  rowKey: string
  caseId?: string
  bizTransactionId?: string
  similarity?: number
  riskLevel?: string
  finalDecision?: string
  amount?: number | string
  currency?: string
  country?: string
  matchSource?: string
  similarityReason?: string
}

interface NormalizedAIDecision {
  id?: number
  suggestedAction?: string
  confidenceScore?: number
  riskLevel?: string
  keyRiskPoints?: string[] | string
  reasoning?: string
  similarCasesAnalysis?: string
  similarCasesDetails?: SimilarCaseDetail[]
  ruleEngineAlignment?: string
  totalTimeMs?: number
  analysisSource?: string
  analysisModel?: string
}

const asString = (value: unknown): string | undefined => (typeof value === 'string' ? value : undefined)

const asNumber = (value: unknown): number | undefined => {
  if (typeof value === 'number') return Number.isFinite(value) ? value : undefined
  if (typeof value === 'string') {
    const parsed = Number(value.trim())
    return Number.isFinite(parsed) ? parsed : undefined
  }
  return undefined
}

const asStringListOrString = (value: unknown): string[] | string | undefined => {
  if (Array.isArray(value) && value.every((item) => typeof item === 'string')) return value
  return typeof value === 'string' ? value : undefined
}

const asObjectList = (value: unknown): Record<string, unknown>[] | undefined => {
  if (Array.isArray(value) && value.every((item) => item && typeof item === 'object' && !Array.isArray(item))) {
    return value as Record<string, unknown>[]
  }
  if (typeof value === 'string') {
    try {
      const parsed = JSON.parse(value)
      if (Array.isArray(parsed) && parsed.every((item) => item && typeof item === 'object' && !Array.isArray(item))) {
        return parsed as Record<string, unknown>[]
      }
    } catch {
      return undefined
    }
  }
  return undefined
}

const asIdString = (value: unknown): string | undefined => {
  const str = asString(value)
  if (str) return str
  const num = asNumber(value)
  return num !== undefined ? String(num) : undefined
}

const isDisplayableAIDecision = (value: unknown): boolean => {
  if (!value || typeof value !== 'object') return false
  const payload = value as Record<string, unknown>
  return !!(
    asString(payload.risk_level) ||
    asString(payload.riskLevel) ||
    asString(payload.reasoning) ||
    asString(payload.similar_cases_analysis) ||
    asString(payload.similarCasesAnalysis)
  )
}

const riskLevelLabel = (value?: string): string => {
  const level = (value ?? '').toUpperCase()
  if (level === 'LOW') return '低风险'
  if (level === 'MEDIUM') return '中风险'
  if (level === 'HIGH') return '高风险'
  return value ?? '-'
}

const actionLabel = (value?: string): string => {
  const action = (value ?? '').toUpperCase()
  if (action === 'APPROVE') return '通过'
  if (action === 'REJECT') return '拒绝'
  if (action === 'MANUAL_REVIEW' || action === 'REVIEW') return '人工复核'
  return value ?? '-'
}

const sourceLabel = (value?: string): string => {
  const source = (value ?? '').toLowerCase()
  if (source === 'rag') return 'RAG 语义检索'
  if (source === 'relaxed_rag') return '宽松阈值检索'
  if (source === 'criteria_fallback') return '条件回退检索'
  if (source === 'heuristic_proxy') return '启发式代理样本'
  return value ?? '-'
}

const normalizeSimilarCaseDetails = (value: unknown): SimilarCaseDetail[] | undefined => {
  const rows = asObjectList(value)
  if (!rows?.length) return undefined

  return rows.map((row, index) => ({
    rowKey: `${asIdString(row.case_id) ?? asIdString(row.caseId) ?? index}`,
    caseId: asIdString(row.case_id) ?? asIdString(row.caseId),
    bizTransactionId: asString(row.biz_transaction_id) ?? asString(row.bizTransactionId),
    similarity: asNumber(row.similarity),
    riskLevel: asString(row.risk_level) ?? asString(row.riskLevel),
    finalDecision: asString(row.final_decision) ?? asString(row.finalDecision),
    amount: asNumber(row.amount) ?? asString(row.amount),
    currency: asString(row.currency),
    country: asString(row.country),
    matchSource: asString(row.match_source) ?? asString(row.matchSource)
  }))
}

const isNumericId = (value?: string): boolean => Boolean(value && /^\d+$/.test(value))

const navigateToCase = (targetCaseId?: string) => {
  const normalized = asIdString(targetCaseId)
  if (!isNumericId(normalized)) return
  if (String(normalized) === caseId.value) return
  router.push(`/cases/${normalized}`)
}

const renderCaseLink = (rawId: unknown, label: string) => {
  const normalized = asIdString(rawId)
  if (!isNumericId(normalized)) return label
  return h(
    'span',
    {
      class: 'link-cell',
      onClick: (e: MouseEvent) => {
        e.stopPropagation()
        navigateToCase(normalized)
      }
    },
    label
  )
}

const buildSimilarityReason = (detail: SimilarCaseDetail): string => {
  const reasons: string[] = []
  const current = currentCase.value
  if (!current) return '语义向量特征相近'

  if (current.country && detail.country && current.country === detail.country) reasons.push('同国家')
  if (current.riskLevel && detail.riskLevel && current.riskLevel === detail.riskLevel) reasons.push('同风险等级')
  if ((detail.matchSource ?? '').includes('rag')) reasons.push('历史语义匹配')

  const currentAmount = asNumber(current.amount)
  const detailAmount = typeof detail.amount === 'number' ? detail.amount : asNumber(detail.amount)
  if (currentAmount !== undefined && detailAmount !== undefined) {
    const denominator = Math.max(currentAmount, detailAmount, 1)
    const distance = Math.abs(currentAmount - detailAmount) / denominator
    if (distance <= 0.15) reasons.push('金额接近')
    else if (distance <= 0.35) reasons.push('金额中等差异')
  }

  return reasons.length ? reasons.join(' + ') : '语义向量特征相近'
}

const similarCasesForDisplay = computed<SimilarCaseDetail[]>(() => {
  const details = normalizedAIDecision.value?.similarCasesDetails ?? []
  return details.map((item) => ({
    ...item,
    similarityReason: buildSimilarityReason(item)
  }))
})

const similarCaseStats = computed(() => {
  const details = similarCasesForDisplay.value
  if (!details.length) return null

  const total = details.length
  const avgSimilarityRaw = details.reduce((sum, item) => sum + (item.similarity ?? 0), 0) / total
  const approved = details.filter((item) => (item.finalDecision ?? '').toUpperCase().includes('APPROVE')).length
  const rejected = details.filter((item) => (item.finalDecision ?? '').toUpperCase().includes('REJECT')).length
  const sourceMap: Record<string, number> = {}
  details.forEach((item) => {
    const source = sourceLabel(item.matchSource || 'unknown')
    sourceMap[source] = (sourceMap[source] ?? 0) + 1
  })

  return {
    total,
    avgSimilarity: `${(avgSimilarityRaw * 100).toFixed(1)}%`,
    approvalRate: `${((approved / total) * 100).toFixed(1)}%`,
    rejectionRate: `${((rejected / total) * 100).toFixed(1)}%`,
    sourceSummary: Object.entries(sourceMap).map(([key, count]) => `${key}:${count}`).join(', ')
  }
})

const similarCasesColumns = [
  {
    title: 'Case ID',
    dataIndex: 'caseId',
    key: 'caseId',
    width: 110,
    customRender: ({ text }: { text?: string | number }) => {
      const label = asIdString(text)
      if (!label) return '-'
      return renderCaseLink(text, label)
    }
  },
  {
    title: '交易流水',
    dataIndex: 'bizTransactionId',
    key: 'bizTransactionId',
    width: 180,
    customRender: ({ text, record }: { text?: string; record: SimilarCaseDetail }) => {
      if (!text) return '-'
      const node = renderCaseLink(record.caseId, text)
      return h('div', { style: 'white-space: normal; word-break: break-all;' }, node)
    }
  },
  {
    title: '相似度',
    dataIndex: 'similarity',
    key: 'similarity',
    width: 110,
    customRender: ({ text }: { text?: number }) => (typeof text === 'number' ? `${(text * 100).toFixed(1)}%` : '-')
  },
  {
    title: '风险等级',
    dataIndex: 'riskLevel',
    key: 'riskLevel',
    width: 110,
    customRender: ({ text }: { text?: string }) => riskLevelLabel(text)
  },
  {
    title: '历史决策',
    dataIndex: 'finalDecision',
    key: 'finalDecision',
    width: 120,
    customRender: ({ text }: { text?: string }) => actionLabel(text)
  },
  {
    title: '金额',
    key: 'amount',
    width: 150,
    customRender: ({ record }: { record: SimilarCaseDetail }) =>
      record.amount !== undefined && record.amount !== null ? `${record.amount} ${record.currency ?? ''}`.trim() : '-'
  },
  { title: '国家', dataIndex: 'country', key: 'country', width: 100 },
  {
    title: '来源',
    dataIndex: 'matchSource',
    key: 'matchSource',
    width: 150,
    customRender: ({ text }: { text?: string }) => sourceLabel(text)
  },
  {
    title: '相似性解释',
    dataIndex: 'similarityReason',
    key: 'similarityReason',
    width: 520,
    customRender: ({ text }: { text?: string }) =>
      h('div', { style: 'white-space: normal; word-break: break-word; line-height: 1.5;' }, text || '-')
  }
]

const riskFeaturesDisplay = computed(() => {
  if (!currentCase.value?.riskFeatures) return null

  const features = typeof currentCase.value.riskFeatures === 'string'
    ? (() => {
        try {
          return JSON.parse(currentCase.value.riskFeatures as string)
        } catch {
          return null
        }
      })()
    : currentCase.value.riskFeatures

  return features as RiskFeatures | null
})

const normalizedAIDecision = computed<NormalizedAIDecision | null>(() => {
  if (!aiDecision.value) return null
  if (!isDisplayableAIDecision(aiDecision.value)) return null

  const executionMetrics = (aiDecision.value.execution_metrics ?? aiDecision.value.executionMetrics) as Record<string, unknown> | undefined

  return {
    id: asNumber(aiDecision.value.id),
    suggestedAction: asString(aiDecision.value.suggested_action) ?? asString(aiDecision.value.suggestedAction),
    confidenceScore: asNumber(aiDecision.value.confidence_score) ?? asNumber(aiDecision.value.confidenceScore),
    riskLevel: asString(aiDecision.value.risk_level) ?? asString(aiDecision.value.riskLevel),
    keyRiskPoints: asStringListOrString(aiDecision.value.key_risk_points) ?? asStringListOrString(aiDecision.value.keyRiskPoints),
    reasoning: asString(aiDecision.value.reasoning),
    similarCasesAnalysis: asString(aiDecision.value.similar_cases_analysis) ?? asString(aiDecision.value.similarCasesAnalysis),
    similarCasesDetails:
      normalizeSimilarCaseDetails(aiDecision.value.similar_cases_details) ??
      normalizeSimilarCaseDetails(aiDecision.value.similarCasesDetails),
    ruleEngineAlignment: asString(aiDecision.value.rule_engine_alignment) ?? asString(aiDecision.value.ruleEngineAlignment),
    totalTimeMs:
      asNumber(aiDecision.value.totalTimeMs) ??
      asNumber(aiDecision.value.total_time_ms) ??
      (executionMetrics ? asNumber(executionMetrics.total_time_ms) ?? asNumber(executionMetrics.totalTimeMs) : undefined),
    analysisSource: asString(aiDecision.value.analysis_source) ?? asString(aiDecision.value.analysisSource),
    analysisModel: asString(aiDecision.value.analysis_model) ?? asString(aiDecision.value.analysisModel)
  }
})

const getRiskLevelColor = (level?: string) => {
  const colors: Record<string, string> = { LOW: 'green', MEDIUM: 'orange', HIGH: 'red' }
  return level ? colors[level] || 'default' : 'default'
}

const getStatusColor = (status?: string) => {
  const colors: Record<string, string> = { PENDING: 'blue', ANALYZING: 'orange', APPROVED: 'green', REJECTED: 'red' }
  return status ? colors[status] || 'default' : 'default'
}

const getStatusLabel = (status?: string) => {
  const labels: Record<string, string> = {
    PENDING: '待审核',
    ANALYZING: '分析中',
    APPROVED: '已通过',
    REJECTED: '已拒绝'
  }
  return status ? labels[status] || status : '-'
}

const getActionColor = (action?: string) => {
  const colors: Record<string, string> = { APPROVE: 'green', REJECT: 'red', REVIEW: 'orange', MANUAL_REVIEW: 'orange' }
  return action ? colors[action] || 'default' : 'default'
}

const formatDate = (date?: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

const fetchAIDecision = async (id: number) => {
  try {
    const response = await caseApi.getAIDecision(id)
    if (response.status === 'success') {
      const fresh = response.data ?? null
      const existingDetails =
        normalizeSimilarCaseDetails(aiDecision.value?.similar_cases_details) ??
        normalizeSimilarCaseDetails(aiDecision.value?.similarCasesDetails)

      if (fresh && existingDetails?.length) {
        const merged = {
          ...fresh,
          similar_cases_details:
            (fresh as Record<string, unknown>).similar_cases_details ??
            (fresh as Record<string, unknown>).similarCasesDetails ??
            existingDetails
        }
        aiDecision.value = isDisplayableAIDecision(merged) ? merged : null
      } else {
        aiDecision.value = isDisplayableAIDecision(fresh) ? fresh : null
      }
    }
  } catch (error) {
    console.error('Error fetching AI decision:', error)
  }
}

const loadCaseData = async (idString: string) => {
  const id = Number(idString)
  if (!Number.isFinite(id) || id <= 0) return
  aiDecision.value = null
  await caseStore.fetchCaseById(id)
  await fetchAIDecision(id)
}

const handleAnalyze = async () => {
  try {
    analyzing.value = true
    const id = Number(caseId.value)
    const response = await caseApi.analyze(id)
    if (response.status === 'success') {
      message.success('分析完成')
      if (response.data) {
        aiDecision.value = response.data
      }
      await caseStore.fetchCaseById(id)
      await fetchAIDecision(id)
    }
  } catch (error: any) {
    message.error(error.message || '分析失败')
  } finally {
    analyzing.value = false
  }
}

const handleApprove = async () => {
  try {
    const id = Number(caseId.value)
    const result = await caseApi.approve(id)
    if (result.status === 'success') {
      message.success('案件已批准')
      await caseStore.fetchCaseById(id)
    } else {
      message.error('批准失败')
    }
  } catch (error: any) {
    message.error(error.message || '操作失败')
  }
}

const handleReject = async () => {
  try {
    const id = Number(caseId.value)
    const result = await caseApi.reject(id)
    if (result.status === 'success') {
      message.success('案件已拒绝')
      await caseStore.fetchCaseById(id)
    } else {
      message.error('拒绝失败')
    }
  } catch (error: any) {
    message.error(error.message || '操作失败')
  }
}

const goToAuditTrail = () => {
  router.push(`/cases/${caseId.value}/audit-trail`)
}

watch(
  () => caseId.value,
  async (newId) => {
    await loadCaseData(newId)
  },
  { immediate: true }
)
</script>

<style scoped>
.case-detail-page {
  padding: 20px;
}

.header-card {
  margin-bottom: 16px;
  background: linear-gradient(120deg, #f6fbff 0%, #f7f7ff 100%);
}

.header-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: #102a43;
}

.page-subtitle {
  margin-top: 4px;
  color: #486581;
  font-size: 13px;
}

.section-card {
  margin-top: 16px;
}

.analysis-top-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.metric-card {
  border: 1px solid #e8eef7;
  border-radius: 8px;
  padding: 12px;
  background: #fbfdff;
}

.metric-label {
  color: #52606d;
  font-size: 12px;
  margin-bottom: 6px;
}

.metric-value {
  font-size: 16px;
  font-weight: 600;
  color: #102a43;
}

.metric-sub {
  font-size: 12px;
  color: #627d98;
  margin-top: 4px;
}

.block-title {
  margin: 10px 0 8px;
  font-size: 15px;
  color: #102a43;
}

.text-block {
  line-height: 1.7;
  color: #243b53;
  white-space: pre-wrap;
  word-break: break-word;
}

.risk-points {
  display: grid;
  gap: 6px;
  color: #243b53;
}

.summary-grid {
  margin-top: 12px;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.summary-box {
  border-radius: 8px;
  border: 1px solid #e8eef7;
  background: #fcfdff;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.summary-box span {
  font-size: 12px;
  color: #627d98;
}

.summary-box strong {
  font-size: 16px;
  color: #102a43;
}

.summary-box.wide {
  grid-column: 1 / -1;
}

.table-wrap {
  margin-top: 10px;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.feature-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  border-bottom: 1px dashed #e8eef7;
  padding-bottom: 6px;
}

.feature-key {
  color: #486581;
  font-size: 13px;
}

.feature-value {
  color: #102a43;
  font-weight: 600;
  text-align: right;
}

:deep(.link-cell) {
  color: #1677ff;
  cursor: pointer;
  text-decoration: underline;
}

:deep(.link-cell:hover) {
  color: #4096ff;
}

@media (max-width: 1200px) {
  .analysis-top-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .case-detail-page {
    padding: 12px;
  }

  .analysis-top-grid,
  .summary-grid {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
}
</style>
