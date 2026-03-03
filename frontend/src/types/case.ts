export interface RiskFeatures {
  [key: string]: unknown
}

export interface RiskCase {
  id: number
  bizTransactionId: string
  amount: number
  currency: string
  country: string
  deviceRisk: string
  userLabel: string
  riskFeatures?: RiskFeatures | string | null
  ruleEngineScore?: number
  triggeredRules?: Record<string, unknown> | null
  riskScore?: number
  riskLevel: string
  riskStatus: string
  aiDecisionId?: number | null
  finalDecision?: string | null
  reviewerId?: number | null
  reviewerName?: string | null
  createdAt: string
  updatedAt: string
}

export interface RiskCasePayload {
  bizTransactionId: string
  amount: number | string
  currency: string
  country?: string
  deviceRisk?: string
  userLabel?: string
  riskLevel?: string
  riskStatus?: string
  riskFeatures?: Record<string, unknown>
  ruleEngineScore?: number | string
  triggeredRules?: Record<string, unknown>
  riskScore?: number | string
}
