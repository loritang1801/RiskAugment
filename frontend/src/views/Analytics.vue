<template>
  <div class="analytics-container">
    <a-card
      :bordered="false"
      style="margin-bottom: 16px"
    >
      <a-row
        :gutter="[16, 16]"
        align="middle"
      >
        <a-col
          :xs="24"
          :sm="12"
        >
          <h2 style="margin: 0">
            数据分析
          </h2>
        </a-col>
        <a-col
          :xs="24"
          :sm="12"
          style="text-align: right"
        >
          <a-space>
            <a-range-picker
              v-model:value="dateRange"
              show-time
              format="YYYY-MM-DD"
              @change="onDateRangeChange"
            />
            <a-button
              type="primary"
              @click="refreshData"
            >
              刷新
            </a-button>
          </a-space>
        </a-col>
      </a-row>
    </a-card>

    <a-row
      :gutter="[16, 16]"
      style="margin-bottom: 16px"
    >
      <a-col
        :xs="24"
        :sm="12"
        :md="6"
      >
        <a-statistic
          title="平均审核时间"
          :value="reviewEfficiency.averageReviewTime"
          suffix="ms"
          :value-style="{ color: '#1890ff' }"
        />
      </a-col>
      <a-col
        :xs="24"
        :sm="12"
        :md="6"
      >
        <a-statistic
          title="总案件数"
          :value="reviewEfficiency.totalCases"
          :value-style="{ color: '#52c41a' }"
        />
      </a-col>
      <a-col
        :xs="24"
        :sm="12"
        :md="6"
      >
        <a-statistic
          title="Override 率"
          :value="(overrideRate.overrideRate * 100).toFixed(2)"
          suffix="%"
          :value-style="{ color: '#ff7a45' }"
        />
      </a-col>
      <a-col
        :xs="24"
        :sm="12"
        :md="6"
      >
        <a-statistic
          title="Override 数"
          :value="overrideRate.overrideCount"
          :value-style="{ color: '#f5222d' }"
        />
      </a-col>
    </a-row>

    <a-card
      title="AI 分析链路健康"
      :bordered="false"
      :loading="loading"
      style="margin-bottom: 16px"
    >
      <a-row :gutter="[16, 16]">
        <a-col :xs="24" :sm="12" :md="6">
          <a-statistic
            title="最近窗口请求数"
            :value="chainHealth.total_requests"
            :value-style="{ color: '#1677ff' }"
          />
        </a-col>
        <a-col :xs="24" :sm="12" :md="6">
          <a-statistic
            title="失败率"
            :value="(chainHealth.failure_rate * 100).toFixed(2)"
            suffix="%"
            :value-style="{ color: chainHealth.failure_rate > 0.2 ? '#f5222d' : '#52c41a' }"
          />
        </a-col>
        <a-col :xs="24" :sm="12" :md="6">
          <a-statistic
            title="降级率"
            :value="((chainHealth.degraded_rate || 0) * 100).toFixed(2)"
            suffix="%"
            :value-style="{ color: (chainHealth.degraded_rate || 0) > 0.2 ? '#fa8c16' : '#52c41a' }"
          />
        </a-col>
        <a-col :xs="24" :sm="12" :md="6">
          <a-statistic
            title="P95 延迟"
            :value="chainHealth.latency_ms.p95"
            suffix="ms"
            :value-style="{ color: chainHealth.latency_ms.p95 > 6000 ? '#fa541c' : '#52c41a' }"
          />
        </a-col>
        <a-col :xs="24" :sm="12" :md="6">
          <a-statistic
            title="LLM 平均耗时"
            :value="chainHealth.stage_avg_ms.llm || 0"
            suffix="ms"
            :value-style="{ color: '#722ed1' }"
          />
        </a-col>
      </a-row>

      <a-alert
        v-if="chainHealth.degraded"
        type="warning"
        show-icon
        style="margin-top: 12px"
        message="当前为降级链路健康数据（AI 服务暂不可达），请检查 ai-service 状态。"
      />

      <a-table
        :columns="errorCategoryColumns"
        :data-source="errorCategoryRows"
        :pagination="false"
        size="small"
        row-key="category"
        style="margin-top: 12px"
      />
    </a-card>

    <a-row
      :gutter="[16, 16]"
      style="margin-bottom: 16px"
    >
      <a-col
        :xs="24"
        :md="12"
      >
        <a-card
          title="审核时间趋势"
          :bordered="false"
          :loading="loading"
        >
          <div
            ref="reviewEfficiencyChartRef"
            style="height: 300px"
          />
        </a-card>
      </a-col>
      <a-col
        :xs="24"
        :md="12"
      >
        <a-card
          title="Override 趋势"
          :bordered="false"
          :loading="loading"
        >
          <div
            ref="overrideRateChartRef"
            style="height: 300px"
          />
        </a-card>
      </a-col>
    </a-row>

    <a-row
      :gutter="[16, 16]"
      style="margin-bottom: 16px"
    >
      <a-col
        :xs="24"
        :md="12"
      >
        <a-card
          title="Prompt 版本对比"
          :bordered="false"
          :loading="loading"
        >
          <div
            v-if="promptVersions.length > 0"
            ref="promptComparisonChartRef"
            style="height: 300px"
          />
          <div
            v-else
            style="height: 300px; display: flex; align-items: center; justify-content: center; color: #999;"
          >
            暂无数据
          </div>
        </a-card>
      </a-col>
      <a-col
        :xs="24"
        :md="12"
      >
        <a-card
          title="各版本 Override 率"
          :bordered="false"
          :loading="loading"
        >
          <div
            v-if="promptVersions.length > 0"
            ref="overrideByVersionChartRef"
            style="height: 300px"
          />
          <div
            v-else
            style="height: 300px; display: flex; align-items: center; justify-content: center; color: #999;"
          >
            暂无数据
          </div>
        </a-card>
      </a-col>
    </a-row>

    <a-card
      title="Prompt 版本详细对比"
      :bordered="false"
      style="margin-bottom: 16px"
    >
      <a-table
        :columns="versionColumns"
        :data-source="promptVersions"
        :pagination="false"
        :loading="loading"
        row-key="version"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'approvalRate'">
            <a-progress
              :percent="parseFloat((record.approvalRate * 100).toFixed(1))"
              :status="record.approvalRate >= 0.8 ? 'success' : record.approvalRate >= 0.5 ? 'normal' : 'exception'"
            />
          </template>
          <template v-else-if="column.key === 'overrideRate'">
            <a-progress
              :percent="parseFloat((record.overrideRate * 100).toFixed(1))"
              :status="record.overrideRate <= 0.1 ? 'success' : record.overrideRate <= 0.2 ? 'normal' : 'exception'"
            />
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onBeforeUnmount, onMounted, nextTick } from 'vue'
import { message } from 'ant-design-vue'
import dayjs from 'dayjs'
import type { Dayjs } from 'dayjs'
import {
  getChainHealthApi,
  getOverrideRateApi,
  getPromptComparisonApi,
  getReviewEfficiencyApi
} from '@/api/analyticsApi'
import type {
  ChainHealthMetrics,
  OverrideRate,
  PromptVersion,
  ReviewEfficiency
} from '@/api/analyticsApi'

const loading = ref(false)
const reviewEfficiency = ref<ReviewEfficiency>({
  averageReviewTime: 0,
  totalCases: 0,
  minTime: 0,
  maxTime: 0
})
const overrideRate = ref<OverrideRate>({
  overrideRate: 0,
  totalDecisions: 0,
  overrideCount: 0
})
const promptVersions = ref<PromptVersion[]>([])
const chainHealth = ref<ChainHealthMetrics>({
  window_size: 200,
  total_requests: 0,
  success_requests: 0,
  degraded_requests: 0,
  failed_requests: 0,
  degraded_rate: 0,
  failure_rate: 0,
  degraded: false,
  error_categories: {},
  latency_ms: {
    avg: 0,
    p50: 0,
    p95: 0,
    max: 0
  },
  stage_avg_ms: {
    rule: 0,
    retrieval: 0,
    similar_analysis: 0,
    transaction_history: 0,
    llm: 0,
    total: 0
  }
})
const dateRange = ref<[Dayjs, Dayjs]>([dayjs().subtract(30, 'days'), dayjs()])

type EChartsType = import('echarts/core').EChartsType
type EchartsModule = typeof import('@/utils/echarts')
let echartsLib: EchartsModule['echarts'] | null = null
const charts = new Map<string, EChartsType>()
const reviewEfficiencyChartRef = ref<HTMLElement | null>(null)
const overrideRateChartRef = ref<HTMLElement | null>(null)
const promptComparisonChartRef = ref<HTMLElement | null>(null)
const overrideByVersionChartRef = ref<HTMLElement | null>(null)
const handleWindowResize = () => {
  charts.forEach((chart) => chart.resize())
}

const versionColumns = [
  { title: 'Prompt 版本', dataIndex: 'version', key: 'version', width: 100 },
  { title: '总案件数', dataIndex: 'totalCases', key: 'totalCases', width: 100 },
  { title: '批准数', dataIndex: 'approvedCases', key: 'approvedCases', width: 100 },
  { title: '拒绝数', dataIndex: 'rejectedCases', key: 'rejectedCases', width: 100 },
  { title: '批准率', dataIndex: 'approvalRate', key: 'approvalRate', width: 150 },
  { title: 'Override 率', dataIndex: 'overrideRate', key: 'overrideRate', width: 150 },
  { title: '平均审核时间(ms)', dataIndex: 'averageReviewTime', key: 'averageReviewTime', width: 150 }
]

const errorCategoryColumns = [
  { title: '失败类别', dataIndex: 'category', key: 'category', width: 220 },
  { title: '次数', dataIndex: 'count', key: 'count', width: 120 }
]

const errorCategoryRows = computed(() => {
  return Object.entries(chainHealth.value.error_categories || {})
    .map(([category, count]) => ({ category, count }))
    .sort((a, b) => b.count - a.count)
})

const getReviewEfficiency = async () => {
  try {
    const [startDate, endDate] = dateRange.value
    const data = await getReviewEfficiencyApi(
      startDate.format('YYYY-MM-DD HH:mm:ss'),
      endDate.format('YYYY-MM-DD HH:mm:ss')
    )
    if (data) reviewEfficiency.value = data
  } catch (error) {
    message.error('获取审核效率数据失败')
    console.error(error)
  }
}

const getOverrideRate = async () => {
  try {
    const [startDate, endDate] = dateRange.value
    const data = await getOverrideRateApi(
      startDate.format('YYYY-MM-DD HH:mm:ss'),
      endDate.format('YYYY-MM-DD HH:mm:ss')
    )
    if (data) overrideRate.value = data
  } catch (error) {
    message.error('获取 Override 率数据失败')
    console.error(error)
  }
}

const getPromptComparison = async () => {
  try {
    const [startDate, endDate] = dateRange.value
    const versions = await getPromptComparisonApi(
      startDate.format('YYYY-MM-DD HH:mm:ss'),
      endDate.format('YYYY-MM-DD HH:mm:ss')
    )

    promptVersions.value = []
    await nextTick()
    promptVersions.value = versions
    await nextTick()
  } catch (error) {
    message.error('获取 Prompt 对比数据失败')
    console.error('Error fetching prompt comparison:', error)
  }
}

const getChainHealth = async () => {
  try {
    const data = await getChainHealthApi(200)
    if (data) {
      chainHealth.value = data
    }
  } catch (error) {
    message.error('获取链路健康指标失败')
    console.error(error)
  }
}

const loadEcharts = async () => {
  if (!echartsLib) {
    const module = await import('@/utils/echarts')
    echartsLib = module.echarts
  }
  return echartsLib
}

const getChart = async (key: string, element: HTMLElement | null) => {
  if (!element) {
    console.warn(`${key} element not found`)
    return
  }

  const echarts = await loadEcharts()
  const existing = charts.get(key)
  if (existing) return existing

  const chart = echarts.init(element)
  chart.resize()
  charts.set(key, chart)
  return chart
}

const renderReviewEfficiencyChart = async () => {
  const chart = await getChart('reviewEfficiencyChart', reviewEfficiencyChartRef.value)
  if (!chart) return

  chart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['最小', '平均', '最大'] },
    yAxis: { type: 'value' },
    series: [
      {
        data: [
          reviewEfficiency.value.minTime,
          reviewEfficiency.value.averageReviewTime,
          reviewEfficiency.value.maxTime
        ],
        type: 'bar',
        itemStyle: { color: '#1890ff' }
      }
    ]
  })
}

const renderOverrideRateChart = async () => {
  const chart = await getChart('overrideRateChart', overrideRateChartRef.value)
  if (!chart) return

  chart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['Override', '正常'] },
    yAxis: { type: 'value' },
    series: [
      {
        data: [
          overrideRate.value.overrideCount,
          overrideRate.value.totalDecisions - overrideRate.value.overrideCount
        ],
        type: 'bar',
        itemStyle: { color: ['#f5222d', '#52c41a'] }
      }
    ]
  })
}

const renderPromptComparisonChart = async () => {
  if (!promptVersions.value.length) return

  const chart = await getChart('promptComparisonChart', promptComparisonChartRef.value)
  if (!chart) return

  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['批准率'] },
    xAxis: { type: 'category', data: promptVersions.value.map((v) => v.version) },
    yAxis: { type: 'value', max: 100 },
    series: [
      {
        name: '批准率',
        data: promptVersions.value.map((v) => parseFloat((v.approvalRate * 100).toFixed(1))),
        type: 'line',
        smooth: true,
        itemStyle: { color: '#52c41a' }
      }
    ]
  })
}

const renderOverrideByVersionChart = async () => {
  if (!promptVersions.value.length) return

  const chart = await getChart('overrideByVersionChart', overrideByVersionChartRef.value)
  if (!chart) return

  chart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: promptVersions.value.map((v) => v.version) },
    yAxis: { type: 'value', max: 100 },
    series: [
      {
        name: 'Override 率',
        data: promptVersions.value.map((v) => parseFloat((v.overrideRate * 100).toFixed(1))),
        type: 'bar',
        itemStyle: {
          color: (params: { value: number | string }) => {
            const rate = parseFloat(String(params.value))
            if (rate < 10) return '#52c41a'
            if (rate < 20) return '#faad14'
            return '#f5222d'
          }
        }
      }
    ]
  })
}

const refreshData = async () => {
  loading.value = true
  try {
    await Promise.all([
      getReviewEfficiency(),
      getOverrideRate(),
      getPromptComparison(),
      getChainHealth()
    ])
  } finally {
    loading.value = false
  }

  // ant-card with loading=true does not render body content.
  // Render charts only after loading is false and DOM nodes exist.
  await nextTick()
  await renderReviewEfficiencyChart()
  await renderOverrideRateChart()
  await renderPromptComparisonChart()
  await renderOverrideByVersionChart()
  handleWindowResize()
}

const onDateRangeChange = () => {
  refreshData()
}

onMounted(() => {
  refreshData()
  window.addEventListener('resize', handleWindowResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleWindowResize)
  charts.forEach((chart) => chart.dispose())
  charts.clear()
})
</script>

<style scoped>
.analytics-container {
  padding: 24px;
}
</style>
