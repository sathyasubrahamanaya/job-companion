import apiClient from './client';
import type {
    APIResponse,
    CandidateProfile,
    User,
    CandidateSignupForm,
    SearchJobsRequest,
    Job,
    Notification
} from './types';

export async function candidateSignup(formData: CandidateSignupForm): Promise<APIResponse<{ user_id: string; email: string }>> {
    const data = new FormData();
    data.append('name', formData.name);
    data.append('email', formData.email);
    data.append('password', formData.password);
    data.append('file', formData.file);

    const response = await apiClient.post<APIResponse<{ user_id: string; email: string }>>(
        '/api/v1/candidate/signup',
        data,
        {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        }
    );
    return response.data;
}

export async function getCandidateProfile(): Promise<APIResponse<{ user: User; profile: CandidateProfile }>> {
    const response = await apiClient.get<APIResponse<{ user: User; profile: CandidateProfile }>>(
        '/api/v1/candidate/profile'
    );
    return response.data;
}

export async function updateResume(file: File): Promise<APIResponse<null>> {
    const data = new FormData();
    data.append('file', file);

    const response = await apiClient.put<APIResponse<null>>(
        '/api/v1/candidate/update-resume',
        data,
        {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        }
    );
    return response.data;
}

export async function searchJobs(request: SearchJobsRequest): Promise<APIResponse<Job[]>> {
    const params = new URLSearchParams();
    params.append('query', request.query);
    params.append('limit', request.limit?.toString() || '10');

    const response = await apiClient.post<APIResponse<Job[]>>(
        '/api/v1/candidate/search-jobs',
        params.toString(),  // ← Changed from 'params' to 'params.toString()'
        {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        }
    );
    return response.data;
}

export async function getNotifications(): Promise<APIResponse<Notification[]>> {
    const res = await apiClient.get('/api/v1/candidate/notifications');
    return res.data;
}

export async function markNotificationRead(id: string): Promise<APIResponse<void>> {
    const res = await apiClient.put(`/api/v1/candidate/notifications/${id}/read`);
    return res.data;
}

export async function acceptInvitation(id: string): Promise<APIResponse<void>> {
    const res = await apiClient.put(`/api/v1/candidate/notifications/${id}/accept`);
    return res.data;
}

export async function rejectInvitation(id: string): Promise<APIResponse<void>> {
    const res = await apiClient.put(`/api/v1/candidate/notifications/${id}/reject`);
    return res.data;
}

export async function updateCandidateMemo(id: string, memo: string): Promise<APIResponse<void>> {
    const res = await apiClient.put(`/api/v1/candidate/notifications/${id}/memo`, { memo });
    return res.data;
}
