Parity Matrix — External Web-App → RiskRadar Backend
====================================================

This matrix maps external web-app features to RiskRadar API contracts. CI checks should ensure entries exist for any new or changed endpoint.

| External Feature | RiskRadar Endpoint | Notes |
|------------------|--------------------|-------|
| Golby Assistant (chat/onboard) | `/api/v1/assistant/*` | Centralized assistant contracts in backend
| Crime & Safety (incidents) | `/api/v1/trips/{id}/safety` | Trip-scoped incident queries, route overlays
| Food / Places | `/api/v1/trips/{id}/places` | Places, cuisine/diet filters, review signals
| Lodging / Hotels | `/api/v1/trips/{id}/lodging` | Lodging results with safety-aware ranking

Keep this file updated for any parity work. The CI validator (`tools/validate_parity_matrix.py`) verifies presence of the three core entries above.
