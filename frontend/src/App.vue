<template>
  <div id="app">
    <router-view v-if="isLoginPage" />

    <a-layout
      v-else
      style="min-height: 100vh"
    >
      <a-layout-header class="header">
        <div class="logo">
          <h1>风控决策增强平台</h1>
        </div>
        <div class="user-menu">
          <a-dropdown>
            <template #overlay>
              <a-menu>
                <a-menu-item key="logout">
                  <a @click="logout">退出登录</a>
                </a-menu-item>
              </a-menu>
            </template>
            <a-button type="text">
              {{ currentUser }}
            </a-button>
          </a-dropdown>
        </div>
      </a-layout-header>

      <a-layout>
        <a-layout-sider
          width="220"
          theme="light"
        >
          <a-menu
            v-model:selected-keys="selectedKeys"
            mode="inline"
          >
            <a-menu-item key="/">
              <router-link to="/">
                仪表板
              </router-link>
            </a-menu-item>
            <a-menu-item key="/cases">
              <router-link to="/cases">
                案件管理
              </router-link>
            </a-menu-item>
            <a-menu-item key="/prompts">
              <router-link to="/prompts">
                Prompt 管理
              </router-link>
            </a-menu-item>
            <a-menu-item key="/analytics">
              <router-link to="/analytics">
                数据分析
              </router-link>
            </a-menu-item>
            <a-menu-item
              v-if="isAdmin"
              key="/users"
            >
              <router-link to="/users">
                用户管理
              </router-link>
            </a-menu-item>
          </a-menu>
        </a-layout-sider>

        <a-layout-content style="padding: 24px">
          <router-view />
        </a-layout-content>
      </a-layout>

      <a-layout-footer style="text-align: center">
        风控决策增强平台 ©2024 Created by Risk Control Team
      </a-layout-footer>
    </a-layout>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const router = useRouter()
const route = useRoute()

const currentUser = ref(localStorage.getItem('user') || 'Admin')
const isAdmin = computed(() => true)
const isLoginPage = computed(() => route.path === '/login')
const selectedKeys = ref<string[]>(['/'])

watch(
  () => route.path,
  (path) => {
    if (path.startsWith('/cases')) {
      selectedKeys.value = ['/cases']
      return
    }
    const topLevel = ['/', '/prompts', '/analytics', '/users']
    selectedKeys.value = [topLevel.includes(path) ? path : '/']
  },
  { immediate: true }
)

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/login')
}
</script>

<style scoped>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.header {
  background: #fff;
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.logo h1 {
  margin: 0;
  color: #1890ff;
  font-size: 20px;
}

.user-menu {
  display: flex;
  align-items: center;
}
</style>
