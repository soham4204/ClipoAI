import { apiClient } from './client';

// === Types ===
export interface User {
  id: string;
  email: string;
  role: string;
}

export interface Video {
  id: string;
  title: string;
  status: string;
  source_type: string;
  source_url: string | null;
  storage_path: string | null;
  created_at: string;
}

export interface Clip {
  id: string;
  video_id: string;
  title: string;
  start_time_sec: number;
  end_time_sec: number;
  viral_score: number;
  status: string;
  storage_path: string | null;
  created_at: string;
}

export interface Job {
  id: string;
  video_id: string;
  type: string;
  status: string;
  error_message: string | null;
}

// === Auth API ===
export const authApi = {
  login: async (formData: FormData) => {
    const response = await apiClient.post('/auth/login/access-token', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    return response.data; // { access_token, token_type }
  },
  signup: async (data: { email: string, password: string }) => {
    const response = await apiClient.post('/auth/signup', data);
    return response.data;
  },
  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  }
};

// === Videos API ===
export const videosApi = {
  getVideos: async (): Promise<Video[]> => {
    const response = await apiClient.get('/videos');
    return response.data;
  },
  getVideo: async (id: string): Promise<Video> => {
    const response = await apiClient.get(`/videos/${id}`);
    return response.data;
  },
  getVideoClips: async (id: string): Promise<Clip[]> => {
    const response = await apiClient.get(`/videos/${id}/clips`);
    return response.data;
  },
  getVideoJobs: async (id: string): Promise<Job[]> => {
    const response = await apiClient.get(`/videos/${id}/jobs`);
    return response.data;
  },
  uploadVideo: async (title: string, file: File): Promise<Video> => {
    const formData = new FormData();
    formData.append('title', title);
    formData.append('file', file);
    const response = await apiClient.post('/videos/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },
  deleteVideo: async (id: string) => {
    const response = await apiClient.delete(`/videos/${id}`);
    return response.data;
  }
};

// === AI Pipeline API ===
export const pipelineApi = {
  transcribe: async (videoId: string) => {
    const response = await apiClient.post(`/transcription/${videoId}`);
    return response.data;
  },
  analyze: async (videoId: string) => {
    const response = await apiClient.post(`/analysis/${videoId}`);
    return response.data;
  },
  generateClip: async (clipId: string) => {
    const response = await apiClient.post(`/clips/${clipId}/generate`);
    return response.data;
  }
};
