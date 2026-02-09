<script lang="ts">
    import { onMount } from "svelte";
    import { page } from "$app/stores";
    import { goto } from "$app/navigation";
    import { authStore } from "$lib/stores/auth";
    import { getJobDetails } from "$lib/api/jobs";
    import { startInterview } from "$lib/api/interview";
    import { UserRole, type Job, type Notification } from "$lib/api/types";
    import { toastStore } from "$lib/stores/toast";
    import { getNotifications } from "$lib/api/candidate";

    let job: Job | null = null;
    let notifications: Notification[] = [];
    let loading = true;
    let startingInterview = false;
    let isInvited = false;

    $: jobId = $page.params.id as string;

    onMount(async () => {
        if (!$authStore.isAuthenticated) {
            goto("/login");
            return;
        }

        try {
            const [jobRes, notifyRes] = await Promise.all([
                getJobDetails(jobId),
                getNotifications(),
            ]);

            job = jobRes.Data;

            if (notifyRes.ErrorCode === 0) {
                notifications = notifyRes.Data || [];
                isInvited = notifications.some(
                    (n) => n.job_id === jobId && n.type === "INVITE",
                );
            }
        } catch (err: any) {
            toastStore.show("error", "Failed to load job details");
        } finally {
            loading = false;
        }
    });

    async function handleStartInterview() {
        if (!job) return;

        startingInterview = true;
        try {
            const response = await startInterview(job.job_id);
            const sessionId = response.Data?.session_id;
            toastStore.show("success", "Interview started!");
            goto(`/candidate/interview/${sessionId}`);
        } catch (err: any) {
            toastStore.show("error", "Failed to start interview");
        } finally {
            startingInterview = false;
        }
    }
</script>

<svelte:head>
    <title>{job?.title || "Job Details"} - JobCompanion AI</title>
</svelte:head>

{#if loading}
    <div class="flex items-center justify-center min-h-[60vh]">
        <div class="text-center">
            <div
                class="w-16 h-16 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"
            ></div>
            <p class="text-gray-600">Loading job details...</p>
        </div>
    </div>
{:else if job}
    <div class="max-w-4xl mx-auto space-y-6">
        <button
            on:click={() => goto("/candidate/jobs/search")}
            class="text-primary-600 hover:text-primary-700 flex items-center gap-2 mb-4"
        >
            <svg
                class="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
            >
                <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M15 19l-7-7 7-7"
                />
            </svg>
            Back to search
        </button>

        {#if isInvited}
            <div
                class="card bg-gradient-to-r from-secondary-600 to-primary-600 text-white p-6 shadow-xl border-none"
            >
                <div class="flex items-center gap-4">
                    <div class="p-3 bg-white/20 rounded-full">
                        <svg
                            class="w-8 h-8"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z"
                            />
                        </svg>
                    </div>
                    <div>
                        <h2 class="text-xl font-bold">You're Invited!</h2>
                        <p class="text-white/90">
                            The employer has personally invited you to interview
                            for this position. Start your AI interview below to
                            proceed.
                        </p>
                    </div>
                </div>
            </div>
        {/if}

        <div class="card">
            <div class="flex justify-between items-start mb-6">
                <div>
                    <h1 class="text-3xl font-bold text-gray-900 mb-2">
                        {job.title}
                    </h1>
                    <div class="flex items-center gap-4 text-gray-600">
                        <span class="flex items-center gap-1">
                            <svg
                                class="w-5 h-5"
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
                        <span class="flex items-center gap-1">
                            <svg
                                class="w-5 h-5"
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
                            {job.experience_required} years experience
                        </span>
                    </div>
                </div>
                <span
                    class="px-4 py-2 bg-primary-100 text-primary-700 font-semibold rounded-full"
                >
                    {job.job_type.replace("_", " ")}
                </span>
            </div>

            {#if job.salary_range}
                <div
                    class="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg"
                >
                    <p class="text-sm text-green-700 font-medium">
                        Salary Range
                    </p>
                    <p class="text-xl font-bold text-green-900">
                        {job.salary_range}
                    </p>
                </div>
            {/if}

            <div class="mb-6">
                <h2 class="text-xl font-semibold text-gray-900 mb-3">
                    Job Description
                </h2>
                <p class="text-gray-700 whitespace-pre-line">
                    {job.description}
                </p>
            </div>

            <div class="mb-6">
                <h2 class="text-xl font-semibold text-gray-900 mb-3">
                    Required Skills
                </h2>
                <div class="flex flex-wrap gap-2">
                    {#each job.required_skills as skill}
                        <span
                            class="px-3 py-2 bg-primary-100 text-primary-700 rounded-lg font-medium"
                            >{skill}</span
                        >
                    {/each}
                </div>
            </div>

            {#if $authStore.user?.role === UserRole.CANDIDATE}
                <div class="pt-6 border-t border-gray-200">
                    <button
                        on:click={handleStartInterview}
                        class="btn btn-primary px-8 py-3"
                        disabled={startingInterview}
                    >
                        {startingInterview
                            ? "Starting Interview..."
                            : "Start AI Interview"}
                    </button>
                    <p class="text-sm text-gray-500 mt-3">
                        Practice your interview skills with our AI interviewer
                        before applying
                    </p>
                </div>
            {/if}
        </div>
    </div>
{:else}
    <div class="card text-center py-12">
        <h2 class="text-2xl font-semibold text-gray-900 mb-2">Job not found</h2>
        <p class="text-gray-600 mb-6">
            The job you're looking for doesn't exist or has been removed
        </p>
        <button
            on:click={() => goto("/candidate/jobs/search")}
            class="btn btn-primary"
        >
            Browse Jobs
        </button>
    </div>
{/if}
