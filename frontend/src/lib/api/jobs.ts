import apiClient from './client';
import type { APIResponse, Job, JobPostForm, JobUpdateForm } from './types';

export async function postJob(formData: JobPostForm): Promise<APIResponse<{ job_id: string; title: string }>> {
    const response = await apiClient.post<APIResponse<{ job_id: string; title: string }>>(
        '/api/v1/jobs/post',
        formData
    );
    return response.data;
}

export async function getMyJobs(): Promise<APIResponse<Job[]>> {
    const response = await apiClient.get<APIResponse<Job[]>>('/api/v1/jobs/my-jobs');
    return response.data;
}

export async function getAllJobs(): Promise<APIResponse<Job[]>> {
    const response = await apiClient.get<APIResponse<Job[]>>('/api/v1/jobs/all');
    return response.data;
}

export async function getJobDetails(jobId: string): Promise<APIResponse<Job>> {
    const response = await apiClient.get<APIResponse<Job>>(`/api/v1/jobs/${jobId}`);
    return response.data;
}

export async function updateJob(jobId: string, updates: JobUpdateForm): Promise<APIResponse<Job>> {
    const response = await apiClient.put<APIResponse<Job>>(`/api/v1/jobs/update/${jobId}`, updates);
    return response.data;
}

export async function deleteJob(jobId: string): Promise<APIResponse<null>> {
    const response = await apiClient.delete<APIResponse<null>>(`/api/v1/jobs/delete/${jobId}`);
    return response.data;
}
