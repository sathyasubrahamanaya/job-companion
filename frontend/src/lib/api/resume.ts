import apiClient from "./client";
import type { APIResponse, ResumeInput, ResumeData, ResumeBuildResponse } from "./types";

/**
 * Sends raw form data to the AI agent to be polished.
 * Returns polished JSON and an HTML preview.
 */
export async function buildResume(data: ResumeInput): Promise<APIResponse<ResumeBuildResponse>> {
    const res = await apiClient.post<APIResponse<ResumeBuildResponse>>("/api/v1/resume/build", data);
    return res.data;
}

/**
 * Downloads the polished resume as a PDF.
 * Uses template parameter to choose the visual style.
 */
export async function downloadResumePdf(data: ResumeData, template: string = "classic") {
    const response = await apiClient.post(`/api/v1/resume/download-pdf?template=${template}`, data, {
        responseType: 'blob'
    });

    // Create a link to download the blob
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;

    const fileName = `${data.full_name.replace(/\s+/g, '_')}_Resume_${template}.pdf`;
    link.setAttribute('download', fileName);

    document.body.appendChild(link);
    link.click();

    // Cleanup
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
}
