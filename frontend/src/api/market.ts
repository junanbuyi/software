import apiClient from "./client";

export const marketApi = {
  getCompanies: () => apiClient.get("/market/companies"),
  getWindUnits: () => apiClient.get("/market/wind-units"),
  getSolarUnits: () => apiClient.get("/market/solar-units"),
  getClearingHistory: (params?: { metric?: string; start?: number; limit?: number }) =>
    apiClient.get("/market/clearing-history", { params }),
  getOutResults: (params: { sheet: string; row_index?: number }) =>
    apiClient.get("/market/out-results", { params }),
  getDayAheadQuotes: (params?: { unit_id?: string }) =>
    apiClient.get("/market/day-ahead-quotes", { params }),
  getSettlementOverview: () => apiClient.get("/market/settlement-overview"),
  getSettlementDetail: () => apiClient.get("/market/settlement-detail"),
  getBalanceChart: () => apiClient.get("/market/balance-chart"),
};
