<script lang="ts">
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import { authStore } from "$lib/stores/auth";
    import { getEmployerProfile } from "$lib/api/employer";
    import { UserRole } from "$lib/api/types";
    import { toastStore } from "$lib/stores/toast";

    let loading = true;
    let profile: any = null;
    let user: any = null;
    let needsOnboarding = false;

    onMount(async () => {
        if (
            !$authStore.isAuthenticated ||
            $authStore.user?.role !== UserRole.EMPLOYER
        ) {
            goto("/login");
            return;
        }

        try {
            const response = await getEmployerProfile();
            profile = response.Data?.profile;
            user = response.Data?.user;

            if (!profile) {
                needsOnboarding = true;
            }
        } catch (err: any) {
            // Profile not found, needs onboarding
            if (
                err.response?.status === 404 ||
                err.response?.data?.Message?.includes("not found")
            ) {
                needsOnboarding = true;
            } else {
                toastStore.show("error", "Failed to load profile");
            }
        } finally {
            loading = false;
        }
    });

    $: if (needsOnboarding && !loading) {
        goto("/employer/onboard");
    }
</script>

<svelte:head>
    <title>Employer Dashboard - JobCompanion AI</title>
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
            class="card bg-gradient-to-r from-secondary-600 to-primary-600 text-white"
        >
            <h1 class="text-3xl font-bold mb-2">
                Welcome back, {user?.name || "Employer"}!
            </h1>
            <p class="text-secondary-100">{profile.company_name}</p>
        </div>

        <!-- Company Profile -->
        <div class="card">
            <h2 class="text-2xl font-bold text-gray-900 mb-6">
                Company Profile
            </h2>

            <div class="space-y-4">
                <div>
                    <h3 class="text-sm font-semibold text-gray-700 mb-1">
                        Company Name
                    </h3>
                    <p class="text-gray-900">{profile.company_name}</p>
                </div>

                <div>
                    <h3 class="text-sm font-semibold text-gray-700 mb-1">
                        Industry
                    </h3>
                    <p class="text-gray-900">{profile.industry}</p>
                </div>

                <div>
                    <h3 class="text-sm font-semibold text-gray-700 mb-1">
                        Location
                    </h3>
                    <p class="text-gray-900">{profile.location}</p>
                </div>

                <div>
                    <h3 class="text-sm font-semibold text-gray-700 mb-1">
                        Description
                    </h3>
                    <p class="text-gray-700 whitespace-pre-line">
                        {profile.company_description}
                    </p>
                </div>
            </div>

            <div class="mt-8 flex gap-4">
                <button
                    on:click={() => goto("/employer/jobs/post")}
                    class="btn btn-primary"
                >
                    Post a Job
                </button>
                <button
                    on:click={() => goto("/employer/jobs")}
                    class="btn btn-secondary"
                >
                    View My Jobs
                </button>
            </div>
        </div>
    </div>
{/if}
