const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  const response = await fetch(url, { ...options, headers });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: response.statusText }));
    let detailMsg = `API Error: ${response.status}`;
    if (typeof errorData?.detail === "string") {
      detailMsg = errorData.detail;
    } else if (Array.isArray(errorData?.detail)) {
      detailMsg = errorData.detail.map((d: any) => d.msg || JSON.stringify(d)).join(", ");
    } else if (errorData?.detail) {
      detailMsg = JSON.stringify(errorData.detail);
    } else if (errorData?.message) {
      detailMsg = errorData.message;
    }
    throw new Error(detailMsg);
  }
  return response.json() as Promise<T>;
}


// -----------------------------------------------------------------------------
// Catalog
// -----------------------------------------------------------------------------
export interface Product {
  sku: string;
  name: string;
  category: string;
  price: number;
  currency: string;
  inventory: number;
  description: string;
  variants: any[];
  shipping_info: any;
  return_policy: any;
  offers: any[];
  bundle_relationships: any[];
  catalog_version: number;
  suspicious_content_flag: boolean;
}

export async function getProducts(merchantId: string = "m_001"): Promise<{ products: Product[] }> {
  return fetchApi<{ products: Product[] }>(`/catalog/products?merchant_id=${merchantId}`);
}

// -----------------------------------------------------------------------------
// Commerce Agent & Checkout
// -----------------------------------------------------------------------------
export interface CartItem {
  sku: string;
  qty: number;
  observed_price: number;
  catalog_version: number;
  snapshot_id?: string;
  source: string;
}

export interface Recommendation {
  sku: string;
  reason: string;
  price: number;
}

export interface ChatResponse {
  session_id: string;
  reply: string;
  cart: { items: CartItem[]; subtotal: number };
  recommendations: Recommendation[];
}

export interface GuardianCheck {
  name: string;
  passed: boolean;
  detail: string;
}

export interface GuardianDecision {
  decision_id: string;
  decision: "APPROVE" | "BLOCK" | "REQUIRE_CONFIRMATION";
  checks: GuardianCheck[];
  primary_reason: string;
  final_verified_total?: number;
  receipt_id: string;
}

export interface CheckoutResponse {
  decision: GuardianDecision;
  razorpay_order?: {
    order_id: string;
    amount: number;
    currency: string;
    key_id: string;
  };
}

export async function sendChatMessage(sessionId: string, buyerId: string, message: string): Promise<ChatResponse> {
  return fetchApi<ChatResponse>("/agent/chat", {
    method: "POST",
    body: JSON.stringify({ session_id: sessionId, buyer_id: buyerId, message }),
  });
}

export async function checkoutCart(sessionId: string, buyerId: string, merchantId: string = "m_001"): Promise<CheckoutResponse> {
  return fetchApi<CheckoutResponse>("/agent/checkout-intent", {
    method: "POST",
    body: JSON.stringify({ session_id: sessionId, buyer_id: buyerId, merchant_id: merchantId }),
  });
}

export async function verifyPayment(orderId: string, paymentId: string, signature: string) {
  return fetchApi<{ verified: boolean; receipt_id?: string }>("/payments/verify", {
    method: "POST",
    body: JSON.stringify({
      razorpay_order_id: orderId,
      razorpay_payment_id: paymentId,
      razorpay_signature: signature,
    }),
  });
}

// -----------------------------------------------------------------------------
// Receipts
// -----------------------------------------------------------------------------
export interface ReceiptData {
  receipt_id: string;
  decision_id: string;
  intent_id?: string;
  merchant_id: string;
  items_snapshot: any[];
  observed_total: number;
  final_verified_total?: number;
  mandate_snapshot?: any;
  policy_snapshot?: any;
  guardian_checks: GuardianCheck[];
  decision: "APPROVE" | "BLOCK" | "REQUIRE_CONFIRMATION";
  reason: string;
  razorpay_order_id?: string;
  razorpay_payment_id?: string;
  failure_reason?: string;
  created_at: string;
}

export async function getReceipt(receiptId: string): Promise<ReceiptData> {
  return fetchApi<ReceiptData>(`/receipts/${receiptId}`);
}

export async function listReceipts(merchantId: string = "m_001"): Promise<{ receipts: ReceiptData[] }> {
  return fetchApi<{ receipts: ReceiptData[] }>(`/receipts?merchant_id=${merchantId}`);
}

export async function replayReceipt(receiptId: string) {
  return fetchApi<{
    receipt_id: string;
    original_decision: string;
    replay_decision: string;
    matches_original: boolean;
    replayed_checks: GuardianCheck[];
    replayed_reason: string;
  }>(`/receipts/${receiptId}/replay`, { method: "POST" });
}

// -----------------------------------------------------------------------------
// Dashboard & Analytics
// -----------------------------------------------------------------------------
export interface RevenueAnalytics {
  total_revenue: number;
  store_revenue?: number;
  order_count: number;
  upsell_attach_rate: number;
  upsell_revenue: number;
  campaign_revenue: number;
  blocked_attempt_count: number;
}

export async function getRevenueAnalytics(merchantId: string = "m_001"): Promise<RevenueAnalytics> {
  return fetchApi<RevenueAnalytics>(`/dashboard/revenue?merchant_id=${merchantId}`);
}

// -----------------------------------------------------------------------------
// Campaign Orchestrator
// -----------------------------------------------------------------------------
export interface CampaignProposalData {
  proposal_id: string;
  merchant_id: string;
  objective: string;
  eligible_skus: string[];
  discount_pct: number;
  budget: number;
  starts_at: string;
  ends_at: string;
  rationale: string;
  guardian_decision: GuardianDecision;
}

export async function proposeCampaign(merchantId: string, objective: string): Promise<CampaignProposalData> {
  return fetchApi<CampaignProposalData>("/campaign/propose", {
    method: "POST",
    body: JSON.stringify({ merchant_id: merchantId, objective }),
  });
}

export async function activateCampaign(proposalId: string): Promise<{ campaign_id: string; status: string }> {
  return fetchApi<{ campaign_id: string; status: string }>(`/campaign/${proposalId}/activate`, {
    method: "POST",
  });
}

// -----------------------------------------------------------------------------
// Buyer Identity & OTP Auth
// -----------------------------------------------------------------------------
export interface BuyerContactProfile {
  phone_number: string;
  email: string;
  name: string;
}

export async function sendOtp(phoneOrEmail: string): Promise<{ success: boolean; demo_otp?: string; message: string }> {
  return fetchApi<{ success: boolean; demo_otp?: string; message: string }>("/auth/otp/send", {
    method: "POST",
    body: JSON.stringify({ phone_or_email: phoneOrEmail }),
  });
}

export async function verifyOtp(phoneOrEmail: string, otp: string, name?: string): Promise<{
  access_token: string;
  buyer_id: string;
  phone_number?: string;
  email?: string;
  name: string;
}> {
  return fetchApi<{
    access_token: string;
    buyer_id: string;
    phone_number?: string;
    email?: string;
    name: string;
  }>("/auth/otp/verify", {
    method: "POST",
    body: JSON.stringify({ phone_or_email: phoneOrEmail, otp, name }),
  });
}

export async function getBuyerProfile(buyerId: string = "b_001"): Promise<BuyerContactProfile> {
  return fetchApi<BuyerContactProfile>(`/auth/profile?buyer_id=${buyerId}`);
}

export async function updateBuyerProfile(buyerId: string, phone: string, email: string, name?: string): Promise<any> {
  return fetchApi("/auth/profile", {
    method: "POST",
    body: JSON.stringify({ buyer_id: buyerId, phone_number: phone, email, name }),
  });
}

// -----------------------------------------------------------------------------
// Autonomous A2A Dynamic Negotiation
// -----------------------------------------------------------------------------

export interface CounterOfferOption {
  option_id: string;
  option_type: string;
  title: string;
  description: string;
  unit_price_paise: number;
  total_amount_paise: number;
  discount_pct: number;
  projected_gross_margin_pct: number;
  margin_floor_satisfied: boolean;
  bundled_items: Array<{
    addon_sku: string;
    addon_name: string;
    addon_qty: number;
    original_price_paise: number;
    discounted_price_paise: number;
    discount_pct: number;
  }>;
  merchant_profit_lift_paise: number;
}

export interface RFQResponseData {
  status: string;
  session_id: string;
  round_index: number;
  merchant_id: string;
  catalog_total_paise: number;
  buyer_target_total_paise: number;
  minimum_margin_floor_pct: number;
  counter_offers: CounterOfferOption[];
  reason: string;
  ai_pricing_agent_notes: string;
}

export interface NegotiationSettlementData {
  status: string;
  guardian_decision: string;
  session_id: string;
  receipt_id: string;
  final_verified_total_paise: number;
  razorpay_order_id?: string;
  payment_link?: string;
  replay_hash: string;
  negotiated_items: Array<{ sku: string; qty: number; price_inr: string }>;
  merchant_margin_achieved_pct: number;
  reason: string;
}

export async function submitRFQ(rfqData: {
  sku: string;
  qty: number;
  target_unit_price_paise: number;
  buyer_agent_id?: string;
}): Promise<RFQResponseData> {
  const targetTotal = rfqData.target_unit_price_paise * rfqData.qty;
  const mandateMax = Math.max(10000000, targetTotal * 2);
  return fetchApi<RFQResponseData>("/commerce/rfq", {
    method: "POST",
    body: JSON.stringify({
      buyer_agent_id: rfqData.buyer_agent_id || "ai_buyer_agent_procure_42",
      merchant_id: "m_001",
      buyer_mandate: {
        buyer_id: "b_001",
        max_amount: mandateMax,
        max_quantity_per_item: 10,
        currency: "INR",
        signature: "sig_rfq_mandate",
      },
      items: [
        {
          sku: rfqData.sku,
          qty: rfqData.qty,
          target_unit_price_paise: rfqData.target_unit_price_paise,
        },
      ],
    }),
  });
}


export async function acceptNegotiatedOffer(acceptData: {
  session_id: string;
  selected_option_id?: string;
  option_id?: string;
  buyer_agent_id?: string;
  buyer_id?: string;
  merchant_id?: string;
}): Promise<NegotiationSettlementData> {
  const chosenOption = acceptData.selected_option_id || acceptData.option_id || "";
  return fetchApi<NegotiationSettlementData>("/commerce/accept", {
    method: "POST",
    body: JSON.stringify({
      session_id: acceptData.session_id,
      buyer_agent_id: acceptData.buyer_agent_id || acceptData.buyer_id || "ai_buyer_agent_procure_42",
      merchant_id: acceptData.merchant_id || "m_001",
      selected_option_id: chosenOption,
      buyer_signature: "sig_ed25519_buyer_accepted_contract",
    }),
  });
}

// -----------------------------------------------------------------------------
// Headless Razorpay UPI AutoPay API
// -----------------------------------------------------------------------------
export interface AutoPayStatusData {
  autopay_enabled: boolean;
  status: string;
  buyer_id: string;
  token_id?: string;
  customer_id?: string;
  max_amount_paise: number;
  max_amount_per_charge_paise?: number;
  total_spent_paise?: number;
  remaining_headroom_paise?: number;
  spent_pct?: number;
  vpa?: string;
  bank_name?: string;
  auth_url?: string;
  message?: string;
}

export interface AutoPayMandateItem {
  mandate_id: string;
  buyer_id: string;
  autopay_enabled: boolean;
  status: string;
  token_id?: string;
  customer_id?: string;
  max_amount_paise: number;
  max_amount_per_charge_paise: number;
  total_spent_paise: number;
  remaining_headroom_paise: number;
  vpa: string;
  bank_name: string;
  created_at?: string;
}

export interface AutoPayAllResponse {
  mandates: AutoPayMandateItem[];
  summary: {
    total_mandates: number;
    active_mandates: number;
    total_active_headroom_paise: number;
    total_autopay_volume_paise: number;
  };
}

export async function getAutoPayStatus(buyerId: string = "b_001"): Promise<AutoPayStatusData> {
  return fetchApi<AutoPayStatusData>(`/mandates/autopay/status?buyer_id=${buyerId}`);
}

export async function setupAutoPayMandate(payload: {
  buyer_id?: string;
  max_amount_paise: number; // Min 3000000 (₹30,000)
  max_amount_per_charge_paise?: number;
  bank_name?: string;
  vpa?: string;
}): Promise<AutoPayStatusData> {
  return fetchApi<AutoPayStatusData>("/mandates/autopay/setup", {
    method: "POST",
    body: JSON.stringify({
      buyer_id: payload.buyer_id || "b_001",
      max_amount_paise: Math.max(3000000, payload.max_amount_paise),
      max_amount_per_charge_paise: payload.max_amount_per_charge_paise || payload.max_amount_paise,
      bank_name: payload.bank_name || "HDFC Bank (UPI AutoPay)",
      vpa: payload.vpa || `${payload.buyer_id || "b_001"}@okhdfcbank`,
    }),
  });
}

export async function revokeAutoPayMandate(buyerId: string = "b_001"): Promise<{ status: string; buyer_id: string; message: string }> {
  return fetchApi<{ status: string; buyer_id: string; message: string }>(`/mandates/autopay/revoke?buyer_id=${buyerId}`, {
    method: "POST",
  });
}

export async function listAllAutoPayMandates(): Promise<AutoPayAllResponse> {
  return fetchApi<AutoPayAllResponse>("/mandates/autopay/all");
}

// Backward-compatibility aliases
export type AutoPayStatus = AutoPayStatusData;
export const setupAutoPay = setupAutoPayMandate;
export const revokeAutoPay = revokeAutoPayMandate;




