import apiClient from "./client";
import type { Paginated } from "./types";

export type Model = {
  id: number;
  name: string;
  description?: string | null;
  file_path: string;
  original_name: string;
  dataset_id: number;
  train_start_date: string;
  train_end_date: string;
  prediction_type: "day_ahead" | "week_ahead";
  status: "untrained" | "trained";
  trained_at?: string | null;
  created_at: string;
  updated_at: string;
};

export type ModelsQuery = {
  page?: number;
  size?: number;
  keyword?: string;
  status?: string;
};

export const fetchModels = async (query: ModelsQuery = {}) => {
  const { data } = await apiClient.get<Paginated<Model>>("/models", { params: query });
  return data;
};

export const uploadModel = async (formData: FormData) => {
  const { data } = await apiClient.post<Model>("/models/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
};

export const trainModel = async (modelId: number) => {
  const { data } = await apiClient.post<{ id: number; status: string; trained_at: string; message: string }>(
    `/models/${modelId}/train`
  );
  return data;
};

export const deleteModel = async (modelId: number) => {
  await apiClient.delete(`/models/${modelId}`);
};
