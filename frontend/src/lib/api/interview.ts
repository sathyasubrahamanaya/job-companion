import apiClient from './client';
import type { APIResponse } from './types';

export async function startInterview(jobId: string): Promise<APIResponse<{ session_id: string }>> {
    const response = await apiClient.post<APIResponse<{ session_id: string }>>(
        `/api/v1/interview/start/${jobId}`
    );
    return response.data;
}

export async function chatInteraction(
    sessionId: string,
    userMessage: string
): Promise<APIResponse<{ response: string }>> {
    const response = await apiClient.post<APIResponse<{ response: string }>>(
        `/api/v1/interview/chat/${sessionId}`,
        { user_message: userMessage }
    );
    return response.data;
}
