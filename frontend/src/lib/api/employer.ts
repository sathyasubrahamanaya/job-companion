import apiClient from './client';
import type {
    APIResponse,
    EmployerProfile,
    User,
    EmployerSignupForm,
    EmployerOnboardForm,
    SearchCandidatesRequest,
    CandidateProfile,
    PotentialCandidate
} from './types';

export async function employerSignup(formData: EmployerSignupForm): Promise<APIResponse<{ user_id: string; email: string }>> {
    const data = new URLSearchParams();
    data.append('name', formData.name);
    data.append('email', formData.email);
    data.append('password', formData.password);

    const response = await apiClient.post<APIResponse<{ user_id: string; email: string }>>(
        '/api/v1/employer/signup',
        data,
        {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        }
    );
    return response.data;
}

export async function onboardEmployer(formData: EmployerOnboardForm): Promise<APIResponse<{ employer_id: string }>> {
    const response = await apiClient.post<APIResponse<{ employer_id: string }>>(
        '/api/v1/employer/onboard',
        formData
    );
    return response.data;
}

export async function getEmployerProfile(): Promise<APIResponse<{ user: User; profile: EmployerProfile }>> {
    const response = await apiClient.get<APIResponse<{ user: User; profile: EmployerProfile }>>(
        '/api/v1/employer/profile'
    );
    return response.data;
}

export async function updateEmployerProfile(
    updates: Partial<EmployerOnboardForm>
): Promise<APIResponse<{ user: User; profile: EmployerProfile }>> {
    const response = await apiClient.put<APIResponse<{ user: User; profile: EmployerProfile }>>(
        '/api/v1/employer/update',
        updates
    );
    return response.data;
}

export async function deleteEmployerAccount(): Promise<APIResponse<null>> {
    const response = await apiClient.delete<APIResponse<null>>('/api/v1/employer/delete');
    return response.data;
}

export async function searchCandidates(request: SearchCandidatesRequest): Promise<APIResponse<CandidateProfile[]>> {
    const data = new URLSearchParams();
    data.append('query', request.query);
    data.append('limit', (request.limit || 10).toString());

    const response = await apiClient.post<APIResponse<CandidateProfile[]>>(
        '/api/v1/employer/search-candidates',
        data,
        {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        }
    );
    return response.data;
}

export async function getPotentialCandidates(jobId: string, limit: number = 10): Promise<APIResponse<PotentialCandidate[]>> {
    const response = await apiClient.get<APIResponse<PotentialCandidate[]>>(
        `/api/v1/employer/potential-candidates/${jobId}`,
        { params: { limit } }
    );
    return response.data;
}

export async function inviteCandidate(candidateId: string, jobId: string): Promise<APIResponse<null>> {
    const response = await apiClient.post<APIResponse<null>>(
        `/api/v1/employer/invite/${candidateId}/${jobId}`
    );
    return response.data;
}

export function getResumeUrl(candidateId: string): string {
    return `${apiClient.defaults.baseURL}/api/v1/employer/resume/${candidateId}`;
}

export async function remindCandidate(candidateId: string, jobId: string): Promise<APIResponse<null>> {
    const response = await apiClient.post<APIResponse<null>>(
        `/api/v1/employer/remind/${candidateId}/${jobId}`
    );
    return response.data;
}

export async function updateEmployerMemo(invitationId: string, memo: string): Promise<APIResponse<void>> {
    const res = await apiClient.put(`/api/v1/employer/notifications/${invitationId}/memo`, { memo });
    return res.data;
}
