import { useEffect, useMemo, useState } from 'react'
import { ArrowUpRight, Bot, CheckCircle2, ChevronRight, CircleAlert, LayoutDashboard, LoaderCircle, Play, RefreshCw, Search, ShieldCheck, Sparkles, WalletCards, XCircle, Zap } from 'lucide-react'
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { fetchCase, fetchCases, fetchSummary, fetchTimeline, generateDemoData, processBatch } from './api/dashboard'
import type { BatchResult, CaseDetail, DemoResult, RecoveryCase, Summary, Timeline } from './types/api'
import './styles.css'

type Page = 'dashboard' | 'cases' | 'demo' | 'detail'

const money = new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 })
const compactMoney = new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', notation: 'compact', maximumFractionDigits: 1 })

function formatMoney(value: number | null | undefined, compact = false) {
  return (compact ? compactMoney : money).format(value || 0)
}

function label(value: string | null | undefined) {
  return value ? value.replaceAll('_', ' ') : 'Pending'
}

function StatusBadge({ value, tone }: { value: string | boolean | null | undefined; tone?: 'success' | 'danger' | 'muted' }) {
  const resolvedTone = tone || (value === true || value === 'success' || value === 'recovered' ? 'success' : value === false || value === 'failed' || value === 'blocked' ? 'danger' : 'muted')
  return <span className={`badge badge-${resolvedTone}`}><span className="badge-dot" />{typeof value === 'boolean' ? (value ? 'Allowed' : 'Blocked') : label(value)}</span>
}

function App() {
  const [page, setPage] = useState<Page>('dashboard')
  const [selectedCaseId, setSelectedCaseId] = useState<number | null>(null)
  const [merchantId, setMerchantId] = useState(1)
  const [summary, setSummary] = useState<Summary | null>(null)
  const [cases, setCases] = useState<RecoveryCase[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [refreshKey, setRefreshKey] = useState(0)

  useEffect(() => {
    setLoading(true)
    setError('')
    Promise.all([fetchSummary(merchantId), fetchCases(merchantId)])
      .then(([nextSummary, nextCases]) => { setSummary(nextSummary); setCases(nextCases) })
      .catch(() => setError('The backend could not be reached. Check that FastAPI is running on port 8000.'))
      .finally(() => setLoading(false))
  }, [merchantId, refreshKey])

  function openCase(id: number) { setSelectedCaseId(id); setPage('detail') }

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark"><Sparkles size={19} /></div><div><strong>Revenue Recovery</strong><span>Agent console</span></div></div>
      <div className="merchant-switcher"><span>Monitoring merchant</span><label><span>#</span><input value={merchantId} onChange={(event) => setMerchantId(Number(event.target.value) || 1)} type="number" min="1" /></label></div>
      <nav>
        <button className={page === 'dashboard' ? 'nav-item active' : 'nav-item'} onClick={() => setPage('dashboard')}><LayoutDashboard size={18} />Dashboard</button>
        <button className={page === 'cases' || page === 'detail' ? 'nav-item active' : 'nav-item'} onClick={() => setPage('cases')}><WalletCards size={18} />Recovery cases<span className="nav-count">{cases.length}</span></button>
        <button className={page === 'demo' ? 'nav-item active' : 'nav-item'} onClick={() => setPage('demo')}><Bot size={18} />Demo simulation</button>
      </nav>
      <div className="sidebar-footer"><div className="status-light"><span />System operational</div><small>AI-powered revenue risk orchestration</small></div>
    </aside>
    <main className="main-content">
      <header className="topbar"><div className="mobile-brand"><div className="brand-mark"><Sparkles size={16} /></div><strong>Revenue Recovery</strong></div><div className="topbar-meta"><span className="live-dot" />Live data</div><button className="icon-button" title="Refresh data" onClick={() => setRefreshKey((key) => key + 1)}><RefreshCw size={17} /></button></header>
      {error && <div className="error-banner"><CircleAlert size={18} />{error}<button onClick={() => setRefreshKey((key) => key + 1)}>Retry</button></div>}
      {page === 'dashboard' && <DashboardPage summary={summary} cases={cases} loading={loading} onOpenCase={openCase} onGoDemo={() => setPage('demo')} />}
      {page === 'cases' && <CasesPage cases={cases} loading={loading} onOpenCase={openCase} />}
      {page === 'detail' && selectedCaseId !== null && <DetailPage riskCaseId={selectedCaseId} onBack={() => setPage('cases')} />}
      {page === 'demo' && <DemoPage merchantId={merchantId} onComplete={() => { setRefreshKey((key) => key + 1); setPage('dashboard') }} />}
    </main>
  </div>
}

function PageHeader({ eyebrow, title, description, action }: { eyebrow: string; title: string; description: string; action?: React.ReactNode }) {
  return <div className="page-header"><div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{description}</p></div>{action}</div>
}

function DashboardPage({ summary, cases, loading, onOpenCase, onGoDemo }: { summary: Summary | null; cases: RecoveryCase[]; loading: boolean; onOpenCase: (id: number) => void; onGoDemo: () => void }) {
  const overview = summary?.overview
  const statusData = summary ? Object.entries(summary.case_status).map(([name, value]) => ({ name: label(name), value })) : []
  const interventionData = summary ? Object.entries(summary.interventions).map(([name, value]) => ({ name: label(name), value })) : []
  const performanceData = summary ? [{ name: 'Recovered', amount: overview?.recovered_amount || 0 }, { name: 'At risk', amount: Math.max((overview?.total_amount_at_risk || 0) - (overview?.recovered_amount || 0), 0) }] : []
  const recentCases = cases.slice(0, 5)
  return <div className="page"><PageHeader eyebrow="Portfolio overview" title="Recovery command center" description="See where revenue is exposed, how the agent is responding, and what has been recovered." action={<button className="primary-button" onClick={onGoDemo}><Play size={16} />Run simulation</button>} />
    {loading && !summary ? <LoadingState /> : <>
      <section className="kpi-grid">
        <KpiCard label="Amount at risk" value={formatMoney(overview?.total_amount_at_risk)} sub="Across detected cases" icon={<CircleAlert />} tone="coral" />
        <KpiCard label="Money recovered" value={formatMoney(overview?.recovered_amount)} sub={`${overview?.recovered_cases || 0} cases recovered`} icon={<WalletCards />} tone="mint" />
        <KpiCard label="Recovery rate" value={`${overview?.recovery_rate || 0}%`} sub="Case recovery conversion" icon={<ArrowUpRight />} tone="blue" />
        <KpiCard label="Total cases" value={String(overview?.total_cases || 0)} sub={`${summary?.policy.escalated_cases || 0} need attention`} icon={<Zap />} tone="gold" />
      </section>
      <section className="chart-grid"><div className="panel chart-panel wide"><PanelHeading title="Recovery performance" caption="Value movement across your portfolio" /><div className="chart-wrap"><ResponsiveContainer width="100%" height="100%"><BarChart data={performanceData} layout="vertical" margin={{ left: 16, right: 22 }}><CartesianGrid horizontal={false} stroke="#e6e1d8" /><XAxis type="number" tickFormatter={(value) => formatMoney(value, true)} axisLine={false} tickLine={false} tick={{ fill: '#8a877f', fontSize: 11 }} /><YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fill: '#4b4a45', fontSize: 12 }} width={68} /><Tooltip formatter={(value) => formatMoney(Number(value))} cursor={{ fill: '#f7f3ec' }} /><Bar dataKey="amount" radius={[0, 5, 5, 0]} barSize={30}>{performanceData.map((entry) => <Cell key={entry.name} fill={entry.name === 'Recovered' ? '#1d8b6c' : '#e78b6d'} />)}</Bar></BarChart></ResponsiveContainer></div></div><div className="panel chart-panel"><PanelHeading title="Case status" caption="Current lifecycle position" /><div className="chart-wrap"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={statusData} dataKey="value" nameKey="name" innerRadius={54} outerRadius={82} paddingAngle={4}>{statusData.map((entry, index) => <Cell key={entry.name} fill={['#1d8b6c', '#e7bd58', '#7197b3', '#d97862'][index % 4]} />)}</Pie><Tooltip /><text x="50%" y="47%" textAnchor="middle" dominantBaseline="middle" className="donut-total">{overview?.total_cases || 0}</text><text x="50%" y="59%" textAnchor="middle" dominantBaseline="middle" className="donut-label">cases</text></PieChart></ResponsiveContainer></div></div></section>
      <section className="lower-grid"><div className="panel"><PanelHeading title="Recent cases" caption="Latest agent activity" action={<button className="text-button" onClick={() => onOpenCase(recentCases[0]?.risk_case_id)}>View latest <ChevronRight size={14} /></button>} />{recentCases.length === 0 ? <EmptyState message="No recovery cases yet. Run a demo simulation to populate the portfolio." /> : <div className="mini-list">{recentCases.map((item) => <button className="mini-row" key={item.risk_case_id} onClick={() => onOpenCase(item.risk_case_id)}><span className="case-avatar">{item.customer_name?.slice(0, 1) || 'R'}</span><span className="mini-main"><strong>Case #{item.risk_case_id}</strong><small>{item.customer_name || 'Unknown customer'} · {label(item.diagnosis_type)}</small></span><span className="mini-value"><strong>{formatMoney(item.amount_at_risk)}</strong><StatusBadge value={item.recovered ? 'recovered' : item.execution_status || item.payment_status} /></span><ChevronRight size={15} className="row-chevron" /></button>)}</div>}</div><div className="panel"><PanelHeading title="Intervention mix" caption="Recommendations by volume" /><div className="intervention-list">{interventionData.map((item, index) => <div className="intervention-row" key={item.name}><div><span className={`intervention-icon i-${index}`}><Zap size={14} /></span><strong>{item.name}</strong></div><span>{item.value}</span></div>)}</div><div className="attention-callout"><ShieldCheck size={17} /><span><strong>{summary?.policy.blocked_actions || 0} blocked actions</strong><small>Policy guardrails kept the workflow safe</small></span></div></div></section>
    </>}
  </div>
}

function KpiCard({ label: title, value, sub, icon, tone }: { label: string; value: string; sub: string; icon: React.ReactNode; tone: string }) { return <div className={`kpi-card tone-${tone}`}><div className="kpi-icon">{icon}</div><div className="kpi-label">{title}</div><div className="kpi-value">{value}</div><div className="kpi-sub">{sub}</div></div> }
function PanelHeading({ title, caption, action }: { title: string; caption: string; action?: React.ReactNode }) { return <div className="panel-heading"><div><h2>{title}</h2><p>{caption}</p></div>{action}</div> }
function LoadingState() { return <div className="loading-state"><LoaderCircle className="spin" size={25} /><span>Loading live recovery data...</span></div> }
function EmptyState({ message }: { message: string }) { return <div className="empty-state"><Bot size={25} /><p>{message}</p></div> }

function CasesPage({ cases, loading, onOpenCase }: { cases: RecoveryCase[]; loading: boolean; onOpenCase: (id: number) => void }) {
  const [query, setQuery] = useState('')
  const [filter, setFilter] = useState('all')
  const filtered = useMemo(() => cases.filter((item) => { const search = `${item.risk_case_id} ${item.payment_id} ${item.customer_name || ''} ${item.customer_email || ''}`.toLowerCase(); return search.includes(query.toLowerCase()) && (filter === 'all' || (filter === 'recovered' ? item.recovered : filter === 'blocked' ? item.policy_allowed === false : item.recommended_action === filter)) }), [cases, filter, query])
  return <div className="page"><PageHeader eyebrow="Agent workflow" title="Recovery cases" description="Trace every payment risk from detection through verified recovery." action={<span className="record-count">{filtered.length} records</span>} /><div className="panel table-panel"><div className="table-toolbar"><label className="search-box"><Search size={17} /><input placeholder="Search case, payment, or customer" value={query} onChange={(event) => setQuery(event.target.value)} /></label><select value={filter} onChange={(event) => setFilter(event.target.value)}><option value="all">All statuses</option><option value="recovered">Recovered</option><option value="blocked">Policy blocked</option><option value="retry">Retry</option><option value="reminder">Reminder</option><option value="payment_link">Payment link</option></select></div>{loading ? <LoadingState /> : filtered.length === 0 ? <EmptyState message="No cases match the current filters." /> : <div className="table-scroll"><table><thead><tr><th>Case</th><th>Customer</th><th>At risk</th><th>Diagnosis</th><th>Action</th><th>Policy</th><th>Execution</th><th>Verification</th><th>Result</th></tr></thead><tbody>{filtered.map((item) => <tr key={item.risk_case_id} onClick={() => onOpenCase(item.risk_case_id)}><td><strong>#{item.risk_case_id}</strong><small>Payment #{item.payment_id}</small></td><td><strong>{item.customer_name || 'Unknown'}</strong><small>{item.customer_email || 'No email'}</small></td><td><strong>{formatMoney(item.amount_at_risk)}</strong></td><td>{label(item.diagnosis_type)}</td><td><span className="action-label">{label(item.recommended_action)}</span></td><td><StatusBadge value={item.policy_allowed} /></td><td><StatusBadge value={item.execution_status} /></td><td><StatusBadge value={item.verification_status} /></td><td>{item.recovered ? <span className="result recovered"><CheckCircle2 size={16} />Recovered</span> : <span className="result pending"><XCircle size={16} />Open</span>}</td></tr>)}</tbody></table></div>}</div></div>
}

function DetailPage({ riskCaseId, onBack }: { riskCaseId: number; onBack: () => void }) {
  const [detail, setDetail] = useState<CaseDetail | null>(null)
  const [timeline, setTimeline] = useState<Timeline | null>(null)
  const [error, setError] = useState('')
  useEffect(() => { Promise.all([fetchCase(riskCaseId), fetchTimeline(riskCaseId)]).then(([nextDetail, nextTimeline]) => { setDetail(nextDetail); setTimeline(nextTimeline) }).catch(() => setError('Could not load this recovery case.')) }, [riskCaseId])
  if (error) return <div className="page"><button className="back-button" onClick={onBack}>← Back to cases</button><div className="error-panel">{error}</div></div>
  if (!detail || !timeline) return <div className="page"><button className="back-button" onClick={onBack}>← Back to cases</button><LoadingState /></div>
  const risk = detail.risk_case; const payment = detail.payment || {}; const customer = detail.customer || {}; const diagnosis = detail.diagnosis || {}; const recovery = detail.recovery || {}; const policy = detail.policy || {}; const execution = detail.execution || {}; const verification = detail.verification || {}
  return <div className="page"><button className="back-button" onClick={onBack}>← Back to cases</button><PageHeader eyebrow={`Recovery case #${riskCaseId}`} title={String(customer.name || 'Unknown customer')} description={`${String(payment.failure_code || 'Payment exception')} · ${formatMoney(Number(risk.amount_at_risk))} at risk`} action={<StatusBadge value={Boolean(verification.payment_verified)} />} /><div className="detail-layout"><div className="detail-main"><DetailSection title="Payment information" icon={<WalletCards />}><InfoGrid items={[["Payment ID", payment.external_payment_id || `#${String(payment.id || '')}`], ["Amount", formatMoney(Number(payment.amount))], ["Method", label(String(payment.payment_method || ''))], ["Failure code", payment.failure_code || '—'], ["Failure reason", payment.failure_reason || '—']]} /></DetailSection><DetailSection title="Customer information" icon={<Bot />}><InfoGrid items={[["Name", customer.name || '—'], ["Email", customer.email || '—']]} /></DetailSection><div className="detail-duo"><DetailSection title="AI diagnosis" icon={<Sparkles />}><InfoGrid items={[["Type", diagnosis.diagnosis_type || 'Pending'], ["Root cause", diagnosis.root_cause || '—'], ["Confidence", diagnosis.confidence_score ? `${diagnosis.confidence_score}%` : '—']]} /></DetailSection><DetailSection title="Recovery decision" icon={<Zap />}><InfoGrid items={[["Probability", recovery.recovery_probability ? `${recovery.recovery_probability}%` : '—'], ["Intervention", label(String(recovery.recommended_intervention || ''))], ["Status", label(String(recovery.status || ''))]]} /></DetailSection></div><DetailSection title="Policy and execution" icon={<ShieldCheck />}><InfoGrid items={[["Policy", policy.is_allowed === undefined ? 'Pending' : policy.is_allowed ? 'Allowed' : 'Blocked'], ["Reason", policy.reason || '—'], ["Escalation", policy.escalation_required ? 'Required' : 'No'], ["Execution", execution.execution_status || 'Not executed'], ["Verification", verification.verification_status || 'Not verified']]} /></DetailSection></div><div className="timeline-panel"><div className="eyebrow">Case lifecycle</div><h2>Agent activity</h2><p className="section-caption">A record of every decision in the recovery workflow.</p><div className="timeline">{timeline.events.map((event) => <div className="timeline-item" key={event.step}><div className={`timeline-node node-${event.status === 'completed' || event.status === 'success' || event.status === 'recovered' || event.status === 'allowed' ? 'done' : event.status === 'blocked' || event.status === 'failed' ? 'alert' : 'idle'}`}>{event.status === 'completed' || event.status === 'success' || event.status === 'recovered' || event.status === 'allowed' ? <CheckCircle2 size={15} /> : <span />}</div><div><div className="timeline-top"><strong>{event.title}</strong><StatusBadge value={event.status} /></div><p>{event.description || 'Awaiting this workflow step.'}</p>{event.timestamp && <small>{new Date(event.timestamp).toLocaleString()}</small>}</div></div>)}</div></div></div></div>
}

function DetailSection({ title, icon, children }: { title: string; icon: React.ReactNode; children: React.ReactNode }) { return <section className="detail-section"><div className="section-heading"><span>{icon}</span><h2>{title}</h2></div>{children}</section> }
function InfoGrid({ items }: { items: [string, unknown][] }) { return <div className="info-grid">{items.map(([key, value]) => <div key={key}><span>{key}</span><strong>{typeof value === 'object' && value !== null ? JSON.stringify(value) : String(value ?? '—')}</strong></div>)}</div> }

function DemoPage({ merchantId, onComplete }: { merchantId: number; onComplete: () => void }) {
  const [customerCount, setCustomerCount] = useState(10); const [paymentsPerCustomer, setPaymentsPerCustomer] = useState(5); const [step, setStep] = useState<'idle' | 'generating' | 'processing' | 'done'>('idle'); const [demo, setDemo] = useState<DemoResult | null>(null); const [batch, setBatch] = useState<BatchResult | null>(null); const [error, setError] = useState('')
  async function run() { setError(''); setStep('generating'); try { const nextDemo = await generateDemoData(merchantId, customerCount, paymentsPerCustomer); setDemo(nextDemo); setStep('processing'); const nextBatch = await processBatch(merchantId); setBatch(nextBatch); setStep('done') } catch { setError('The simulation could not complete. Check the backend and try again.') } }
  const busy = step === 'generating' || step === 'processing'
  return <div className="page"><PageHeader eyebrow="Controlled simulation" title="Run the recovery agent" description="Generate a realistic payment failure cohort, then watch the orchestration pipeline resolve it." /><div className="demo-layout"><div className="panel demo-form"><div className="demo-orbit"><div className="orbit-core"><Bot size={31} /></div><span className="orbit-ring ring-one" /><span className="orbit-ring ring-two" /></div><div className="eyebrow">Simulation inputs</div><h2>Build a merchant cohort</h2><p>Use this sandbox to populate the agent with failed payments and move them through risk, diagnosis, policy, execution, and verification.</p><label>Merchant ID<input type="number" min="1" value={merchantId} readOnly /></label><div className="form-row"><label>Customers<input type="number" min="1" max="100" value={customerCount} onChange={(event) => setCustomerCount(Number(event.target.value))} /></label><label>Payments / customer<input type="number" min="1" max="50" value={paymentsPerCustomer} onChange={(event) => setPaymentsPerCustomer(Number(event.target.value))} /></label></div><button className="primary-button full-button" disabled={busy} onClick={run}>{busy ? <><LoaderCircle className="spin" size={17} />{step === 'generating' ? 'Generating data...' : 'Agent is processing...'}</> : <><Play size={17} />Run AI recovery agent</>}</button>{error && <div className="form-error"><CircleAlert size={16} />{error}</div>}</div><div className="panel pipeline-panel"><div className="eyebrow">Live run status</div><h2>From failed payment to recovered revenue</h2><div className="pipeline">{['Generate payment cohort', 'Detect revenue risk', 'Diagnose root cause', 'Evaluate policy', 'Execute intervention', 'Verify payment'].map((name, index) => { const active = step === 'generating' ? index === 0 : step === 'processing' ? index > 0 : step === 'done'; return <div className={`pipeline-step ${active ? 'active' : ''} ${step === 'done' ? 'complete' : ''}`} key={name}><span>{step === 'done' ? <CheckCircle2 size={16} /> : index + 1}</span><strong>{name}</strong></div> })}</div>{batch && <div className="batch-result"><div className="result-head"><div><div className="eyebrow">Run complete</div><h3>Revenue recovery report</h3></div><span className="success-mark"><CheckCircle2 size={20} /></span></div><div className="result-grid"><ResultMetric label="New risk cases" value={batch.new_risk_cases_detected} /><ResultMetric label="Cases processed" value={batch.cases_processed} /><ResultMetric label="Actions executed" value={batch.actions_executed} /><ResultMetric label="Successful recoveries" value={batch.successful_recoveries} /><ResultMetric label="At risk" value={formatMoney(batch.total_amount_at_risk)} /><ResultMetric label="Recovered" value={formatMoney(batch.recovered_amount)} /></div><div className="recovery-highlight"><span>Money recovery rate</span><strong>{batch.money_recovery_rate}%</strong></div><button className="text-button" onClick={onComplete}>Open refreshed dashboard <ArrowUpRight size={15} /></button></div>}{demo && !batch && <div className="demo-note"><CheckCircle2 size={17} />Generated {demo.payments_created} payments, including {demo.failed_payments} failed payments.</div>}</div></div></div>
}
function ResultMetric({ label: title, value }: { label: string; value: string | number }) { return <div><span>{title}</span><strong>{value}</strong></div> }

export default App
