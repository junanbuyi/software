import apiClient from "./client";
import type { Paginated } from "./types";

export type Ranking = {
  id: number;
  score: number;
  time_range: string;
  mae_ratio: number;
  rmse_ratio: number;
  rank_type: string;
  weather: string;
  is_holiday: boolean;
  model_name: string;
  author: string;
  plan_id?: number | null;
  created_at: string;
};

export type RankingQuery = {
  page?: number;
  size?: number;
  rank_type?: string;
  weather?: string;
  is_holiday?: boolean;
  model_name?: string;
};

export const fetchRankings = async (query: RankingQuery = {}) => {
  const { data } = await apiClient.get<Paginated<Ranking>>("/rankings", { params: query });
  return data;
};

