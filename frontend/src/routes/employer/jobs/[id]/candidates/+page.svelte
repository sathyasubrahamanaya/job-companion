<script lang="ts">
    import { onMount } from "svelte";
    import { page } from "$app/stores";
    import { goto } from "$app/navigation";
    import { authStore } from "$lib/stores/auth";
    import { getPotentialCandidates } from "$lib/api/employer";
    import { getJobDetails } from "$lib/api/jobs";
    import {
        UserRole,
        type PotentialCandidate,
        type Job,
    } from "$lib/api/types";
    import { toastStore } from "$lib/stores/toast";
    import CandidateCard from "$lib/components/CandidateCard.svelte";

    let candidates: PotentialCandidate[] = [];
    let job: Job | null = null;
    let loading = true;
    let error = "";

    $: jobId = $page.params.id;

    onMount(async () => {
        if (
            !$authStore.isAuthenticated ||
            $authStore.user?.role !== UserRole.EMPLOYER
        ) {
            goto("/login");
            return;
        }

        try {
            const [jobRes, candidatesRes] = await Promise.all([
                getJobDetails(jobId),
                getPotentialCandidates(jobId),
            ]);

            if (jobRes.ErrorCode === 0) job = jobRes.Data;
            if (candidatesRes.ErrorCode === 0)
                candidates = candidatesRes.Data || [];
        } catch (err: any) {
            error = "Failed to load potential candidates.";
            toastStore.show("error", error);
        } finally {
            loading = false;
        }
    });
</script>

<svelte:head>
    <title>Potential Candidates - JobCompanion AI</title>
</svelte:head>

<div class="space-y-6">
    <div class="flex items-center gap-4">
        <button
            on:click={() => goto("/employer/jobs")}
            class="text-primary-600 hover:text-primary-700 flex items-center gap-1"
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
            Back to Jobs
        </button>
    </div>

    {#if loading}
        <div class="flex items-center justify-center py-20">
            <div class="text-center">
                <div
                    class="w-16 h-16 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"
                ></div>
                <p class="text-gray-600 text-lg">
                    AI is finding the best matches for your job...
                </p>
            </div>
        </div>
    {:else if error}
        <div class="card p-12 text-center bg-red-50 border-red-100">
            <h2 class="text-xl font-bold text-red-800 mb-2">
                Error Loading Candidates
            </h2>
            <p class="text-red-700">{error}</p>
            <button
                on:click={() => window.location.reload()}
                class="btn btn-primary mt-6">Try Again</button
            >
        </div>
    {:else}
        <div>
            <div class="mb-8">
                <h1 class="text-3xl font-bold text-gray-900">
                    Potential Candidates
                </h1>
                {#if job}
                    <p class="text-gray-600 mt-2">
                        AI Matched candidates for <span
                            class="font-semibold text-primary-700"
                            >{job.title}</span
                        >
                    </p>
                {/if}
            </div>

            {#if candidates.length > 0}
                <div class="grid gap-6">
                    {#each candidates as candidate}
                        <CandidateCard {candidate} {jobId} />
                    {/each}
                </div>
            {:else}
                <div class="card text-center py-20">
                    <div
                        class="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6"
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
                                d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
                            />
                        </svg>
                    </div>
                    <h3 class="text-2xl font-bold text-gray-900 mb-2">
                        No matches found yet
                    </h3>
                    <p class="text-gray-600 max-w-md mx-auto">
                        We couldn't find any candidates that match your job
                        requirements. Try refreshing later as new candidates
                        join.
                    </p>
                </div>
            {/if}
        </div>
    {/if}
</div>
