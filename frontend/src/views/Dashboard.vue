<template>
  <div class="dashboard">
    <a-row :gutter="[16, 16]">
      <a-col
        :xs="24"
        :sm="12"
        :md="6"
      >
        <a-card>
          <a-statistic
            title="待处理案件"
            :value="pendingCount"
            :value-style="{ color: '#ff4d4f' }"
          />
        </a-card>
      </a-col>
      <a-col
        :xs="24"
        :sm="12"
        :md="6"
      >
        <a-card>
          <a-statistic
            title="高风险案件"
            :value="highRiskCount"
            :value-style="{ color: '#faad14' }"
          />
        </a-card>
      </a-col>
      <a-col
        :xs="24"
        :sm="12"
        :md="6"
      >
        <a-card>
          <a-statistic
            title="今日通过"
            :value="todayApproved"
            :value-style="{ color: '#52c41a' }"
          />
        </a-card>
      </a-col>
      <a-col
        :xs="24"
        :sm="12"
        :md="6"
      >
        <a-card>
          <a-statistic
            title="平均审核时长(秒)"
            :value="avgReviewTime"
            :value-style="{ color: '#1890ff' }"
          />
        </a-card>
      </a-col>
    </a-row>

    <a-row
      :gutter="[16, 16]"
      style="margin-top: 24px"
    >
      <a-col
        :xs="24"
        :md="12"
      >
        <a-card title="案件状态分布">
          <div
            ref="statusChartEl"
            class="chart"
          />
        </a-card>
      </a-col>
      <a-col
        :xs="24"
        :md="12"
      >
        <a-card title="风险等级分布">
          <div
            ref="riskChartEl"
            class="chart"
          />
        </a-card>
      </a-col>
    </a-row>

    <a-row
      :gutter="[16, 16]"
      style="margin-top: 24px"
    >
      <a-col :xs="24">
        <a-card title="最近案件">
          <a-table
            :columns="columns"
            :data-source="recentCases"
            :loading="loading"
            :pagination="false"
            row-key="id"
            size="small"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'riskLevel'">
                <a-tag :color="getRiskLevelColor(record.riskLevel)">
                  {{ getRiskLevelLabel(record.riskLevel) }}
                </a-tag>
              </template>
              <template v-else-if="column.key === 'riskStatus'">
                <a-tag :color="getStatusColor(record.riskStatus)">
                  {{ getStatusLabel(record.riskStatus) }}
                </a-tag>
              </template>
              <template v-else-if="column.key === 'action'">
                <router-link :to="`/cases/${record.id}`">
                  查看
                </router-link>
              </template>
            </template>
          </a-table>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { message } from 'ant-design-vue'
import caseApi from '@/api/caseApi'

type RiskCase = {
  id: number
  bizTransactionId?: string
  amount?: number
  riskLevel?: string
  riskStatus?: string
}

const pendingCount = ref(0)
const highRiskCount = ref(0)
const todayApproved = ref(0)
const avgReviewTime = ref(0)
const loading = ref(false)
const recentCases = ref<RiskCase[]>([])
const allCases = ref<RiskCase[]>([])
const statusChartEl = ref<HTMLElement | null>(null)
const riskChartEl = ref<HTMLElement | null>(null)

type EChartsType = import('echarts/core').EChartsType
type EchartsModule = typeof import('@/utils/echarts')
let echartsLib: EchartsModule['echarts'] | null = null
let statusChart: EChartsType | null = null
let riskChart: EChartsType | null = null

const columns = [
  { title: '交易ID', dataIndex: 'bizTransactionId', key: 'bizTransactionId' },
  { title: '金额', dataIndex: 'amount', key: 'amount' },
  { title: '风险等级', dataIndex: 'riskLevel', key: 'riskLevel' },
  { title: '状态', dataIndex: 'riskStatus', key: 'riskStatus' },
  { title: '操作', key: 'action' }
]

const getRiskLevelColor = (level: string) => {
  const colors: Record<string, string> = {
    LOW: 'green',
    MEDIUM: 'orange',
    HIGH: 'red'
  }
  return colors[level] || 'default'
}

const getRiskLevelLabel = (level?: string) => {
  const labels: Record<string, string> = {
    LOW: '低风险',
    MEDIUM: '中风险',
    HIGH: '高风险'
  }
  return labels[level || ''] || level || '-'
}

const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    PENDING: 'blue',
    ANALYZING: 'orange',
    APPROVED: 'green',
    REJECTED: 'red'
  }
  return colors[status] || 'default'
}

const getStatusLabel = (status?: string) => {
  const labels: Record<string, string> = {
    PENDING: '待审核',
    ANALYZING: '分析中',
    APPROVED: '已通过',
    REJECTED: '已拒绝'
  }
  return labels[status || ''] || status || '-'
}

const normalizeCases = (response: any): RiskCase[] => {
  const payload = response?.data ?? response
  if (Array.isArray(payload)) return payload
  if (Array.isArray(payload?.content)) return payload.content
  if (Array.isArray(response?.data?.content)) return response.data.content
  return []
}

const loadEcharts = async () => {
  if (!echartsLib) {
    const module = await import('@/utils/echarts')
    echartsLib = module.echarts
  }
  return echartsLib
}

const renderStatusChart = async (cases: RiskCase[]) => {
  if (!statusChartEl.value) return
  const echarts = await loadEcharts()
  if (!statusChart) {
    statusChart = echarts.init(statusChartEl.value)
  }

  const counts = {
    PENDING: cases.filter((c) => c.riskStatus === 'PENDING').length,
    ANALYZING: cases.filter((c) => c.riskStatus === 'ANALYZING').length,
    APPROVED: cases.filter((c) => c.riskStatus === 'APPROVED').length,
    REJECTED: cases.filter((c) => c.riskStatus === 'REJECTED').length
  }

  statusChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [
      {
        name: '案件状态',
        type: 'pie',
        radius: ['35%', '65%'],
        data: [
          { value: counts.PENDING, name: '待处理' },
          { value: counts.ANALYZING, name: '分析中' },
          { value: counts.APPROVED, name: '已通过' },
          { value: counts.REJECTED, name: '已拒绝' }
        ]
      }
    ]
  })
}

const renderRiskChart = async (cases: RiskCase[]) => {
  if (!riskChartEl.value) return
  const echarts = await loadEcharts()
  if (!riskChart) {
    riskChart = echarts.init(riskChartEl.value)
  }

  const counts = {
    LOW: cases.filter((c) => c.riskLevel === 'LOW').length,
    MEDIUM: cases.filter((c) => c.riskLevel === 'MEDIUM').length,
    HIGH: cases.filter((c) => c.riskLevel === 'HIGH').length
  }

  riskChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: ['低风险', '中风险', '高风险']
    },
    yAxis: { type: 'value', minInterval: 1 },
    series: [
      {
        name: '案件数',
        type: 'bar',
        data: [
          { value: counts.LOW, itemStyle: { color: '#52c41a' } },
          { value: counts.MEDIUM, itemStyle: { color: '#faad14' } },
          { value: counts.HIGH, itemStyle: { color: '#ff4d4f' } }
        ],
        barMaxWidth: 48
      }
    ]
  })
}

const renderCharts = async () => {
  await nextTick()
  await renderStatusChart(allCases.value)
  await renderRiskChart(allCases.value)
}

const handleResize = () => {
  statusChart?.resize()
  riskChart?.resize()
}

const loadDashboardData = async () => {
  loading.value = true
  try {
    const response = await caseApi.list(0, 1000)
    const cases = normalizeCases(response)

    allCases.value = cases
    pendingCount.value = cases.filter((c) => c.riskStatus === 'PENDING').length
    highRiskCount.value = cases.filter((c) => c.riskLevel === 'HIGH').length
    todayApproved.value = cases.filter((c) => c.riskStatus === 'APPROVED').length
    avgReviewTime.value = 45
    recentCases.value = cases.slice(0, 5)
    await renderCharts()
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
    message.error('加载仪表板数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDashboardData()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  statusChart?.dispose()
  riskChart?.dispose()
  statusChart = null
  riskChart = null
})
</script>

<style scoped>
.dashboard {
  padding: 24px;
}

.chart {
  height: 320px;
}
</style>
