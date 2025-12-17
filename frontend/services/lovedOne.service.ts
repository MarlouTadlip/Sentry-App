import { coreApi } from '@/lib/api';

// Types
export interface LovedOne {
  id: number;
  user_id: number;
  loved_one: {
    id: number;
    email: string;
    username: string;
    first_name: string;
    last_name: string;
    profile_picture: string | null;
  };
  is_active: boolean;
  is_alerted: boolean;
  created_at: string;
  updated_at: string;
}

export interface LovedOneListResponse {
  message: string;
  loved_ones: LovedOne[];
  count: number;
}

export interface AddLovedOneRequest {
  loved_one_email: string;
  is_alerted?: boolean;
}

export interface LovedOneResponse {
  message: string;
  loved_one: LovedOne | null;
}

export interface UpdateLovedOneRequest {
  is_alerted?: boolean;
  is_active?: boolean;
}

export interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  profile_picture: string | null;
}

export interface UserSearchResponse {
  users: User[];
  count: number;
}

export const lovedOneService = {
  /**
   * Get all loved ones for the current user
   */
  getLovedOnes: async (): Promise<LovedOneListResponse> => {
    const response = await coreApi.get<LovedOneListResponse>('/loved-one/me');
    return response.data;
  },

  /**
   * Add a loved one contact
   */
  addLovedOne: async (email: string, isAlerted: boolean = false): Promise<LovedOneResponse> => {
    const response = await coreApi.post<LovedOneResponse>('/loved-one/', {
      loved_one_email: email,
      is_alerted: isAlerted,
    });
    return response.data;
  },

  /**
   * Delete a loved one relationship
   */
  deleteLovedOne: async (lovedOneId: number): Promise<{ message: string }> => {
    const response = await coreApi.delete<{ message: string }>(`/loved-one/${lovedOneId}`);
    return response.data;
  },

  /**
   * Update loved one settings
   */
  updateLovedOne: async (
    lovedOneId: number,
    updates: UpdateLovedOneRequest
  ): Promise<LovedOneResponse> => {
    const response = await coreApi.patch<LovedOneResponse>(`/loved-one/${lovedOneId}`, updates);
    return response.data;
  },

  /**
   * Toggle is_alerted status for a loved one
   */
  toggleLovedOneAlerted: async (lovedOneId: number): Promise<LovedOneResponse> => {
    const response = await coreApi.post<LovedOneResponse>(
      `/loved-one/${lovedOneId}/toggle-alerted`
    );
    return response.data;
  },

  /**
   * Search for users by email, username, first name, or last name
   */
  searchUsers: async (query: string, limit: number = 10): Promise<UserSearchResponse> => {
    const response = await coreApi.get<UserSearchResponse>('/user/search', {
      params: { q: query, limit },
    });
    return response.data;
  },
};

