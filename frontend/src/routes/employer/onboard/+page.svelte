<script lang="ts">
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import { authStore } from "$lib/stores/auth";
    import { onboardEmployer, getEmployerProfile } from "$lib/api/employer";
    import { UserRole } from "$lib/api/types";
    import { toastStore } from "$lib/stores/toast";

    let companyName = "";
    let companyDescription = "";
    let industry = "";
    let location = "";
    let loading = false;
    let error = "";

    onMount(async () => {
        if (
            !$authStore.isAuthenticated ||
            $authStore.user?.role !== UserRole.EMPLOYER
        ) {
            goto("/login");
            return;
        }

        // Check if already onboarded
        try {
            await getEmployerProfile();
            // If success, already onboarded
            goto("/employer/jobs");
        } catch (err) {
            // If 404/400, stay here to complete onboarding
            console.log("No profile found, staying on onboarding page");
        }
    });

    async function handleOnboard() {
        error = "";
        loading = true;

        try {
            await onboardEmployer({
                company_name: companyName,
                company_description: companyDescription,
                industry,
                location,
            });
            toastStore.show("success", "Company profile created successfully!");
            goto("/employer/jobs");
        } catch (err: any) {
            error =
                err.response?.data?.Message ||
                "Onboarding failed. Please try again.";

            if (error.toLowerCase().includes("already exists")) {
                toastStore.show(
                    "info",
                    "Employer profile already exists. Redirecting...",
                );
                goto("/employer/jobs");
            } else {
                toastStore.show("error", error);
            }
        } finally {
            loading = false;
        }
    }
</script>

<svelte:head>
    <title>Company Onboarding - JobCompanion AI</title>
</svelte:head>

<div class="max-w-2xl mx-auto">
    <div class="card">
        <div class="mb-8">
            <h1 class="text-3xl font-bold text-gray-900 mb-2">
                Complete Your Company Profile
            </h1>
            <p class="text-gray-600">
                Tell us about your company to start posting jobs and finding
                talent
            </p>
        </div>

        <form on:submit|preventDefault={handleOnboard} class="space-y-5">
            <div>
                <label for="companyName" class="label">Company Name</label>
                <input
                    id="companyName"
                    type="text"
                    bind:value={companyName}
                    required
                    class="input"
                    placeholder="Acme Corporation"
                />
            </div>

            <div>
                <label for="industry" class="label">Industry</label>
                <input
                    id="industry"
                    type="text"
                    bind:value={industry}
                    required
                    class="input"
                    placeholder="e.g., Technology, Healthcare, Finance"
                />
            </div>

            <div>
                <label for="location" class="label">Company Location</label>
                <input
                    id="location"
                    type="text"
                    bind:value={location}
                    required
                    class="input"
                    placeholder="e.g., San Francisco, CA or Remote"
                />
            </div>

            <div>
                <label for="companyDescription" class="label"
                    >Company Description</label
                >
                <textarea
                    id="companyDescription"
                    bind:value={companyDescription}
                    required
                    rows="5"
                    class="input"
                    placeholder="Describe your company, mission, culture, and what makes it a great place to work..."
                ></textarea>
                <p class="text-xs text-gray-500 mt-1">
                    This will be shown to candidates when they view your job
                    postings
                </p>
            </div>

            {#if error}
                <div
                    class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm"
                >
                    {error}
                </div>
            {/if}

            <button
                type="submit"
                class="btn btn-primary w-full py-3"
                disabled={loading}
            >
                {loading ? "Creating Profile..." : "Complete Onboarding"}
            </button>
        </form>
    </div>
</div>
