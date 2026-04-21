# NoCode Apps - KT Reference Doc

**Date:** Mar 12, 2026
**Context:** Initial KT for Shobhit Jain's takeover of the Low Code / No Code Apps portfolio.

---

## 1. Product Portfolio Overview

All products share a similar creation flow but differ in underlying tables and UI.

| Product | Importance | Description |
|---------|-----------|-------------|
| **Payment Links** | Highest (800k DAU) | Link-based payment collection, most traffic and revenue |
| **Payment Pages** | High | Form-based payment pages with custom fields |
| **Web Stores** | Medium | Shopping-style UI showing a few items for purchase |
| **Payment Handles** | Medium | Auto-created per-merchant links (e.g. `razorpay.me/merchant`), 95% same as Payment Pages |
| **Payment Buttons** | Low | Embeddable HTML button that opens a payment page overlay, then Checkout SDK |
| **Invoices** | Medium | Distinct product — generates local invoice PDFs, supports single/multiple payments. No govt API integration (IRN/chalan) |
| **WhatsApp Native Payments (WANP)** | Special | Built with Meta partnership, frequent source of issues |
| **Gimli** | Utility | URL shortening service |

---

## 2. Repositories

### Backend Services

| Repo | GitHub | Products | Language |
|------|--------|----------|----------|
| **no-code-apps** | [razorpay/no-code-apps](https://github.com/razorpay/no-code-apps) | Payment Pages, Web Stores, Handles, Buttons | Go |
| **payment-links** | [razorpay/payment-links](https://github.com/razorpay/payment-links) | Payment Links | Go |
| **invoices** | [razorpay/invoices](https://github.com/razorpay/invoices) | Invoices | Go |
| **gimli** | [razorpay/gimli](https://github.com/razorpay/gimli) | URL Shortener | Go |
| **api** (monolith) | [razorpay/api](https://github.com/razorpay/api) | Legacy — being decomposed out | PHP |
| **stork** | [razorpay/stork](https://github.com/razorpay/stork) | Notifications (webhooks, SMS, email) used by all products | Go |

### Frontend

| Repo | Description |
|------|-------------|
| **razorpay/dashboard** | Merchant-facing dashboard UI |
| **razorpay/static** | UI and static assets for payment pages/links |
| **razorpay/frontend-stores-ecommerce** | Frontend UI specifically for Web Stores |

All repos have `agents.md` / `AGENTS.md` files for AI agent context.

---

## 3. Decomp (De-Monolithization) Status

| Product | Decomp Status | Target Repo | Notes |
|---------|--------------|-------------|-------|
| **Payment Links** | ~95% complete | `payment-links` | Final migration steps remaining |
| **Payment Pages** | In progress, ETA this month (Mar 2026) | `no-code-apps` | Dual-write + shadowing strategy |
| **Web Stores** | 100% complete | `no-code-apps` | Already fully moved out of monolith |
| **Payment Handles** | Active — dual write in place | `no-code-apps` | Monolith function replacement in progress |
| **Payment Buttons** | Early planning / spec phase | `no-code-apps` | Migration phases defined, not started |
| **Invoices** | ~70% dev complete | `invoices` | Dev: ~1 more month. Full migration (incl. data migration): ~2 more months. Data migration is the hardest part, needs GTM plan |
| **Gimli** | Standalone | `gimli` | Already separate |

---

## 4. Tech Specs & Documentation

### Decomp Specs

| Doc | Link |
|-----|------|
| Payment Pages Decomp Spec | [Google Doc](https://docs.google.com/document/d/14-CZOZKtn5-FtsvLIOeCd9JgAFEOi_YBbU-zZreopWU/edit?tab=t.0#heading=h.rd7hpjfh29ai) |
| Payment Links Tech Spec | [Google Doc](https://docs.google.com/document/d/14af-WP9NpmMcOqk9PHsMOlLnZGCXpUFbIXGRWu0Xwuw/edit?tab=t.0#heading=h.i3rn67z2j8su) |
| Payment Handles Decomp Spec | [Google Doc](https://docs.google.com/document/d/1n6yOW0tOkT2LuaKyjrHdIBPexeOQoxwKVLRA1vD70nA/edit?tab=t.0#heading=h.rd7hpjfh29ai) |
| Payment Buttons Decomp Spec | [Google Doc](https://docs.google.com/document/d/1DER5Ibz799f-0fpc2LqW0Chf2uGEAeU3R8u3cgvPG10/edit?tab=t.0#heading=h.rd7hpjfh29ai) |
| Invoices Decomp Spec | [Google Doc](https://docs.google.com/document/d/1GaFmlqpLEVO5wXGKpDmZH-amvPvILfoxhDPPGDUKeXE/edit?tab=t.0#heading=h.rd7hpjfh29ai) |
| Invoices Project Plan | [Google Sheet](https://docs.google.com/spreadsheets/d/1CBNoziuqJqWjwVknc5GeDVWNSVRifn6Lr3O2nlkWJC8/edit?gid=0#gid=0) |
| Task Breakup Sheet (PP, PH, PB) | [Google Sheet](https://docs.google.com/spreadsheets/d/1AL_iDy-RRmZuinq0jMj4PG5XM6VpXaKnFcV5HxcOtr8/edit?gid=394929843#gid=394929843) |

### WhatsApp Native Payments (WANP) Specs

| Doc | Link |
|-----|------|
| WANP Main Spec | [Google Doc](https://docs.google.com/document/d/1J4DdL4aVhPXRVTeYkjvGocCCC9K9mefx2FT2yivdWqc/edit?tab=t.0#heading=h.37qewst9ki6) |
| Payment Links as WANP | [Google Doc](https://docs.google.com/document/d/1N4ULftHDeAvxAVnOMAZAVdrMXDhs3ZboIkuGUmFO2u0/edit?tab=t.0#heading=h.rd7hpjfh29ai) |
| TPV for WANP (Solution Doc) | [Google Doc](https://docs.google.com/document/d/1lvw7tOELAbZXbeQM6e2of0564XkxXUJqFoHlXbvLeiU/edit?tab=t.0#heading=h.3l628bo8zl60) |
| WANP TPV Implementation Details | [Google Doc](https://docs.google.com/document/d/1kU4QA7yZpeNt6nvVOUPjx0747Kw3oqHEFTjL2Cxws-U/edit?tab=t.0#heading=h.3l628bo8zl60) |
| TPV Implementation Details | [Google Doc](https://docs.google.com/document/d/11pPELrXhjlryo76sMNWdj67uF4szw2S3q7djAw23mLc/edit?tab=t.0) |
| Meta WhatsApp Payments API | [Meta Docs](https://developers.facebook.com/documentation/business-messaging/whatsapp/payments/payments-in/pg) |

### Internal Docs (this repo)

| Doc | Path |
|-----|------|
| Payment Pages Decomp Index | `/docs/projects/payment-pages-decomp/_index.md` |
| Payment Links Decomp Index | `/docs/projects/payment-links-decomp/_index.md` |
| Payment Handles Decomp Spec | `/docs/projects/payment-handles-decomp/PaymentHandleDecomp.md` |
| Payment Buttons Decomp Spec | `/docs/projects/payment-buttons-decomp/PAYMENT_BUTTONS_DECOMP.md` |
| PP Entity Mapping | `/docs/projects/payment-pages-decomp/entity-mapping.md` |
| Coralogix Queries | `/docs/projects/payment-pages-decomp/coralogix-queries.md` |
| Deploy to Devstack | `/docs/agent-actions/deploy-to-devstack.md` |

---

## 5. Sprint Board & Tickets

### DevRev

| Resource | Link |
|----------|------|
| **No-Code Apps Feature Board** | [FEAT-262](https://app.devrev.ai/razorpay/works?applies_to_part=FEAT-262) |
| NoCodeApps Tech Initiatives | [ENH-15110](https://app.devrev.ai/razorpay/works?applies_to_part=ENH-15110) |
| NoCodeApps Decomp: Payment Handles | [ENH-10610](https://app.devrev.ai/razorpay/works?applies_to_part=ENH-10610) |

### PSE Tickets

PSE tickets are auto-created in DevRev and posted to `#tech_oncall` Slack channel, tagging `@nc-apps-pse`.

**March 2026 PSE Summary** (11 issues tagged to `@nc-apps-pse` this month):

| Date | DevRev ID | Summary | Priority | Status |
|------|-----------|---------|----------|--------|
| Mar 12 | [ISS-1688097](https://app.devrev.ai/razorpay/issue/ISS-1688097) | Payment page count mismatch — UI shows 43 payments/17,450 but actual is 42/17,100 | P2/Sev-4 | Under Investigation |
| Mar 12 | [ISS-1685493](https://app.devrev.ai/razorpay/issue/ISS-1685493) | Receipt name shows business name instead of billing label — recurring issue, needs `invoice_label_field` data-fix | P2/Sev-4 | Under Investigation |
| Mar 9 | [ISS-1669358](https://app.devrev.ai/razorpay/issue/ISS-1669358) | Thomas Cook — callback signature not sent for 3 payment links, `PAYMENT_LINK_V2_CALLBACK_GENERATED` log missing | P1/Sev-4 | Under Investigation |
| Mar 8 | — | PSE tagged (details in thread) | — | — |
| Mar 7 | — | PSE tagged (details in thread) | — | — |
| Mar 5 | — | PSE tagged (details in thread) | — | — |
| Mar 4 | — | PSE tagged (details in thread) | — | — |
| Mar 4 | — | PSE tagged (details in thread) | — | — |
| Mar 3 | — | PSE tagged (details in thread) | — | — |
| Mar 1 | — | PSE tagged (details in thread) | — | — |
| Mar 1 | — | PSE tagged (details in thread) | — | — |

**Typical volume:** ~10 PSE issues/week, 1-2 escalate to engineering. The product is old and stable.

---

## 6. Slack Channels

| Channel | Purpose |
|---------|---------|
| `#no-code-app` | Main team channel for NCA discussions |
| `#tech_oncall` | PSE tickets land here (tagged `@nc-apps-pse`) |
| `#whatsapp-payments` | WANP-specific discussions |
| `#money-saver` | Invoices team collaboration |
| `#api_decomposition` | Cross-team decomp status updates |
| `#checkout-engg` | Checkout engineering (dependencies for PL/PP) |

---

## 7. Deployment & Infrastructure

| Aspect | Status |
|--------|--------|
| **Deployment tool** | SPRE (Spinnaker) |
| **V3 (Vera) readiness** | Services are V3-ready but currently not on V3 due to a hotfix that required the normal pipeline |
| **Unit test coverage** | Good across all services |
| **SLIT (SLI/SLO/SLA)** | Still being built |
| **E2E coverage** | Lacking for most services. Payment Links has some old E2E tests (~2 years old) that need migration to `mono e2e repo` for BrowserStack compliance |

### Service URLs

| Service | Dev URL |
|---------|---------|
| NCA | `https://nca.dev.razorpay.in` |
| Payment Links | `https://payment-links.dev.razorpay.in` |
| Pages | `https://pages.dev.razorpay.in` |

---

## 8. Team & Key Contacts

| Person | Role |
|--------|------|
| **Shobhit Jain** | New portfolio owner (Low Code / No Code + Plugins) |
| **Revanth M** | Engineering lead, owns decomp execution |
| **Karthik Boddeda** | Engineer, PP/PL decomp, WANP |
| **Nikhil Musale** | Engineer, Invoices decomp |
| **Shalky Sharma** | Engineering, decomp initiatives lead |
| **Mandeep Goyat** | Engineering, Invoices/Handles decomp |
| **Tanishq Birania** | PSE on-call for NCA |
| **Ankit** | Plugins (soon to be under Shobhit) |
| **Ram Prakash** | Team member (follow-up KT planned) |
| **Yeshwanth Hali** | Team member (follow-up KT planned) |

---

## 9. Current State & Future Direction

### Current State
- Team is predominantly in **KTLO (maintenance) mode** — no new features being built apart from decomp
- Invoices product has undergone a **complete UI revamp** with the money-saver team (with Nikhil)
- Active feature development concluded ~6 months ago

### Future Plans
- **Complete all decomps** — PP (this month), Invoices (~3 months), PH/PB (in progress)
- **Revamp all existing pages** and integrate **new AI workflows** for customers
- Significant **team expansion** to 7-8 people
- Associate Director of PM being assigned
- Focus on: performance, NFRs, E2E coverage, building AI as internal capability
- Potentially **rebuild everything from scratch** after decomp completes

---

## 10. Notes on Meeting Accuracy

A few corrections/clarifications to Gemini's auto-generated notes:

1. **Invoices is a distinct product** with its own service and APIs — it is NOT just a variant of Payment Links, despite the legacy API route being `/v1/invoices` (which is actually Payment Links V1's route name, a historical naming overlap)
2. **Web Stores decomp is already 100% complete** — this was correctly noted but worth emphasizing
3. **Payment Handles and Payment Pages share 95% infrastructure** — differences are primarily UX and ~5% feature flags
4. **WANP requires a dedicated 2-hour deep dive** — not covered in this KT
