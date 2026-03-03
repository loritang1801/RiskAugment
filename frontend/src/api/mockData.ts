// Mock data for demonstration purposes

export const mockCases = [
  {
    id: 1,
    bizTransactionId: 'TXN001',
    amount: 5000,
    currency: 'USD',
    country: 'US',
    deviceRisk: 'LOW',
    userLabel: 'existing_user',
    riskLevel: 'LOW',
    riskStatus: 'PENDING',
    riskScore: 0.25,
    createdAt: new Date().toISOString()
  },
  {
    id: 2,
    bizTransactionId: 'TXN002',
    amount: 15000,
    currency: 'USD',
    country: 'CN',
    deviceRisk: 'MEDIUM',
    userLabel: 'new_user',
    riskLevel: 'MEDIUM',
    riskStatus: 'ANALYZING',
    riskScore: 0.55,
    createdAt: new Date().toISOString()
  },
  {
    id: 3,
    bizTransactionId: 'TXN003',
    amount: 50000,
    currency: 'USD',
    country: 'RU',
    deviceRisk: 'HIGH',
    userLabel: 'vip_user',
    riskLevel: 'HIGH',
    riskStatus: 'PENDING',
    riskScore: 0.85,
    createdAt: new Date().toISOString()
  },
  {
    id: 4,
    bizTransactionId: 'TXN004',
    amount: 3000,
    currency: 'EUR',
    country: 'DE',
    deviceRisk: 'LOW',
    userLabel: 'existing_user',
    riskLevel: 'LOW',
    riskStatus: 'APPROVED',
    riskScore: 0.15,
    createdAt: new Date().toISOString()
  },
  {
    id: 5,
    bizTransactionId: 'TXN005',
    amount: 25000,
    currency: 'GBP',
    country: 'GB',
    deviceRisk: 'MEDIUM',
    userLabel: 'new_user',
    riskLevel: 'MEDIUM',
    riskStatus: 'REJECTED',
    riskScore: 0.65,
    createdAt: new Date().toISOString()
  },
  {
    id: 6,
    bizTransactionId: 'TXN006',
    amount: 8000,
    currency: 'USD',
    country: 'JP',
    deviceRisk: 'LOW',
    userLabel: 'existing_user',
    riskLevel: 'LOW',
    riskStatus: 'PENDING',
    riskScore: 0.30,
    createdAt: new Date().toISOString()
  },
  {
    id: 7,
    bizTransactionId: 'TXN007',
    amount: 45000,
    currency: 'USD',
    country: 'IN',
    deviceRisk: 'HIGH',
    userLabel: 'new_user',
    riskLevel: 'HIGH',
    riskStatus: 'ANALYZING',
    riskScore: 0.80,
    createdAt: new Date().toISOString()
  },
  {
    id: 8,
    bizTransactionId: 'TXN008',
    amount: 12000,
    currency: 'EUR',
    country: 'FR',
    deviceRisk: 'MEDIUM',
    userLabel: 'existing_user',
    riskLevel: 'MEDIUM',
    riskStatus: 'PENDING',
    riskScore: 0.50,
    createdAt: new Date().toISOString()
  },
  {
    id: 9,
    bizTransactionId: 'TXN009',
    amount: 60000,
    currency: 'USD',
    country: 'BR',
    deviceRisk: 'HIGH',
    userLabel: 'vip_user',
    riskLevel: 'HIGH',
    riskStatus: 'PENDING',
    riskScore: 0.90,
    createdAt: new Date().toISOString()
  },
  {
    id: 10,
    bizTransactionId: 'TXN010',
    amount: 2000,
    currency: 'USD',
    country: 'CA',
    deviceRisk: 'LOW',
    userLabel: 'new_user',
    riskLevel: 'LOW',
    riskStatus: 'APPROVED',
    riskScore: 0.20,
    createdAt: new Date().toISOString()
  }
]

export const mockAIDecisions = [
  { id: 1, caseId: 1, promptVersion: 'v1', suggestedAction: 'APPROVE', aiConfidence: 0.92, totalTimeMs: 1250 },
  { id: 2, caseId: 2, promptVersion: 'v1', suggestedAction: 'REVIEW', aiConfidence: 0.78, totalTimeMs: 1450 },
  { id: 3, caseId: 3, promptVersion: 'v1', suggestedAction: 'REJECT', aiConfidence: 0.88, totalTimeMs: 1380 },
  { id: 4, caseId: 4, promptVersion: 'v1', suggestedAction: 'APPROVE', aiConfidence: 0.95, totalTimeMs: 1100 },
  { id: 5, caseId: 5, promptVersion: 'v1', suggestedAction: 'REJECT', aiConfidence: 0.85, totalTimeMs: 1320 },
  { id: 6, caseId: 6, promptVersion: 'v1', suggestedAction: 'APPROVE', aiConfidence: 0.90, totalTimeMs: 1200 },
  { id: 7, caseId: 7, promptVersion: 'v1', suggestedAction: 'REJECT', aiConfidence: 0.82, totalTimeMs: 1400 },
  { id: 8, caseId: 8, promptVersion: 'v1', suggestedAction: 'REVIEW', aiConfidence: 0.75, totalTimeMs: 1350 },
  { id: 9, caseId: 9, promptVersion: 'v1', suggestedAction: 'REJECT', aiConfidence: 0.91, totalTimeMs: 1280 },
  { id: 10, caseId: 10, promptVersion: 'v1', suggestedAction: 'APPROVE', aiConfidence: 0.93, totalTimeMs: 1150 }
]

export const mockPrompts = [
  {
    id: 1,
    version: 'v1',
    systemPrompt: 'You are a risk analysis expert specializing in financial fraud detection.',
    userPromptTemplate: 'Analyze the following transaction case...',
    description: 'Initial version - Basic risk analysis',
    isActive: true,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: 2,
    version: 'v2',
    systemPrompt: 'You are an advanced risk analysis expert with deep knowledge of fraud patterns.',
    userPromptTemplate: 'Analyze the following transaction case with enhanced risk dimensions...',
    description: 'Enhanced version - Improved accuracy',
    isActive: false,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  }
]

export const mockAnalytics = {
  reviewEfficiency: {
    avgReviewTime: 1250,
    totalReviewed: 10,
    trend: [
      { date: '2026-02-20', avgTime: 1300 },
      { date: '2026-02-21', avgTime: 1280 },
      { date: '2026-02-22', avgTime: 1250 },
      { date: '2026-02-23', avgTime: 1200 },
      { date: '2026-02-24', avgTime: 1180 },
      { date: '2026-02-25', avgTime: 1150 },
      { date: '2026-02-26', avgTime: 1120 }
    ]
  },
  overrideRate: {
    rate: 0.15,
    total: 10,
    overridden: 2,
    byVersion: [
      { version: 'v1', rate: 0.15, total: 10, overridden: 2 },
      { version: 'v2', rate: 0.10, total: 5, overridden: 1 }
    ]
  }
}

export const mockAuditTrail = [
  {
    id: 1,
    caseId: 1,
    operation: 'CREATE',
    operatorId: 1,
    operatorName: 'admin',
    createdAt: new Date().toISOString()
  },
  {
    id: 2,
    caseId: 1,
    operation: 'ANALYZE',
    operatorId: 1,
    operatorName: 'admin',
    createdAt: new Date().toISOString()
  }
]
