<template>
  <div class="prompt-management">
    <a-card
      title="Prompt 版本管理"
      :bordered="false"
    >
      <template #extra>
        <a-button
          type="primary"
          @click="showCreateModal = true"
        >
          <template #icon>
            <PlusOutlined />
          </template>
          创建新版本
        </a-button>
      </template>

      <a-table
        :columns="columns"
        :data-source="prompts"
        :loading="loading"
        :pagination="false"
        row-key="version"
        bordered
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'version'">
            <a-tag color="blue">
              {{ record.version }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'system_prompt'">
            <span :title="record.system_prompt">
              {{ record.system_prompt && record.system_prompt.length > 50 ? record.system_prompt.substring(0, 50) + '...' : (record.system_prompt || '-') }}
            </span>
          </template>
          <template v-else-if="column.key === 'is_active'">
            <a-tag
              v-if="record.is_active"
              color="green"
            >
              已激活
            </a-tag>
            <a-tag
              v-else
              color="default"
            >
              未激活
            </a-tag>
          </template>
          <template v-else-if="column.key === 'created_at'">
            {{ formatDate(record.created_at) }}
          </template>
          <template v-else-if="column.key === 'action'">
            <a-space>
              <a-button
                type="link"
                size="small"
                @click="openDetailModal(record)"
              >
                查看详情
              </a-button>
              <a-button
                v-if="!record.is_active"
                type="link"
                size="small"
                @click="handleActivate(record.version)"
              >
                激活
              </a-button>
              <a-popconfirm
                v-if="!record.is_active"
                title="确定删除该版本？"
                ok-text="确定"
                cancel-text="取消"
                @confirm="handleDelete(record.version)"
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
      title="创建新 Prompt 版本"
      ok-text="创建"
      cancel-text="取消"
      @ok="handleCreate"
    >
      <a-form
        :model="createForm"
        layout="vertical"
      >
        <a-form-item
          label="版本号"
          required
        >
          <a-input
            v-model:value="createForm.version"
            placeholder="例如：v3"
          />
        </a-form-item>

        <a-form-item
          label="系统提示词"
          required
        >
          <a-textarea
            v-model:value="createForm.system_prompt"
            :rows="4"
            placeholder="请输入系统提示词"
          />
        </a-form-item>

        <a-form-item
          label="用户提示词模板"
          required
        >
          <a-textarea
            v-model:value="createForm.user_prompt_template"
            :rows="6"
            placeholder="请输入用户提示词模板"
          />
        </a-form-item>

        <a-form-item label="描述">
          <a-textarea
            v-model:value="createForm.description"
            :rows="2"
            placeholder="请输入版本描述"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <a-modal
      v-model:visible="showDetailModal"
      title="Prompt 版本详情"
      :footer="null"
      width="800px"
    >
      <a-descriptions
        v-if="selectedPrompt"
        :column="1"
        bordered
      >
        <a-descriptions-item label="版本号">
          <a-tag color="blue">
            {{ selectedPrompt.version }}
          </a-tag>
        </a-descriptions-item>

        <a-descriptions-item label="状态">
          <a-tag
            v-if="selectedPrompt.is_active"
            color="green"
          >
            已激活
          </a-tag>
          <a-tag
            v-else
            color="default"
          >
            未激活
          </a-tag>
        </a-descriptions-item>

        <a-descriptions-item label="描述">
          {{ selectedPrompt.description || '-' }}
        </a-descriptions-item>

        <a-descriptions-item label="系统提示词">
          <div class="prompt-text">
            {{ selectedPrompt.system_prompt }}
          </div>
        </a-descriptions-item>

        <a-descriptions-item label="用户提示词模板">
          <div class="prompt-text">
            {{ selectedPrompt.user_prompt_template }}
          </div>
        </a-descriptions-item>

        <a-descriptions-item label="创建时间">
          {{ formatDate(selectedPrompt.created_at) }}
        </a-descriptions-item>

        <a-descriptions-item label="更新时间">
          {{ formatDate(selectedPrompt.updated_at) }}
        </a-descriptions-item>
      </a-descriptions>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import * as promptApi from '../api/promptApi'

interface Prompt {
  id: number
  version: string
  system_prompt: string
  user_prompt_template: string
  description?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

const prompts = ref<Prompt[]>([])
const loading = ref(false)
const showCreateModal = ref(false)
const showDetailModal = ref(false)
const selectedPrompt = ref<Prompt | null>(null)

const createForm = ref({
  version: '',
  system_prompt: '',
  user_prompt_template: '',
  description: ''
})

const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

const columns: any[] = [
  { title: '版本号', dataIndex: 'version', key: 'version', width: 100 },
  { title: '描述', dataIndex: 'description', key: 'description', width: 200, ellipsis: true },
  { title: '系统提示词预览', dataIndex: 'system_prompt', key: 'system_prompt', width: 250, ellipsis: true },
  { title: '状态', dataIndex: 'is_active', key: 'is_active', width: 100 },
  { title: '创建时间', dataIndex: 'created_at', key: 'created_at', width: 180 },
  { title: '操作', key: 'action', width: 200 }
]

const loadPrompts = async () => {
  loading.value = true
  try {
    const response = await promptApi.getAllPrompts()
    if (response.status === 'success') {
      prompts.value = response.data ?? []
    }
  } catch (error) {
    message.error('加载 Prompt 版本失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleCreate = async () => {
  if (!createForm.value.version || !createForm.value.system_prompt || !createForm.value.user_prompt_template) {
    message.error('请填写必填项')
    return
  }

  try {
    const response = await promptApi.createPrompt(createForm.value)
    if (response.status === 'success') {
      message.success('Prompt 版本创建成功')
      showCreateModal.value = false
      createForm.value = {
        version: '',
        system_prompt: '',
        user_prompt_template: '',
        description: ''
      }
      await loadPrompts()
    }
  } catch (error) {
    message.error('创建 Prompt 版本失败')
    console.error(error)
  }
}

const handleActivate = async (version: string) => {
  try {
    const response = await promptApi.activatePrompt(version)
    if (response.status === 'success') {
      message.success(`Prompt 版本 ${version} 已激活`)
      await loadPrompts()
    }
  } catch (error) {
    message.error('激活 Prompt 版本失败')
    console.error(error)
  }
}

const handleDelete = async (version: string) => {
  try {
    const response = await promptApi.deletePrompt(version)
    if (response.status === 'success') {
      message.success(`Prompt 版本 ${version} 已删除`)
      await loadPrompts()
    }
  } catch (error) {
    message.error('删除 Prompt 版本失败')
    console.error(error)
  }
}

const openDetailModal = (prompt: Record<string, unknown>) => {
  selectedPrompt.value = prompt as unknown as Prompt
  showDetailModal.value = true
}

onMounted(() => {
  loadPrompts()
})
</script>

<style scoped>
.prompt-management {
  padding: 20px;
}

.prompt-text {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 300px;
  overflow-y: auto;
}
</style>
