<template>
  <div class="case-list">
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
            案件管理
          </h2>
        </a-col>
        <a-col
          :xs="24"
          :sm="12"
          style="text-align: right"
        >
          <a-space>
            <a-button @click="toggleAdvancedFilter">
              {{ showAdvancedFilter ? '隐藏' : '显示' }}高级筛选
            </a-button>
            <a-button
              type="primary"
              @click="showCreateModal = true"
            >
              + 新增案件
            </a-button>
          </a-space>
        </a-col>
      </a-row>
    </a-card>

    <a-card
      v-if="showAdvancedFilter"
      class="advanced-filter-card"
      :bordered="false"
      style="margin-bottom: 16px"
    >
      <a-row :gutter="[16, 16]">
        <a-col
          :xs="24"
          :sm="12"
          :md="6"
        >
          <div class="filter-label">
            交易ID
          </div>
          <a-input-search
            v-model:value="filters.bizTransactionId"
            placeholder="搜索交易ID"
            @search="handleFilterChange"
          />
        </a-col>
        <a-col
          :xs="24"
          :sm="12"
          :md="6"
        >
          <div class="filter-label">
            案件状态
          </div>
          <a-select
            v-model:value="filters.status"
            placeholder="选择状态"
            allow-clear
            @change="handleFilterChange"
          >
            <a-select-option value="PENDING">
              待审核
            </a-select-option>
            <a-select-option value="ANALYZING">
              分析中
            </a-select-option>
            <a-select-option value="APPROVED">
              已批准
            </a-select-option>
            <a-select-option value="REJECTED">
              已拒绝
            </a-select-option>
          </a-select>
        </a-col>
        <a-col
          :xs="24"
          :sm="12"
          :md="6"
        >
          <div class="filter-label">
            风险等级
          </div>
          <a-select
            v-model:value="filters.riskLevel"
            placeholder="选择风险等级"
            allow-clear
            @change="handleFilterChange"
          >
            <a-select-option value="LOW">
              低
            </a-select-option>
            <a-select-option value="MEDIUM">
              中
            </a-select-option>
            <a-select-option value="HIGH">
              高
            </a-select-option>
          </a-select>
        </a-col>
        <a-col
          :xs="24"
          :sm="12"
          :md="6"
        >
          <div class="filter-label">
            国家
          </div>
          <a-input
            v-model:value="filters.country"
            placeholder="输入国家代码"
            @change="handleFilterChange"
          />
        </a-col>
      </a-row>
      <a-row
        :gutter="[16, 16]"
        style="margin-top: 12px"
      >
        <a-col :xs="24">
          <a-button @click="resetFilters">
            重置筛选
          </a-button>
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
          title="总案件数"
          :value="caseStore.pagination.total"
          :value-style="{ color: '#1890ff' }"
        />
      </a-col>
      <a-col
        :xs="24"
        :sm="12"
        :md="6"
      >
        <a-statistic
          title="待审核"
          :value="pendingCount"
          :value-style="{ color: '#faad14' }"
        />
      </a-col>
      <a-col
        :xs="24"
        :sm="12"
        :md="6"
      >
        <a-statistic
          title="已批准"
          :value="approvedCount"
          :value-style="{ color: '#52c41a' }"
        />
      </a-col>
      <a-col
        :xs="24"
        :sm="12"
        :md="6"
      >
        <a-statistic
          title="已拒绝"
          :value="rejectedCount"
          :value-style="{ color: '#f5222d' }"
        />
      </a-col>
    </a-row>

    <a-card :bordered="false">
      <a-table
        :columns="columns"
        :data-source="cases"
        :loading="loading"
        :pagination="tablePagination"
        row-key="id"
        size="middle"
        :scroll="{ x: 1200 }"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'amount'">
            {{ record.amount }} {{ record.currency }}
          </template>
          <template v-else-if="column.key === 'riskLevel'">
            <a-tag :color="getRiskLevelColor(record.riskLevel)">
              {{ getRiskLevelLabel(record.riskLevel) }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'riskStatus'">
            <a-tag :color="getStatusColor(record.riskStatus)">
              {{ getStatusLabel(record.riskStatus) }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'createdAt'">
            {{ formatDate(record.createdAt) }}
          </template>
          <template v-else-if="column.key === 'action'">
            <a-space size="small">
              <router-link :to="`/cases/${record.id}`">
                <a-button
                  type="link"
                  size="small"
                >
                  查看
                </a-button>
              </router-link>
              <a-button
                type="link"
                size="small"
                @click="handleEdit(record)"
              >
                编辑
              </a-button>
              <a-popconfirm
                title="确定删除此案件？"
                ok-text="确定"
                cancel-text="取消"
                @confirm="handleDelete(record.id)"
              >
                <a-button
                  type="link"
                  danger
                  size="small"
                >
                  删除
                </a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <a-modal
      v-model:visible="showCreateModal"
      :title="editingCase ? '编辑案件' : '新增案件'"
      width="600px"
      @ok="handleCreateOk"
      @cancel="resetForm"
    >
      <a-form
        :model="formData"
        layout="vertical"
        :label-col="{ span: 24 }"
      >
        <a-form-item
          label="交易ID"
          required
        >
          <a-input
            v-model:value="formData.bizTransactionId"
            placeholder="输入交易ID"
            :disabled="!!editingCase"
          />
        </a-form-item>
        <a-form-item
          label="金额"
          required
        >
          <a-input-number
            v-model:value="formData.amount"
            placeholder="输入金额"
            :min="0"
            :precision="2"
            style="width: 100%"
          />
        </a-form-item>
        <a-form-item
          label="币种"
          required
        >
          <a-select
            v-model:value="formData.currency"
            placeholder="选择币种"
          >
            <a-select-option value="USD">
              USD
            </a-select-option>
            <a-select-option value="EUR">
              EUR
            </a-select-option>
            <a-select-option value="CNY">
              CNY
            </a-select-option>
            <a-select-option value="GBP">
              GBP
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="国家">
          <a-input
            v-model:value="formData.country"
            placeholder="输入国家代码"
          />
        </a-form-item>
        <a-form-item label="设备风险">
          <a-select
            v-model:value="formData.deviceRisk"
            placeholder="选择设备风险"
          >
            <a-select-option value="LOW">
              低
            </a-select-option>
            <a-select-option value="MEDIUM">
              中
            </a-select-option>
            <a-select-option value="HIGH">
              高
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="用户标签">
          <a-select
            v-model:value="formData.userLabel"
            placeholder="选择用户标签"
          >
            <a-select-option value="new_user">
              新用户
            </a-select-option>
            <a-select-option value="existing_user">
              老用户
            </a-select-option>
            <a-select-option value="vip_user">
              VIP用户
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="风险等级">
          <a-select
            v-model:value="formData.riskLevel"
            placeholder="选择风险等级"
          >
            <a-select-option value="LOW">
              低
            </a-select-option>
            <a-select-option value="MEDIUM">
              中
            </a-select-option>
            <a-select-option value="HIGH">
              高
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="设备指纹">
          <a-input
            v-model:value="formData.riskFeatures.device_fingerprint"
            placeholder="输入设备指纹"
          />
        </a-form-item>
        <a-form-item label="IP地址">
          <a-input
            v-model:value="formData.riskFeatures.ip_address"
            placeholder="输入IP地址"
          />
        </a-form-item>
        <a-form-item label="用户行为评分">
          <a-input-number
            v-model:value="formData.riskFeatures.user_behavior_score"
            placeholder="输入用户行为评分"
            :min="0"
            :max="100"
            style="width: 100%"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { useCaseStore } from '@/stores/case'
import type { RiskCase } from '@/types/case'

const caseStore = useCaseStore()
const showCreateModal = ref(false)
const showAdvancedFilter = ref(false)
const editingCase = ref<RiskCase | null>(null)

interface CaseFormData {
  bizTransactionId: string
  amount: number
  currency: string
  country: string
  deviceRisk: string
  userLabel: string
  riskLevel: string
  riskStatus: string
  riskFeatures: {
    device_fingerprint: string
    ip_address: string
    user_behavior_score: number
  }
  ruleEngineScore: number
  triggeredRules: Record<string, unknown>
  riskScore: number
}

const createInitialFormData = (): CaseFormData => ({
  bizTransactionId: '',
  amount: 0,
  currency: 'USD',
  country: '',
  deviceRisk: 'LOW',
  userLabel: 'existing_user',
  riskLevel: 'LOW',
  riskStatus: 'PENDING',
  riskFeatures: {
    device_fingerprint: '',
    ip_address: '',
    user_behavior_score: 0
  },
  ruleEngineScore: 0,
  triggeredRules: {},
  riskScore: 0
})

const filters = ref({
  bizTransactionId: '',
  status: '',
  riskLevel: '',
  country: ''
})

const formData = ref<CaseFormData>(createInitialFormData())

const columns: any[] = [
  { title: '交易ID', dataIndex: 'bizTransactionId', key: 'bizTransactionId', width: 140, ellipsis: true },
  { title: '金额', dataIndex: 'amount', key: 'amount', width: 120, align: 'right' },
  { title: '国家', dataIndex: 'country', key: 'country', width: 80 },
  { title: '风险等级', dataIndex: 'riskLevel', key: 'riskLevel', width: 100 },
  { title: '状态', dataIndex: 'riskStatus', key: 'riskStatus', width: 100 },
  { title: '创建时间', dataIndex: 'createdAt', key: 'createdAt', width: 160 },
  { title: '操作', key: 'action', width: 150, fixed: 'right' }
]

const cases = computed(() => caseStore.cases)
const loading = computed(() => caseStore.loading)

const tablePagination = computed(() => ({
  current: caseStore.pagination.page + 1,
  pageSize: caseStore.pagination.size,
  total: caseStore.pagination.total,
  showSizeChanger: true,
  showQuickJumper: true,
  pageSizeOptions: ['10', '20', '50', '100']
}))

const pendingCount = computed(() => cases.value.filter(c => c.riskStatus === 'PENDING').length)
const approvedCount = computed(() => cases.value.filter(c => c.riskStatus === 'APPROVED').length)
const rejectedCount = computed(() => cases.value.filter(c => c.riskStatus === 'REJECTED').length)

const getRiskLevelColor = (level: string) => {
  const colors: Record<string, string> = { LOW: 'green', MEDIUM: 'orange', HIGH: 'red' }
  return colors[level] || 'default'
}

const getRiskLevelLabel = (level: string) => {
  const labels: Record<string, string> = { LOW: '低风险', MEDIUM: '中风险', HIGH: '高风险' }
  return labels[level] || level || '-'
}

const getStatusColor = (status: string) => {
  const colors: Record<string, string> = { PENDING: 'blue', ANALYZING: 'orange', APPROVED: 'green', REJECTED: 'red' }
  return colors[status] || 'default'
}

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    PENDING: '待审核',
    ANALYZING: '分析中',
    APPROVED: '已通过',
    REJECTED: '已拒绝'
  }
  return labels[status] || status || '-'
}

const formatDate = (date: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

const toggleAdvancedFilter = () => {
  showAdvancedFilter.value = !showAdvancedFilter.value
}

const handleFilterChange = () => {
  caseStore.fetchCases(0, caseStore.pagination.size, filters.value)
}

const resetFilters = () => {
  filters.value = { bizTransactionId: '', status: '', riskLevel: '', country: '' }
  caseStore.fetchCases(0, caseStore.pagination.size)
}

const handleTableChange = (pagination: any) => {
  caseStore.fetchCases(pagination.current - 1, pagination.pageSize)
}

const handleEdit = (record: Record<string, unknown>) => {
  const typedRecord = record as unknown as RiskCase
  const recordFeatures = typedRecord.riskFeatures && typeof typedRecord.riskFeatures === 'object'
    ? typedRecord.riskFeatures
    : {}
  editingCase.value = typedRecord
  formData.value = {
    ...createInitialFormData(),
    bizTransactionId: typedRecord.bizTransactionId,
    amount: typedRecord.amount,
    currency: typedRecord.currency,
    country: typedRecord.country,
    deviceRisk: typedRecord.deviceRisk,
    userLabel: typedRecord.userLabel,
    riskLevel: typedRecord.riskLevel,
    riskStatus: typedRecord.riskStatus,
    ruleEngineScore: typedRecord.ruleEngineScore ?? 0,
    triggeredRules: typedRecord.triggeredRules ?? {},
    riskScore: typedRecord.riskScore ?? 0,
    riskFeatures: {
      device_fingerprint: '',
      ip_address: '',
      user_behavior_score: 0,
      ...recordFeatures
    }
  }
  showCreateModal.value = true
}

const handleCreateOk = async () => {
  try {
    if (!formData.value.bizTransactionId || !formData.value.amount || !formData.value.currency) {
      message.error('请填写必填项')
      return
    }

    const submitData = {
      bizTransactionId: formData.value.bizTransactionId,
      amount: formData.value.amount,
      currency: formData.value.currency,
      country: formData.value.country || '',
      deviceRisk: formData.value.deviceRisk || 'LOW',
      userLabel: formData.value.userLabel || 'existing_user',
      riskLevel: formData.value.riskLevel || 'LOW',
      riskStatus: formData.value.riskStatus || 'PENDING',
      riskFeatures: {
        device_fingerprint: formData.value.riskFeatures?.device_fingerprint || '',
        ip_address: formData.value.riskFeatures?.ip_address || '',
        user_behavior_score: formData.value.riskFeatures?.user_behavior_score || 0
      },
      ruleEngineScore: formData.value.ruleEngineScore ?? 0,
      triggeredRules: formData.value.triggeredRules || {},
      riskScore: formData.value.riskScore ?? 0
    }

    if (editingCase.value) {
      await caseStore.updateCase(editingCase.value.id, submitData)
      message.success('更新成功')
    } else {
      await caseStore.createCase(submitData)
      message.success('创建成功')
    }
    resetForm()
    await caseStore.fetchCases()
  } catch (error: any) {
    console.error('Error:', error)
    message.error(error.message || '操作失败')
  }
}

const handleDelete = async (id: number) => {
  try {
    await caseStore.deleteCase(id)
    message.success('删除成功')
    await caseStore.fetchCases()
  } catch (error: any) {
    console.error('Error:', error)
    message.error(error.message || '删除失败')
  }
}

const resetForm = () => {
  showCreateModal.value = false
  editingCase.value = null
  formData.value = createInitialFormData()
}

onMounted(() => {
  caseStore.fetchCases()
})
</script>

<style scoped>
.case-list {
  padding: 24px;
}

.filter-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 8px;
  font-weight: 500;
}

.advanced-filter-card :deep(.ant-select) {
  width: 100%;
}
</style>
