<script lang="ts">
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import { authStore } from "$lib/stores/auth";
    import { getMyJobs, deleteJob } from "$lib/api/jobs";
    import { UserRole, type Job } from "$lib/api/types";
    import { toastStore } from "$lib/stores/toast";

    let jobs: Job[] = [];
    let loading = true;

    onMount(async () => {
        if (
            !$authStore.isAuthenticated ||
            $authStore.user?.role !== UserRole.EMPLOYER
        ) {
            goto("/login");
            return;
        }

        await loadJobs();
    });

    async function loadJobs() {
        try {
            const response = await getMyJobs();
            jobs = response.Data || [];
        } catch (err: any) {
            toastStore.show("error", "Failed to load jobs");
        } finally {
            loading = false;
        }
    }

    async function handleDelete(jobId: string) {
        if (!confirm("Are you sure you want to delete this job posting?")) {
            return;
        }

        try {
            await deleteJob(jobId);
            jobs = jobs.filter((j) => j.job_id !== jobId);
            toastStore.show("success", "Job deleted successfully");
        } catch (err: any) {
            toastStore.show("error", "Failed to delete job");
        }
    }
</script>

<svelte:head>
    <title>My Jobs - JobCompanion AI</title>
</svelte:head>

<div class="space-y-6">
    <div class="flex items-center justify-between">
        <div>
            <h1 class="text-3xl font-bold text-gray-900">My Job Postings</h1>
            <p class="text-gray-600 mt-1">Manage and track your job listings</p>
        </div>
        <button
            on:click={() => goto("/employer/jobs/post")}
            class="btn btn-primary"
        >
            <svg
                class="w-5 h-5 inline mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
            >
                <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 4v16m8-8H4"
                />
            </svg>
            Post New Job
        </button>
    </div>

    {#if loading}
        <div class="flex items-center justify-center py-12">
            <div class="text-center">
                <div
                    class="w-16 h-16 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"
                ></div>
                <p class="text-gray-600">Loading your jobs...</p>
            </div>
        </div>
    {:else if jobs.length > 0}
        <div class="grid gap-4">
            {#each jobs as job}
                <div class="card hover:shadow-md transition-shadow">
                    <div class="flex justify-between items-start">
                        <div class="flex-1">
                            <div class="flex items-start justify-between mb-3">
                                <div>
                                    <h3
                                        class="text-xl font-semibold text-gray-900"
                                    >
                                        {job.title}
                                    </h3>
                                    <div
                                        class="flex items-center gap-4 text-sm text-gray-600 mt-2"
                                    >
                                        <span class="flex items-center gap-1">
                                            <svg
                                                class="w-4 h-4"
                                                fill="none"
                                                stroke="currentColor"
                                                viewBox="0 0 24 24"
                                            >
                                                <path
                                                    stroke-linecap="round"
                                                    stroke-linejoin="round"
                                                    stroke-width="2"
                                                    d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                                                />
                                            </svg>
                                            {job.location}
                                        </span>
                                        <span
                                            class="px-2 py-1 bg-primary-100 text-primary-700 text-xs rounded-full"
                                        >
                                            {job.job_type.replace("_", " ")}
                                        </span>
                                        <span class="text-xs text-gray-500">
                                            Posted {new Date(
                                                job.created_at,
                                            ).toLocaleDateString()}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            <p class="text-gray-600 text-sm mb-3 line-clamp-2">
                                {job.description}
                            </p>

                            <div class="flex flex-wrap gap-2 mb-4">
                                {#each job.required_skills.slice(0, 5) as skill}
                                    <span
                                        class="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-md"
                                        >{skill}</span
                                    >
                                {/each}
                                {#if job.required_skills.length > 5}
                                    <span
                                        class="px-2 py-1 bg-gray-100 text-gray-500 text-xs rounded-md"
                                    >
                                        +{job.required_skills.length - 5} more
                                    </span>
                                {/if}
                            </div>

                            <div
                                class="flex items-center justify-between mt-6 pt-4 border-t border-gray-50"
                            >
                                <div class="flex gap-4">
                                    <button
                                        on:click={() =>
                                            goto(
                                                `/employer/jobs/${job.job_id}/edit`,
                                            )}
                                        class="text-primary-600 hover:text-primary-700 font-medium text-sm flex items-center gap-1"
                                    >
                                        <svg
                                            class="w-4 h-4"
                                            fill="none"
                                            stroke="currentColor"
                                            viewBox="0 0 24 24"
                                        >
                                            <path
                                                stroke-linecap="round"
                                                stroke-linejoin="round"
                                                stroke-width="2"
                                                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                                            />
                                        </svg>
                                        Edit
                                    </button>
                                    <button
                                        on:click={() =>
                                            goto(
                                                `/candidate/jobs/${job.job_id}`,
                                            )}
                                        class="text-gray-600 hover:text-gray-700 font-medium text-sm flex items-center gap-1"
                                    >
                                        <svg
                                            class="w-4 h-4"
                                            fill="none"
                                            stroke="currentColor"
                                            viewBox="0 0 24 24"
                                        >
                                            <path
                                                stroke-linecap="round"
                                                stroke-linejoin="round"
                                                stroke-width="2"
                                                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                                            />
                                            <path
                                                stroke-linecap="round"
                                                stroke-linejoin="round"
                                                stroke-width="2"
                                                d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                                            />
                                        </svg>
                                        View
                                    </button>
                                    <button
                                        on:click={() =>
                                            handleDelete(job.job_id)}
                                        class="text-red-600 hover:text-red-700 font-medium text-sm flex items-center gap-1"
                                    >
                                        <svg
                                            class="w-4 h-4"
                                            fill="none"
                                            stroke="currentColor"
                                            viewBox="0 0 24 24"
                                        >
                                            <path
                                                stroke-linecap="round"
                                                stroke-linejoin="round"
                                                stroke-width="2"
                                                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                                            />
                                        </svg>
                                        Delete
                                    </button>
                                </div>
                                <button
                                    on:click={() =>
                                        goto(
                                            `/employer/jobs/${job.job_id}/candidates`,
                                        )}
                                    class="btn btn-secondary py-1.5 px-4 text-sm font-bold flex items-center gap-2"
                                >
                                    <svg
                                        class="w-4 h-4"
                                        fill="none"
                                        stroke="currentColor"
                                        viewBox="0 0 24 24"
                                    >
                                        <path
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                            stroke-width="2"
                                            d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                                        />
                                    </svg>
                                    View Best Candidates
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            {/each}
        </div>
    {:else}
        <div class="card text-center py-12">
            <div
                class="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4"
            >
                <svg
                    class="w-10 h-10 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                    />
                </svg>
            </div>
            <h3 class="text-xl font-semibold text-gray-900 mb-2">
                No jobs posted yet
            </h3>
            <p class="text-gray-600 mb-6">
                Start finding talent by posting your first job
            </p>
            <button
                on:click={() => goto("/employer/jobs/post")}
                class="btn btn-primary"
            >
                Post Your First Job
            </button>
        </div>
    {/if}
</div>
