<script lang="ts">
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import { authStore } from "$lib/stores/auth";
    import { getAllJobs } from "$lib/api/jobs";
    import type { Job } from "$lib/api/types";
    import { toastStore } from "$lib/stores/toast";
    import JobCard from "$lib/components/JobCard.svelte";

    let jobs: Job[] = [];
    let loading = true;
    let filteredJobs: Job[] = [];
    let searchTerm = "";
    let selectedJobType = "all";

    onMount(async () => {
        if (!$authStore.isAuthenticated) {
            goto("/login");
            return;
        }

        await loadJobs();
    });

    async function loadJobs() {
        try {
            const response = await getAllJobs();
            jobs = response.Data || [];
            filteredJobs = jobs;
        } catch (err: any) {
            toastStore.show("error", "Failed to load jobs");
        } finally {
            loading = false;
        }
    }

    function viewJobDetails(jobId: string) {
        goto(`/candidate/jobs/${jobId}`);
    }

    $: {
        // Filter jobs based on search term and job type
        filteredJobs = jobs.filter((job) => {
            const matchesSearch =
                searchTerm === "" ||
                job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                job.description
                    .toLowerCase()
                    .includes(searchTerm.toLowerCase()) ||
                job.required_skills.some((skill) =>
                    skill.toLowerCase().includes(searchTerm.toLowerCase()),
                ) ||
                job.location.toLowerCase().includes(searchTerm.toLowerCase());

            const matchesType =
                selectedJobType === "all" || job.job_type === selectedJobType;

            return matchesSearch && matchesType;
        });
    }
</script>

<svelte:head>
    <title>Browse All Jobs - JobCompanion AI</title>
</svelte:head>

<div class="space-y-6">
    <div>
        <h1 class="text-3xl font-bold text-gray-900">Browse All Jobs</h1>
        <p class="text-gray-600 mt-1">
            Explore all available opportunities on our platform
        </p>
    </div>

    <!-- Filters -->
    <div class="card">
        <div class="grid md:grid-cols-2 gap-4">
            <div>
                <label for="search" class="label">Search</label>
                <input
                    id="search"
                    type="text"
                    bind:value={searchTerm}
                    placeholder="Search by title, skills, location..."
                    class="input"
                />
            </div>
            <div>
                <label for="jobType" class="label">Job Type</label>
                <select id="jobType" bind:value={selectedJobType} class="input">
                    <option value="all">All Types</option>
                    <option value="FULL_TIME">Full Time</option>
                    <option value="PART_TIME">Part Time</option>
                    <option value="INTERNSHIP">Internship</option>
                </select>
            </div>
        </div>
    </div>

    <!-- Results -->
    {#if loading}
        <div class="flex items-center justify-center py-12">
            <div class="text-center">
                <div
                    class="w-16 h-16 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"
                ></div>
                <p class="text-gray-600">Loading jobs...</p>
            </div>
        </div>
    {:else if filteredJobs.length > 0}
        <div>
            <div class="flex items-center justify-between mb-4">
                <h2 class="text-xl font-semibold text-gray-900">
                    {filteredJobs.length}
                    {filteredJobs.length === 1 ? "job" : "jobs"} found
                </h2>
                {#if searchTerm || selectedJobType !== "all"}
                    <button
                        on:click={() => {
                            searchTerm = "";
                            selectedJobType = "all";
                        }}
                        class="text-primary-600 hover:text-primary-700 text-sm font-medium"
                    >
                        Clear filters
                    </button>
                {/if}
            </div>
            <div class="grid gap-4">
                {#each filteredJobs as job}
                    <JobCard {job} onClick={() => viewJobDetails(job.job_id)} />
                {/each}
            </div>
        </div>
    {:else if jobs.length === 0}
        <div class="card text-center py-12">
            <svg
                class="w-16 h-16 text-gray-400 mx-auto mb-4"
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
            <h3 class="text-lg font-semibold text-gray-900 mb-2">
                No jobs available
            </h3>
            <p class="text-gray-600">Check back later for new opportunities</p>
        </div>
    {:else}
        <div class="card text-center py-12">
            <svg
                class="w-16 h-16 text-gray-400 mx-auto mb-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
            >
                <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
            </svg>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">
                No jobs match your filters
            </h3>
            <p class="text-gray-600 mb-4">Try adjusting your search criteria</p>
            <button
                on:click={() => {
                    searchTerm = "";
                    selectedJobType = "all";
                }}
                class="btn btn-primary"
            >
                Clear filters
            </button>
        </div>
    {/if}
</div>
