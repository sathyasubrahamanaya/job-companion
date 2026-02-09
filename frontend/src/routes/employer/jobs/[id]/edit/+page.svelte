<script lang="ts">
    import { onMount } from "svelte";
    import { page } from "$app/stores";
    import { goto } from "$app/navigation";
    import { authStore } from "$lib/stores/auth";
    import { getJobDetails } from "$lib/api/jobs";
    import { updateJob } from "$lib/api/jobs";
    import { JobType, UserRole, type Job } from "$lib/api/types";
    import { toastStore } from "$lib/stores/toast";

    let job: Job | null = null;
    let loading = true;
    let saving = false;

    // Form fields
    let title = "";
    let description = "";
    let requiredSkills = "";
    let experienceRequired = 0;
    let location = "";
    let jobType: JobType = JobType.FULL_TIME;
    let salaryRange = "";
    let error = "";

    $: jobId = $page.params.id as string;

    onMount(async () => {
        if (
            !$authStore.isAuthenticated ||
            $authStore.user?.role !== UserRole.EMPLOYER
        ) {
            goto("/login");
            return;
        }

        try {
            const response = await getJobDetails(jobId);
            job = response.Data;

            // Populate form fields
            if (job) {
                title = job.title;
                description = job.description;
                requiredSkills = job.required_skills.join(", ");
                experienceRequired = job.experience_required;
                location = job.location;
                jobType = job.job_type;
                salaryRange = job.salary_range || "";
            }
        } catch (err: any) {
            toastStore.show("error", "Failed to load job details");
            goto("/employer/jobs");
        } finally {
            loading = false;
        }
    });

    async function handleUpdate() {
        error = "";

        if (!requiredSkills.trim()) {
            error = "Please add at least one required skill";
            return;
        }

        saving = true;

        try {
            const skillsArray = requiredSkills
                .split(",")
                .map((s) => s.trim())
                .filter((s) => s.length > 0);

            await updateJob(jobId, {
                title,
                description,
                required_skills: skillsArray,
                experience_required: experienceRequired,
                location,
                job_type: jobType,
                salary_range: salaryRange || undefined,
            });

            toastStore.show("success", "Job updated successfully!");
            goto("/employer/jobs");
        } catch (err: any) {
            error =
                err.response?.data?.Message ||
                err.response?.data?.detail ||
                "Failed to update job. Please try again.";
            toastStore.show("error", error);
        } finally {
            saving = false;
        }
    }
</script>

<svelte:head>
    <title>Edit Job - JobCompanion AI</title>
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
    <div class="max-w-3xl mx-auto">
        <button
            on:click={() => goto("/employer/jobs")}
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
            Back to My Jobs
        </button>

        <div class="card">
            <div class="mb-8">
                <h1 class="text-3xl font-bold text-gray-900 mb-2">Edit Job</h1>
                <p class="text-gray-600">Update the job details below</p>
            </div>

            <form on:submit|preventDefault={handleUpdate} class="space-y-6">
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
                            <option value={JobType.INTERNSHIP}
                                >Internship</option
                            >
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
                    <label for="requiredSkills" class="label"
                        >Required Skills</label
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
                    <label for="description" class="label"
                        >Job Description</label
                    >
                    <textarea
                        id="description"
                        bind:value={description}
                        required
                        rows="8"
                        class="input"
                        placeholder="Describe the role, responsibilities, qualifications, and what makes this opportunity great..."
                    ></textarea>
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
                        disabled={saving}
                    >
                        {saving ? "Updating Job..." : "Update Job"}
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
{/if}
