import apiClient from "./client";
import type { Paginated } from "./types";

export type Plan = {
  id: number;
  name: string;
  plan_type: string;
  dataset_id?: number | null;
  status: string;
  description?: string | null;
  created_by: number;
  created_at: string;
  updated_at: string;
};

export type PlanResult = {
  id: number;
  plan_id: number;
  model_name: string;
  weather: string;
  mae: number;
  nmae: number;
  rmse: number;
  nrmse: number;
  score: number;
};

export type PlansQuery = {
  page?: number;
  size?: number;
  keyword?: string;
};

export const fetchPlans = async (query: PlansQuery = {}) => {
  const { data } = await apiClient.get<Paginated<Plan>>("/plans", { params: query });
  return data;
};

export const fetchPlan = async (planId: number) => {
  const { data } = await apiClient.get<Plan>(`/plans/${planId}`);
  return data;
};

export const updatePlan = async (planId: number, payload: Partial<Plan>) => {
  const { data } = await apiClient.put<Plan>(`/plans/${planId}`, payload);
  return data;
};

export const deletePlan = async (planId: number) => {
  const { data } = await apiClient.delete<{ message: string }>(`/plans/${planId}`);
  return data;
};

export const fetchPlanResults = async (planId: number) => {
  const { data } = await apiClient.get<PlanResult[]>(`/plans/${planId}/results`);
  return data;
};

