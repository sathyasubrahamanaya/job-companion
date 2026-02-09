<script lang="ts">
    import type { Job } from "$lib/api/types";

    export let job: Job;
    export let onClick: (() => void) | undefined = undefined;
</script>

<div
    class="card hover:shadow-md transition-shadow cursor-pointer"
    on:click={onClick}
    on:keypress={(e) => e.key === "Enter" && onClick?.()}
    role="button"
    tabindex="0"
>
    <div class="flex justify-between items-start mb-3">
        <h3 class="text-lg font-semibold text-gray-900">{job.title}</h3>
        <span
            class="px-3 py-1 bg-primary-100 text-primary-700 text-sm font-medium rounded-full"
        >
            {job.job_type.replace("_", " ")}
        </span>
    </div>

    <p class="text-gray-600 text-sm mb-4 line-clamp-2">{job.description}</p>

    <div class="flex flex-wrap gap-2 mb-4">
        {#each job.required_skills.slice(0, 4) as skill}
            <span class="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-md"
                >{skill}</span
            >
        {/each}
        {#if job.required_skills.length > 4}
            <span
                class="px-2 py-1 bg-gray-100 text-gray-500 text-xs rounded-md"
            >
                +{job.required_skills.length - 4} more
            </span>
        {/if}
    </div>

    <div class="flex items-center justify-between text-sm text-gray-500">
        <div class="flex items-center space-x-4">
            <span class="flex items-center">
                <svg
                    class="w-4 h-4 mr-1"
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
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                    />
                </svg>
                {job.location}
            </span>
            <span class="flex items-center">
                <svg
                    class="w-4 h-4 mr-1"
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
                {job.experience_required} years
            </span>
        </div>
        {#if job.salary_range}
            <span class="font-semibold text-primary-600"
                >{job.salary_range}</span
            >
        {/if}
    </div>
</div>
