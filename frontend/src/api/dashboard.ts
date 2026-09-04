import { api } from './client'
import type { BatchResult, CaseDetail, DemoResult, RecoveryCase, Summary, Timeline } from '../types/api'

export async function fetchSummary(merchantId?: number): Promise<Summary> {
  const response = await api.get<Summary>('/api/dashboard/summary', { params: merchantId ? { merchant_id: merchantId } : undefined })
  return response.data
}

export async function fetchCases(merchantId?: number): Promise<RecoveryCase[]> {
  const response = await api.get<RecoveryCase[]>('/api/dashboard/cases', { params: merchantId ? { merchant_id: merchantId } : undefined })
  return response.data
}

export async function fetchCase(riskCaseId: number): Promise<CaseDetail> {
  const response = await api.get<CaseDetail>(`/api/dashboard/cases/${riskCaseId}`)
  return response.data
}

export async function fetchTimeline(riskCaseId: number): Promise<Timeline> {
  const response = await api.get<Timeline>(`/api/dashboard/cases/${riskCaseId}/timeline`)
  return response.data
}

export async function generateDemoData(merchantId: number, customerCount: number, paymentsPerCustomer: number): Promise<DemoResult> {
  const response = await api.post<DemoResult>('/api/demo/generate', null, { params: { merchant_id: merchantId, customer_count: customerCount, payments_per_customer: paymentsPerCustomer } })
  return response.data
}

export async function processBatch(merchantId: number): Promise<BatchResult> {
  const response = await api.post<BatchResult>('/api/batch/process', null, { params: { merchant_id: merchantId } })
  return response.data
}
