<template>
  <div class="login-container">
    <a-card
      class="login-card"
      title="风控决策增强平台"
    >
      <a-form
        :model="formData"
        layout="vertical"
        @finish="handleLogin"
      >
        <a-form-item
          label="用户名"
          name="username"
          :rules="[{ required: true, message: '请输入用户名' }]"
        >
          <a-input
            v-model:value="formData.username"
            placeholder="输入用户名"
          />
        </a-form-item>
        <a-form-item
          label="密码"
          name="password"
          :rules="[{ required: true, message: '请输入密码' }]"
        >
          <a-input-password
            v-model:value="formData.password"
            placeholder="输入密码"
          />
        </a-form-item>
        <a-form-item>
          <a-button
            type="primary"
            html-type="submit"
            block
            :loading="loading"
          >
            登录
          </a-button>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import axios from 'axios'

const router = useRouter()
const loading = ref(false)
const formData = ref({
  username: '',
  password: ''
})

const handleLogin = async () => {
  if (!formData.value.username || !formData.value.password) {
    message.error('请输入用户名和密码')
    return
  }

  loading.value = true
  try {
    // Call backend login API
    const response = await axios.post('/api/auth/login', {
      username: formData.value.username,
      password: formData.value.password
    }, {
      timeout: 10000
    })

    if (response.data.status === 'success') {
      // Save token and user info
      localStorage.setItem('token', response.data.data.token)
      localStorage.setItem('user', response.data.data.username)
      message.success('登录成功')
      router.push('/')
    } else {
      message.error(response.data.message || '登录失败')
    }
  } catch (error: any) {
    console.error('Login error:', error)
    message.error(error.response?.data?.message || '登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 100%;
  max-width: 400px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}
</style>
