import apiClient from "./client";

export type AdminProfile = {
  id: number;
  username: string;
  display_name: string;
  created_at: string;
  updated_at: string;
};

export type AdminUpdatePayload = {
  username: string;
  display_name: string;
};

export type PasswordUpdatePayload = {
  current_password: string;
  new_password: string;
};

export const fetchProfile = async () => {
  const { data } = await apiClient.get<AdminProfile>("/admin/me");
  return data;
};

export const updateProfile = async (payload: AdminUpdatePayload) => {
  const { data } = await apiClient.put<AdminProfile>("/admin/me", payload);
  return data;
};

export const updatePassword = async (payload: PasswordUpdatePayload) => {
  const { data } = await apiClient.put<{ message: string }>("/admin/me/password", payload);
  return data;
};

