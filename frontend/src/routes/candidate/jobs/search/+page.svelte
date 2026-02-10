<script lang="ts">
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import { authStore } from "$lib/stores/auth";
    import { searchJobs } from "$lib/api/candidate";
    import { UserRole, type Job } from "$lib/api/types";
    import { toastStore } from "$lib/stores/toast";
    import JobCard from "$lib/components/JobCard.svelte";

    let query = "";
    let loading = false;
    let jobs: Job[] = [];
    let searched = false;

    onMount(() => {
        if (
            !$authStore.isAuthenticated ||
            $authStore.user?.role !== UserRole.CANDIDATE
        ) {
            goto("/login");
        }
    });

    async function handleSearch() {
        if (!query.trim()) {
            toastStore.show("error", "Please enter a search query");
            return;
        }

        loading = true;
        try {
            console.log("🔍 Searching for:", query);
            const response = await searchJobs({ query, limit: 20 });
            console.log("✅ Response received:", response);
            console.log("📦 Response.Data:", response.Data);

            jobs = response.Data || [];
            searched = true;
            toastStore.show("success", `Found ${jobs.length} matching jobs`);
        } catch (err: any) {
            console.error("❌ Search error:", err);
            console.error("Error details:", err.response?.data);
            toastStore.show("error", "Search failed. Please try again.");
        } finally {
            loading = false;
        }
    }

    function viewJobDetails(jobId: string) {
        goto(`/candidate/jobs/${jobId}`);
    }
</script>

<svelte:head>
    <title>Search Jobs - JobCompanion AI</title>
</svelte:head>

<div class="space-y-8">
    <div>
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Search Jobs</h1>
        <p class="text-gray-600">
            Use AI-powered semantic search to find the perfect opportunities
        </p>
    </div>

    <!-- Search Bar -->
    <div class="card">
        <form on:submit|preventDefault={handleSearch} class="flex gap-4">
            <input
                type="text"
                bind:value={query}
                placeholder="e.g., 'Senior Python developer with ML experience in San Francisco'"
                class="input flex-1"
            />
            <button
                type="submit"
                class="btn btn-primary px-8"
                disabled={loading}
            >
                {loading ? "Searching..." : "Search"}
            </button>
        </form>
        <p class="text-sm text-gray-500 mt-3">
            💡 Tip: Describe your ideal job naturally. Our AI understands
            context and semantics!
        </p>
    </div>

    <!-- Results -->
    {#if loading}
        <div class="flex items-center justify-center py-12">
            <div class="text-center">
                <div
                    class="w-16 h-16 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"
                ></div>
                <p class="text-gray-600">Searching for the best matches...</p>
            </div>
        </div>
    {:else if searched}
        {#if jobs.length > 0}
            <div>
                <h2 class="text-xl font-semibold text-gray-900 mb-4">
                    Found {jobs.length} matching {jobs.length === 1
                        ? "job"
                        : "jobs"}
                </h2>
                <div class="grid gap-4">
                    {#each jobs as job}
                        <JobCard
                            {job}
                            onClick={() => viewJobDetails(job.job_id)}
                        />
                    {/each}
                </div>
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
                    No jobs found
                </h3>
                <p class="text-gray-600">
                    Try adjusting your search query or check back later for new
                    opportunities
                </p>
            </div>
        {/if}
    {/if}
</div>
