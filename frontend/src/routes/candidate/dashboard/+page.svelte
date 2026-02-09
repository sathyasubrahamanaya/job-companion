<script lang="ts">
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import { authStore } from "$lib/stores/auth";
    import { getCandidateProfile } from "$lib/api/candidate";
    import { candidateProfile } from "$lib/stores/profile";
    import { UserRole } from "$lib/api/types";
    import { toastStore } from "$lib/stores/toast";

    let loading = true;
    let profile: any = null;
    let user: any = null;

    onMount(async () => {
        if (
            !$authStore.isAuthenticated ||
            $authStore.user?.role !== UserRole.CANDIDATE
        ) {
            goto("/login");
            return;
        }

        try {
            const response = await getCandidateProfile();
            profile = response.Data?.profile;
            user = response.Data?.user;
            candidateProfile.set(profile);
        } catch (err: any) {
            toastStore.show("error", "Failed to load profile");
        } finally {
            loading = false;
        }
    });
</script>

<svelte:head>
    <title>Candidate Dashboard - JobCompanion AI</title>
</svelte:head>

{#if loading}
    <div class="flex items-center justify-center min-h-[60vh]">
        <div class="text-center">
            <div
                class="w-16 h-16 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"
            ></div>
            <p class="text-gray-600">Loading your dashboard...</p>
        </div>
    </div>
{:else if profile}
    <div class="space-y-8">
        <!-- Welcome Section -->
        <div
            class="card bg-gradient-to-r from-primary-600 to-secondary-600 text-white"
        >
            <h1 class="text-3xl font-bold mb-2">
                Welcome back, {user?.name || "Candidate"}!
            </h1>
            <p class="text-primary-100">Ready to find your next opportunity?</p>
        </div>

        <!-- Quick Stats -->
        <div class="grid md:grid-cols-3 gap-6">
            <div class="card">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-500 text-sm">Skills</p>
                        <p class="text-2xl font-bold text-gray-900">
                            {profile.skills?.length || 0}
                        </p>
                    </div>
                    <div
                        class="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center"
                    >
                        <svg
                            class="w-6 h-6 text-primary-600"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"
                            />
                        </svg>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-500 text-sm">Experience</p>
                        <p class="text-2xl font-bold text-gray-900">
                            {profile.experience_years} years
                        </p>
                    </div>
                    <div
                        class="w-12 h-12 bg-secondary-100 rounded-lg flex items-center justify-center"
                    >
                        <svg
                            class="w-6 h-6 text-secondary-600"
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
                </div>
            </div>

            <div class="card">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-500 text-sm">Education</p>
                        <p class="text-2xl font-bold text-gray-900">
                            {profile.educations?.length || 0}
                        </p>
                    </div>
                    <div
                        class="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center"
                    >
                        <svg
                            class="w-6 h-6 text-primary-600"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path d="M12 14l9-5-9-5-9 5 9 5z" />
                            <path
                                d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z"
                            />
                            <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14zm-4 6v-7.5l4-2.222"
                            />
                        </svg>
                    </div>
                </div>
            </div>
        </div>

        <!-- Profile Overview -->
        <div class="card">
            <h2 class="text-2xl font-bold text-gray-900 mb-6">Your Profile</h2>

            <div class="space-y-6">
                <div>
                    <h3 class="text-sm font-semibold text-gray-700 mb-2">
                        Skills
                    </h3>
                    <div class="flex flex-wrap gap-2">
                        {#each profile.skills || [] as skill}
                            <span
                                class="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-medium"
                                >{skill}</span
                            >
                        {/each}
                    </div>
                </div>

                <div>
                    <h3 class="text-sm font-semibold text-gray-700 mb-2">
                        Preferred Roles
                    </h3>
                    <div class="flex flex-wrap gap-2">
                        {#each profile.preferred_roles || [] as role}
                            <span
                                class="px-3 py-1 bg-secondary-100 text-secondary-700 rounded-full text-sm font-medium"
                                >{role}</span
                            >
                        {/each}
                    </div>
                </div>

                <div>
                    <h3 class="text-sm font-semibold text-gray-700 mb-2">
                        Preferred Locations
                    </h3>
                    <div class="flex flex-wrap gap-2">
                        {#each profile.preferred_locations || [] as location}
                            <span
                                class="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                                >{location}</span
                            >
                        {/each}
                    </div>
                </div>

                <div>
                    <h3 class="text-sm font-semibold text-gray-700 mb-2">
                        Education
                    </h3>
                    <ul class="list-disc list-inside space-y-1 text-gray-600">
                        {#each profile.educations || [] as education}
                            <li>{education}</li>
                        {/each}
                    </ul>
                </div>
            </div>

            <div class="mt-8 flex gap-4">
                <button
                    on:click={() => goto("/candidate/profile")}
                    class="btn btn-primary"
                >
                    Edit Profile
                </button>
                <button
                    on:click={() => goto("/candidate/jobs/search")}
                    class="btn btn-secondary"
                >
                    Search Jobs
                </button>
            </div>
        </div>
    </div>
{/if}
