# Future SaaS Feature Roadmap

This document outlines the next-phase features and architecture improvements to move the budget tracker from a prototype backend into a SaaS-ready service.

## Core product capabilities

1. Multi-account support
   - User-owned accounts with OAuth or secure bank API connectors.
   - Per-user account linking and account metadata.
   - Account-level transaction ingestion and reconciliation.

2. Personal budgets and goals
   - Budget definitions by category and period.
   - Budget item targets and alerts for overspending.
   - Goal tracking for savings, debt paydown, or expense reduction.

3. Rich reporting and analytics
   - Monthly and category summaries with trends.
   - Forecasting and burn-rate projections.
   - Export reports as CSV/JSON.

4. Onboarding and import automation
   - Scheduled imports from connected accounts.
   - Google Sheets sync jobs and bank CSV import as fallback.
   - Automatic categorization with rule learning.

5. User management and subscriptions
   - Authentication, authorization, and user profiles.
   - Organization/team accounts and shared budgets.
   - Subscription tier gating for premium features.

## SaaS platform priorities

1. Authentication and identity
   - Add sign-up/login flows.
   - Support OAuth providers and email/password.
   - Implement account-level isolation and permissions.

2. Security and compliance
   - Audit logging for sensitive actions.
   - Rate limiting and request throttling.
   - Secrets management for bank/API credentials.
   - Secure storage of financial data.

3. Scalability and operational readiness
   - Move from SQLite to PostgreSQL or managed DB.
   - Add caching for repeated summary queries.
   - Separate worker service for imports and summary refresh.
   - Add observability: metrics, logs, and health checks.

4. Integration ecosystem
   - Bank API connectors (Plaid, Yodlee, or direct bank APIs).
   - Spreadsheet connectors beyond Google Sheets.
   - Webhook or webhook-like callback support.

## Short-term product roadmap

- [ ] Add user/auth layer and session management
- [ ] Migrate to PostgreSQL and support multi-tenant data isolation
- [ ] Expand import connectors and bank account mapping
- [ ] Add budgets and goals tables + API endpoints
- [ ] Build an admin dashboard for data review and support

## Recommended next development slices

1. `auth/identity`
   - Add user model, JWT auth, and login/signup flows.
   - Protect API endpoints behind authenticated sessions.

2. `finance/import`
   - Add a generic import service that selects connectors by source.
   - Persist account metadata and normalize transaction sources.

3. `budgeting`
   - Add budget CRUD and attach budgets to categories.
   - Add alerts or weekly summary email generation.

4. `operations`
   - Add deployment docs for cloud DB, scheduler, and worker.
   - Add monitoring and healthcheck endpoints.

## Why this roadmap matters

The current codebase is a strong MVP for internal automation, but SaaS success depends on:

- secure user isolation,
- predictable repeatable imports,
- extensible connector architecture,
- and clear multi-tenant application boundaries.

This roadmap keeps the current backend stable while laying the foundation for those capabilities.
