<template>
  <div class="audit-trail-container">
    <a-card
      title="案件审计追踪"
      :bordered="false"
    >
      <template #extra>
        <a-button
          type="primary"
          @click="refreshData"
        >
          刷新
        </a-button>
      </template>

      <a-descriptions
        :column="2"
        bordered
        size="small"
        class="case-info"
      >
        <a-descriptions-item label="案件ID">
          {{ caseInfo?.id }}
        </a-descriptions-item>
        <a-descriptions-item label="交易ID">
          {{ caseInfo?.bizTransactionId }}
        </a-descriptions-item>
        <a-descriptions-item label="金额">
          {{ caseInfo?.amount }} {{ caseInfo?.currency }}
        </a-descriptions-item>
        <a-descriptions-item label="风险等级">
          <a-tag :color="getRiskLevelColor(caseInfo?.riskLevel)">
            {{ getRiskLevelLabel(caseInfo?.riskLevel) }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="案件状态">
          <a-tag :color="getStatusColor(caseInfo?.riskStatus)">
            {{ getStatusLabel(caseInfo?.riskStatus) }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="创建时间">
          {{ formatTime(caseInfo?.createdAt) }}
        </a-descriptions-item>
      </a-descriptions>

      <div class="timeline-section">
        <h3>执行链路</h3>
        <a-timeline>
          <a-timeline-item
            v-for="log in auditLogs"
            :key="log.id"
            :color="getOperationColor(log.operation)"
          >
            <div class="timeline-content">
              <div class="operation-header">
                <span class="operation-badge">{{ log.operation }}</span>
                <span
                  v-if="log.operatorName"
                  class="operator-info"
                >操作人: {{ log.operatorName }}</span>
                <span class="timestamp">{{ formatTime(log.createdAt) }}</span>
              </div>
              <div
                v-if="log.newValue"
                class="operation-details"
              >
                <a-button
                  type="link"
                  size="small"
                  @click="toggleDetails(log.id)"
                >
                  {{ expandedLogs.has(log.id) ? '隐藏' : '显示' }}详情
                </a-button>
                <div
                  v-if="expandedLogs.has(log.id)"
                  class="details-content"
                >
                  <a-descriptions
                    :column="1"
                    size="small"
                    bordered
                  >
                    <a-descriptions-item
                      v-for="(value, key) in log.newValue"
                      :key="key"
                      :label="key"
                    >
                      <span v-if="typeof value === 'object'">{{ JSON.stringify(value) }}</span>
                      <span v-else>{{ value }}</span>
                    </a-descriptions-item>
                  </a-descriptions>
                </div>
              </div>
            </div>
          </a-timeline-item>
        </a-timeline>
      </div>

      <a-empty
        v-if="auditLogs.length === 0"
        description="暂无审计日志"
      />
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import { getExecutionChainApi } from '@/api/auditApi'
import type { AuditCaseInfo as CaseInfo, AuditLog } from '@/api/auditApi'

const route = useRoute()
const caseId = ref<number>(Number(route.params.caseId))
const auditLogs = ref<AuditLog[]>([])
const caseInfo = ref<CaseInfo | null>(null)
const expandedLogs = ref<Set<number>>(new Set())
const loading = ref(false)

const getExecutionChain = async () => {
  loading.value = true
  try {
    const data = await getExecutionChainApi(caseId.value)
    if (data) {
      caseInfo.value = data.case
      auditLogs.value = data.auditLogs || []
    }
  } catch (error) {
    message.error('获取审计追踪失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  getExecutionChain()
}

const toggleDetails = (logId: number) => {
  if (expandedLogs.value.has(logId)) {
    expandedLogs.value.delete(logId)
  } else {
    expandedLogs.value.add(logId)
  }
}

const formatTime = (time: string | undefined) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

const getOperationColor = (operation: string) => {
  const colors: Record<string, string> = {
    CREATE: 'green',
    ANALYZE: 'blue',
    APPROVE: 'green',
    REJECT: 'red',
    OVERRIDE: 'orange'
  }
  return colors[operation] || 'gray'
}

const getRiskLevelColor = (level: string | undefined) => {
  const colors: Record<string, string> = {
    LOW: 'green',
    MEDIUM: 'orange',
    HIGH: 'red'
  }
  return colors[level || ''] || 'default'
}

const getRiskLevelLabel = (level: string | undefined) => {
  const labels: Record<string, string> = {
    LOW: '低风险',
    MEDIUM: '中风险',
    HIGH: '高风险'
  }
  return labels[level || ''] || level || '-'
}

const getStatusColor = (status: string | undefined) => {
  const colors: Record<string, string> = {
    PENDING: 'blue',
    ANALYZING: 'processing',
    APPROVED: 'green',
    REJECTED: 'red'
  }
  return colors[status || ''] || 'default'
}

const getStatusLabel = (status: string | undefined) => {
  const labels: Record<string, string> = {
    PENDING: '待审核',
    ANALYZING: '分析中',
    APPROVED: '已通过',
    REJECTED: '已拒绝'
  }
  return labels[status || ''] || status || '-'
}

onMounted(() => {
  getExecutionChain()
})
</script>

<style scoped>
.audit-trail-container {
  padding: 20px;
}

.case-info {
  margin-bottom: 30px;
}

.timeline-section {
  margin-top: 30px;
}

.timeline-section h3 {
  margin-bottom: 20px;
  font-size: 16px;
  font-weight: 600;
}

.timeline-content {
  padding: 10px 0;
}

.operation-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 10px;
}

.operation-badge {
  display: inline-block;
  padding: 4px 12px;
  background-color: #f0f0f0;
  border-radius: 4px;
  font-weight: 600;
  font-size: 12px;
}

.operator-info {
  font-size: 12px;
  color: #666;
}

.timestamp {
  font-size: 12px;
  color: #999;
  margin-left: auto;
}

.operation-details {
  margin-top: 10px;
}

.details-content {
  margin-top: 10px;
  padding: 10px;
  background-color: #fafafa;
  border-radius: 4px;
}
</style>
