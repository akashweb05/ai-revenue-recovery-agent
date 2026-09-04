export interface Summary {
  merchant_id: number | null
  overview: {
    total_cases: number
    total_amount_at_risk: number
    recovered_cases: number
    recovered_amount: number
    recovery_rate: number
  }
  case_status: {
    pending: number
    executed: number
    recovered: number
    verification_failed: number
  }
  interventions: {
    retry: number
    reminder: number
    payment_link: number
  }
  policy: {
    blocked_actions: number
    escalated_cases: number
  }
}

export interface RecoveryCase {
  risk_case_id: number
  payment_id: number
  merchant_id: number
  customer_id: number
  customer_name: string | null
  customer_email: string | null
  amount_at_risk: number
  payment_status: string | null
  payment_method: string | null
  failure_code: string | null
  failure_reason: string | null
  diagnosis_type: string | null
  recovery_probability: number | null
  recommended_action: string | null
  policy_allowed: boolean | null
  policy_reason: string | null
  escalation_required: boolean | null
  execution_id: number | null
  execution_status: string | null
  verification_status: string | null
  recovered: boolean
  created_at: string | null
}

export interface CaseDetail {
  risk_case: Record<string, unknown>
  payment: Record<string, unknown> | null
  customer: Record<string, unknown> | null
  diagnosis: Record<string, unknown> | null
  recovery: Record<string, unknown> | null
  policy: Record<string, unknown> | null
  execution: Record<string, unknown> | null
  verification: Record<string, unknown> | null
}

export interface TimelineEvent {
  step: string
  title: string
  description: string | null
  status: string
  timestamp: string | null
}

export interface Timeline {
  risk_case_id: number
  events: TimelineEvent[]
}

export interface BatchResult {
  merchant_id: number | null
  new_risk_cases_detected: number
  risk_cases_found: number
  cases_processed: number
  actions_executed: number
  actions_blocked: number
  escalated_cases: number
  successful_recoveries: number
  total_amount_at_risk: number
  recovered_amount: number
  money_recovery_rate: number
  results: RecoveryCase[]
}

export interface DemoResult {
  merchant_id: number
  merchant_created: boolean
  customers_created: number
  payments_created: number
  successful_payments: number
  failed_payments: number
}
