<script lang="ts">
    import { authStore } from "$lib/stores/auth";
    import { goto } from "$app/navigation";
    import { UserRole } from "$lib/api/types";
    import NotificationBell from "./NotificationBell.svelte";

    let isOpen = false;
    let user: any = null;

    $: user = $authStore.user;
    $: isAuthenticated = $authStore.isAuthenticated;

    function handleLogout() {
        authStore.logout();
        goto("/login");
    }
</script>

<nav class="bg-white shadow-sm border-b border-gray-200">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
            <!-- Logo -->
            <div class="flex items-center">
                <a href="/" class="flex items-center space-x-2">
                    <div
                        class="w-10 h-10 bg-gradient-to-br from-primary-600 to-secondary-600 rounded-lg flex items-center justify-center"
                    >
                        <span class="text-white font-bold text-xl">JC</span>
                    </div>
                    <span class="font-bold text-xl text-gray-900"
                        >JobCompanion</span
                    >
                </a>
            </div>

            <!-- Desktop Navigation -->
            <div class="hidden md:flex items-center space-x-6">
                {#if isAuthenticated}
                    <a
                        href="/jobs/all"
                        class="text-gray-700 hover:text-primary-600 font-medium"
                        >Browse Jobs</a
                    >

                    {#if user?.role === UserRole.CANDIDATE}
                        <a
                            href="/candidate/dashboard"
                            class="text-gray-700 hover:text-primary-600 font-medium"
                            >Dashboard</a
                        >
                        <a
                            href="/candidate/jobs/search"
                            class="text-gray-700 hover:text-primary-600 font-medium"
                            >AI Search</a
                        >
                    {:else if user?.role === UserRole.EMPLOYER}
                        <a
                            href="/employer/dashboard"
                            class="text-gray-700 hover:text-primary-600 font-medium"
                            >Dashboard</a
                        >
                        <a
                            href="/employer/jobs"
                            class="text-gray-700 hover:text-primary-600 font-medium"
                            >My Jobs</a
                        >
                        <a
                            href="/employer/jobs/post"
                            class="text-gray-700 hover:text-primary-600 font-medium"
                            >Post Job</a
                        >
                    {/if}

                    {#if isAuthenticated}
                        <NotificationBell />
                    {/if}

                    <!-- User Dropdown -->
                    <div class="relative">
                        <button
                            on:click={() => (isOpen = !isOpen)}
                            class="flex items-center space-x-2 text-gray-700 hover:text-primary-600"
                        >
                            <div
                                class="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center"
                            >
                                <span
                                    class="text-primary-600 font-semibold text-sm"
                                    >{user?.name?.charAt(0) || "U"}</span
                                >
                            </div>
                            <span class="font-medium">{user?.name}</span>
                        </button>

                        {#if isOpen}
                            <div
                                class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50"
                            >
                                <button
                                    on:click={handleLogout}
                                    class="w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-100"
                                >
                                    Logout
                                </button>
                            </div>
                        {/if}
                    </div>
                {:else}
                    <a
                        href="/login"
                        class="text-gray-700 hover:text-primary-600 font-medium"
                        >Login</a
                    >
                    <a href="/signup/candidate" class="btn btn-primary"
                        >Get Started</a
                    >
                {/if}
            </div>

            <!-- Mobile menu button -->
            <div class="md:hidden">
                <button class="text-gray-700">
                    <svg
                        class="w-6 h-6"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M4 6h16M4 12h16M4 18h16"
                        />
                    </svg>
                </button>
            </div>
        </div>
    </div>
</nav>
