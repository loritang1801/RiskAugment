export interface User {
  id: number
  username: string
  email: string
  fullName: string
  role: 'ADMIN' | 'REVIEWER' | 'ANALYST'
  department?: string | null
  status: 'ACTIVE' | 'INACTIVE' | 'LOCKED'
  lastLoginAt?: string | null
  createdAt: string
  updatedAt: string
}

export interface CreateUserRequest {
  username: string
  email: string
  password: string
  fullName: string
  role: 'ADMIN' | 'REVIEWER' | 'ANALYST'
  department?: string
}

export interface UpdateUserRequest {
  fullName: string
  role: 'ADMIN' | 'REVIEWER' | 'ANALYST'
  department?: string
  status?: 'ACTIVE' | 'INACTIVE' | 'LOCKED'
}
