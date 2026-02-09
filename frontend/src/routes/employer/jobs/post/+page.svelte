<script lang="ts">
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import { authStore } from "$lib/stores/auth";
    import { postJob } from "$lib/api/jobs";
    import { JobType, UserRole } from "$lib/api/types";
    import { toastStore } from "$lib/stores/toast";

    let title = "";
    let description = "";
    let requiredSkills = "";
    let experienceRequired = 0;
    let location = "";
    let jobType: JobType = JobType.FULL_TIME;
    let salaryRange = "";
    let loading = false;
    let error = "";

    onMount(() => {
        if (
            !$authStore.isAuthenticated ||
            $authStore.user?.role !== UserRole.EMPLOYER
        ) {
            goto("/login");
        }
    });

    async function handlePost() {
        error = "";

        if (!requiredSkills.trim()) {
            error = "Please add at least one required skill";
            return;
        }

        loading = true;

        try {
            const skillsArray = requiredSkills
                .split(",")
                .map((s) => s.trim())
                .filter((s) => s.length > 0);

            await postJob({
                title,
                description,
                required_skills: skillsArray,
                experience_required: experienceRequired,
                location,
                job_type: jobType,
                salary_range: salaryRange || undefined,
            });

            toastStore.show("success", "Job posted successfully!");
            goto("/employer/jobs");
        } catch (err: any) {
            error =
                err.response?.data?.Message ||
                err.response?.data?.detail ||
                "Failed to post job. Please try again.";
            toastStore.show("error", error);
        } finally {
            loading = false;
        }
    }
</script>

<svelte:head>
    <title>Post a Job - JobCompanion AI</title>
</svelte:head>

<div class="max-w-3xl mx-auto">
    <div class="card">
        <div class="mb-8">
            <h1 class="text-3xl font-bold text-gray-900 mb-2">
                Post a New Job
            </h1>
            <p class="text-gray-600">
                Fill in the details to attract the best candidates with
                AI-powered matching
            </p>
        </div>

        <form on:submit|preventDefault={handlePost} class="space-y-6">
            <div>
                <label for="title" class="label">Job Title</label>
                <input
                    id="title"
                    type="text"
                    bind:value={title}
                    required
                    class="input"
                    placeholder="e.g., Senior Full Stack Developer"
                />
            </div>

            <div class="grid md:grid-cols-2 gap-4">
                <div>
                    <label for="jobType" class="label">Job Type</label>
                    <select
                        id="jobType"
                        bind:value={jobType}
                        required
                        class="input"
                    >
                        <option value={JobType.FULL_TIME}>Full Time</option>
                        <option value={JobType.PART_TIME}>Part Time</option>
                        <option value={JobType.INTERNSHIP}>Internship</option>
                    </select>
                </div>

                <div>
                    <label for="experienceRequired" class="label"
                        >Years of Experience Required</label
                    >
                    <input
                        id="experienceRequired"
                        type="number"
                        bind:value={experienceRequired}
                        required
                        min="0"
                        max="50"
                        class="input"
                        placeholder="e.g., 3"
                    />
                </div>
            </div>

            <div class="grid md:grid-cols-2 gap-4">
                <div>
                    <label for="location" class="label">Location</label>
                    <input
                        id="location"
                        type="text"
                        bind:value={location}
                        required
                        class="input"
                        placeholder="e.g., New York, NY or Remote"
                    />
                </div>

                <div>
                    <label for="salaryRange" class="label"
                        >Salary Range (Optional)</label
                    >
                    <input
                        id="salaryRange"
                        type="text"
                        bind:value={salaryRange}
                        class="input"
                        placeholder="e.g., $120k - $160k"
                    />
                </div>
            </div>

            <div>
                <label for="requiredSkills" class="label">Required Skills</label
                >
                <input
                    id="requiredSkills"
                    type="text"
                    bind:value={requiredSkills}
                    required
                    class="input"
                    placeholder="e.g., Python, React, Docker, AWS (comma-separated)"
                />
                <p class="text-xs text-gray-500 mt-1">
                    Separate skills with commas
                </p>
                {#if requiredSkills}
                    <div class="flex flex-wrap gap-2 mt-2">
                        {#each requiredSkills
                            .split(",")
                            .map((s) => s.trim())
                            .filter((s) => s.length > 0) as skill}
                            <span
                                class="px-2 py-1 bg-primary-100 text-primary-700 text-xs rounded-md"
                                >{skill}</span
                            >
                        {/each}
                    </div>
                {/if}
            </div>

            <div>
                <label for="description" class="label">Job Description</label>
                <textarea
                    id="description"
                    bind:value={description}
                    required
                    rows="8"
                    class="input"
                    placeholder="Describe the role, responsibilities, qualifications, and what makes this opportunity great..."
                ></textarea>
                <p class="text-xs text-gray-500 mt-1">
                    Be detailed - our AI will use this to match candidates
                </p>
            </div>

            {#if error}
                <div
                    class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm"
                >
                    {error}
                </div>
            {/if}

            <div class="flex gap-4">
                <button
                    type="submit"
                    class="btn btn-primary flex-1 py-3"
                    disabled={loading}
                >
                    {loading ? "Posting Job..." : "Post Job"}
                </button>
                <button
                    type="button"
                    on:click={() => goto("/employer/jobs")}
                    class="btn btn-secondary px-6"
                >
                    Cancel
                </button>
            </div>
        </form>
    </div>
</div>
