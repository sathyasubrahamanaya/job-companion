<script lang="ts">
    import { goto } from "$app/navigation";
    import { authStore } from "$lib/stores/auth";

    $: isAuthenticated = $authStore.isAuthenticated;
</script>

<svelte:head>
    <title>JobCompanion AI - Your AI-Powered Career Partner</title>
</svelte:head>

<div class="min-h-[calc(100vh-4rem)] flex items-center">
    <div class="w-full">
        <!-- Hero Section -->
        <div class="text-center max-w-4xl mx-auto mb-16">
            <div class="mb-8">
                <span
                    class="inline-block px-4 py-2 bg-primary-100 text-primary-700 rounded-full font-semibold text-sm mb-6"
                >
                    AI-Powered Job Platform
                </span>
            </div>
            <h1
                class="text-5xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight"
            >
                Find Your <span
                    class="bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent"
                    >Dream Job</span
                > with AI
            </h1>
            <p class="text-xl text-gray-600 mb-10 max-w-2xl mx-auto">
                JobCompanion uses advanced AI to match candidates with perfect
                opportunities and help employers find the best talent.
                Experience the future of recruitment.
            </p>

            {#if !isAuthenticated}
                <div
                    class="flex flex-col sm:flex-row gap-4 justify-center items-center"
                >
                    <button
                        on:click={() => goto("/signup/candidate")}
                        class="btn btn-primary px-8 py-3 text-lg"
                    >
                        Get Started as Candidate
                    </button>
                    <button
                        on:click={() => goto("/signup/employer")}
                        class="btn btn-secondary px-8 py-3 text-lg"
                    >
                        I'm an Employer
                    </button>
                </div>
                <p class="mt-6 text-gray-500">
                    Already have an account?
                    <a
                        href="/login"
                        class="text-primary-600 hover:text-primary-700 font-semibold"
                        >Sign in</a
                    >
                </p>
            {:else}
                <div class="flex gap-4 justify-center">
                    <button
                        on:click={() =>
                            goto(
                                $authStore.user?.role === "CANDIDATE"
                                    ? "/candidate/dashboard"
                                    : "/employer/dashboard",
                            )}
                        class="btn btn-primary px-8 py-3 text-lg"
                    >
                        Go to Dashboard
                    </button>
                </div>
            {/if}
        </div>

        <!-- Features Grid -->
        <div class="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto mt-20">
            <div class="text-center">
                <div
                    class="w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-4"
                >
                    <svg
                        class="w-8 h-8 text-white"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                        />
                    </svg>
                </div>
                <h3 class="text-xl font-semibold text-gray-900 mb-2">
                    AI-Powered Matching
                </h3>
                <p class="text-gray-600">
                    Semantic search and intelligent matching to find the perfect
                    fit
                </p>
            </div>

            <div class="text-center">
                <div
                    class="w-16 h-16 bg-gradient-to-br from-secondary-500 to-secondary-600 rounded-2xl flex items-center justify-center mx-auto mb-4"
                >
                    <svg
                        class="w-8 h-8 text-white"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                        />
                    </svg>
                </div>
                <h3 class="text-xl font-semibold text-gray-900 mb-2">
                    AI Interviews
                </h3>
                <p class="text-gray-600">
                    Practice with AI-powered interview simulations
                </p>
            </div>

            <div class="text-center">
                <div
                    class="w-16 h-16 bg-gradient-to-br from-primary-400 to-secondary-500 rounded-2xl flex items-center justify-center mx-auto mb-4"
                >
                    <svg
                        class="w-8 h-8 text-white"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                        />
                    </svg>
                </div>
                <h3 class="text-xl font-semibold text-gray-900 mb-2">
                    Smart Resume Parser
                </h3>
                <p class="text-gray-600">
                    AI extracts and structures information from your resume
                    automatically
                </p>
            </div>
        </div>
    </div>
</div>
