<template>
  <div class="user-management">
    <a-card title="用户管理">
      <template #extra>
        <a-space>
          <a-select
            v-model:value="roleFilter"
            style="width: 140px"
            @change="handleFilterChange"
          >
            <a-select-option value="ALL">
              全部角色
            </a-select-option>
            <a-select-option value="ADMIN">
              管理员
            </a-select-option>
            <a-select-option value="REVIEWER">
              审核员
            </a-select-option>
            <a-select-option value="ANALYST">
              分析员
            </a-select-option>
          </a-select>
          <a-button @click="reload">
            刷新
          </a-button>
          <a-button
            type="primary"
            @click="openCreateModal"
          >
            新增用户
          </a-button>
        </a-space>
      </template>

      <a-table
        :loading="loading"
        :columns="columns"
        :data-source="users"
        :pagination="tablePagination"
        row-key="id"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'role'">
            <a-tag :color="getRoleColor(record.role)">
              {{ record.role }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'status'">
            <a-tag :color="getStatusColor(record.status)">
              {{ getUserStatusLabel(record.status) }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'lastLoginAt'">
            {{ formatDate(record.lastLoginAt) }}
          </template>
          <template v-else-if="column.key === 'createdAt'">
            {{ formatDate(record.createdAt) }}
          </template>
          <template v-else-if="column.key === 'actions'">
            <a-space>
              <a-button
                type="link"
                size="small"
                @click="openEditModal(record)"
              >
                编辑
              </a-button>
              <a-popconfirm
                title="确认停用该用户？"
                ok-text="确认"
                cancel-text="取消"
                @confirm="handleDeactivate(record.id)"
              >
                <a-button
                  type="link"
                  size="small"
                  :disabled="record.status !== 'ACTIVE'"
                >
                  停用
                </a-button>
              </a-popconfirm>
              <a-popconfirm
                title="确认删除该用户？"
                ok-text="确认"
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
      v-model:visible="showModal"
      :title="editingUser ? '编辑用户' : '新增用户'"
      :confirm-loading="submitting"
      @ok="handleSubmit"
      @cancel="closeModal"
    >
      <a-form
        :model="formData"
        layout="vertical"
      >
        <template v-if="!editingUser">
          <a-form-item
            label="用户名"
            required
          >
            <a-input v-model:value="formData.username" />
          </a-form-item>
          <a-form-item
            label="邮箱"
            required
          >
            <a-input v-model:value="formData.email" />
          </a-form-item>
          <a-form-item
            label="密码"
            required
          >
            <a-input-password v-model:value="formData.password" />
          </a-form-item>
        </template>

        <a-form-item
          label="姓名"
          required
        >
          <a-input v-model:value="formData.fullName" />
        </a-form-item>

        <a-form-item
          label="角色"
          required
        >
          <a-select v-model:value="formData.role">
            <a-select-option value="ADMIN">
              管理员
            </a-select-option>
            <a-select-option value="REVIEWER">
              审核员
            </a-select-option>
            <a-select-option value="ANALYST">
              分析员
            </a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="部门">
          <a-input v-model:value="formData.department" />
        </a-form-item>

        <a-form-item
          v-if="editingUser"
          label="状态"
        >
          <a-select v-model:value="formData.status">
            <a-select-option value="ACTIVE">
              启用
            </a-select-option>
            <a-select-option value="INACTIVE">
              停用
            </a-select-option>
            <a-select-option value="LOCKED">
              锁定
            </a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { message } from 'ant-design-vue'
import userApi from '@/api/userApi'
import type { User, CreateUserRequest, UpdateUserRequest } from '@/types/user'

type RoleFilter = 'ALL' | 'ADMIN' | 'REVIEWER' | 'ANALYST'

interface UserFormData {
  username: string
  email: string
  password: string
  fullName: string
  role: 'ADMIN' | 'REVIEWER' | 'ANALYST'
  department: string
  status: 'ACTIVE' | 'INACTIVE' | 'LOCKED'
}

const createInitialFormData = (): UserFormData => ({
  username: '',
  email: '',
  password: '',
  fullName: '',
  role: 'ANALYST',
  department: '',
  status: 'ACTIVE'
})

const users = ref<User[]>([])
const loading = ref(false)
const submitting = ref(false)
const showModal = ref(false)
const editingUser = ref<User | null>(null)
const roleFilter = ref<RoleFilter>('ALL')
const formData = ref<UserFormData>(createInitialFormData())
const pagination = ref({ page: 0, size: 20, total: 0 })

const columns: any[] = [
  { title: '用户名', dataIndex: 'username', key: 'username' },
  { title: '姓名', dataIndex: 'fullName', key: 'fullName' },
  { title: '邮箱', dataIndex: 'email', key: 'email' },
  { title: '角色', dataIndex: 'role', key: 'role', width: 120 },
  { title: '状态', dataIndex: 'status', key: 'status', width: 120 },
  { title: '部门', dataIndex: 'department', key: 'department' },
  { title: '上次登录', dataIndex: 'lastLoginAt', key: 'lastLoginAt', width: 180 },
  { title: '创建时间', dataIndex: 'createdAt', key: 'createdAt', width: 180 },
  { title: '操作', key: 'actions', fixed: 'right', width: 220 }
]

const tablePagination = computed(() => ({
  current: pagination.value.page + 1,
  pageSize: pagination.value.size,
  total: pagination.value.total,
  showSizeChanger: true,
  showQuickJumper: true
}))

const getRoleColor = (role: User['role']) => {
  if (role === 'ADMIN') return 'red'
  if (role === 'REVIEWER') return 'blue'
  return 'green'
}

const getStatusColor = (status: User['status']) => {
  if (status === 'ACTIVE') return 'green'
  if (status === 'INACTIVE') return 'orange'
  return 'red'
}

const getUserStatusLabel = (status: User['status']) => {
  if (status === 'ACTIVE') return '启用'
  if (status === 'INACTIVE') return '停用'
  if (status === 'LOCKED') return '锁定'
  return status
}

const formatDate = (date?: string | null) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

const loadUsers = async (page = pagination.value.page, size = pagination.value.size) => {
  loading.value = true
  try {
    const response = roleFilter.value === 'ALL'
      ? await userApi.list(page, size)
      : await userApi.listByRole(roleFilter.value, page, size)

    if (response.status === 'success') {
      users.value = response.data ?? []
      pagination.value = {
        page: response.page ?? page,
        size: response.size ?? size,
        total: response.total ?? 0
      }
    }
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : '加载用户失败'
    message.error(msg)
  } finally {
    loading.value = false
  }
}

const handleTableChange = (pager: { current?: number; pageSize?: number }) => {
  const nextPage = (pager.current ?? 1) - 1
  const nextSize = pager.pageSize ?? pagination.value.size
  loadUsers(nextPage, nextSize)
}

const handleFilterChange = () => {
  loadUsers(0, pagination.value.size)
}

const reload = () => {
  loadUsers()
}

const openCreateModal = () => {
  editingUser.value = null
  formData.value = createInitialFormData()
  showModal.value = true
}

const openEditModal = (user: Record<string, unknown>) => {
  const typedUser = user as unknown as User
  editingUser.value = typedUser
  formData.value = {
    username: typedUser.username,
    email: typedUser.email,
    password: '',
    fullName: typedUser.fullName,
    role: typedUser.role,
    department: typedUser.department ?? '',
    status: typedUser.status
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingUser.value = null
  formData.value = createInitialFormData()
}

const handleSubmit = async () => {
  try {
    submitting.value = true
    if (!formData.value.fullName || !formData.value.role) {
      message.error('请填写完整信息')
      return
    }

    if (editingUser.value) {
      const payload: UpdateUserRequest = {
        fullName: formData.value.fullName,
        role: formData.value.role,
        department: formData.value.department,
        status: formData.value.status
      }
      const response = await userApi.update(editingUser.value.id, payload)
      if (response.status === 'success') {
        message.success('用户更新成功')
      }
    } else {
      if (!formData.value.username || !formData.value.email || !formData.value.password) {
        message.error('请填写完整信息')
        return
      }
      if (formData.value.password.length < 6) {
        message.error('密码至少 6 位')
        return
      }

      const payload: CreateUserRequest = {
        username: formData.value.username,
        email: formData.value.email,
        password: formData.value.password,
        fullName: formData.value.fullName,
        role: formData.value.role,
        department: formData.value.department
      }
      const response = await userApi.create(payload)
      if (response.status === 'success') {
        message.success('用户创建成功')
      }
    }

    closeModal()
    await loadUsers()
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : '操作失败'
    message.error(msg)
  } finally {
    submitting.value = false
  }
}

const handleDeactivate = async (id: number) => {
  try {
    const response = await userApi.deactivate(id)
    if (response.status === 'success') {
      message.success('用户已停用')
      await loadUsers()
    }
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : '停用失败'
    message.error(msg)
  }
}

const handleDelete = async (id: number) => {
  try {
    const response = await userApi.delete(id)
    if (response.status === 'success') {
      message.success('用户删除成功')
      await loadUsers()
    }
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : '删除失败'
    message.error(msg)
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.user-management {
  padding: 24px;
}
</style>
