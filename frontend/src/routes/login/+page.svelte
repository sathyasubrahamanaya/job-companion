<script lang="ts">
    import { goto } from "$app/navigation";
    import { login, saveToken } from "$lib/api/auth";
    import { authStore } from "$lib/stores/auth";
    import { toastStore } from "$lib/stores/toast";
    import { UserRole } from "$lib/api/types";
    import { onMount } from "svelte";

    let email = "";
    let password = "";
    let loading = false;
    let error = "";

    onMount(() => {
        // Redirect if already logged in
        if ($authStore.isAuthenticated) {
            const role = $authStore.user?.role;
            if (role === UserRole.CANDIDATE) {
                goto("/candidate/dashboard");
            } else if (role === UserRole.EMPLOYER) {
                goto("/employer/dashboard");
            }
        }
    });

    async function handleLogin() {
        error = "";
        loading = true;

        try {
            const tokenResponse = await login({ email, password });
            saveToken(tokenResponse.access_token);

            // Decode JWT to get user info
            const payload = JSON.parse(
                atob(tokenResponse.access_token.split(".")[1]),
            );

            // Create user object
            const user = {
                user_id: payload.sub,
                email: payload.sub,
                name: email.split("@")[0],
                role: payload.role as UserRole,
                created_at: new Date().toISOString(),
            };

            authStore.setAuth(user, tokenResponse.access_token);
            toastStore.show("success", "Login successful!");

            // Redirect based on role
            if (payload.role === UserRole.CANDIDATE) {
                goto("/candidate/dashboard");
            } else if (payload.role === UserRole.EMPLOYER) {
                goto("/employer/dashboard");
            }
        } catch (err: any) {
            error =
                err.response?.data?.Message ||
                "Login failed. Please check your credentials.";
            toastStore.show("error", error);
        } finally {
            loading = false;
        }
    }
</script>

<svelte:head>
    <title>Login - JobCompanion AI</title>
</svelte:head>

<div class="min-h-[calc(100vh-8rem)] flex items-center justify-center">
    <div class="card max-w-md w-full">
        <div class="text-center mb-8">
            <h1 class="text-3xl font-bold text-gray-900 mb-2">Welcome Back</h1>
            <p class="text-gray-600">Sign in to your JobCompanion account</p>
        </div>

        <form on:submit|preventDefault={handleLogin} class="space-y-5">
            <div>
                <label for="email" class="label">Email Address</label>
                <input
                    id="email"
                    type="email"
                    bind:value={email}
                    required
                    class="input"
                    placeholder="you@example.com"
                />
            </div>

            <div>
                <label for="password" class="label">Password</label>
                <input
                    id="password"
                    type="password"
                    bind:value={password}
                    required
                    class="input"
                    placeholder="Enter your password"
                />
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
                {loading ? "Signing in..." : "Sign In"}
            </button>
        </form>

        <div class="mt-6 text-center text-sm">
            <p class="text-gray-600">
                Don't have an account?
                <a
                    href="/signup/candidate"
                    class="text-primary-600 hover:text-primary-700 font-semibold"
                    >Sign up as Candidate</a
                >
                or
                <a
                    href="/signup/employer"
                    class="text-primary-600 hover:text-primary-700 font-semibold"
                    >Employer</a
                >
            </p>
        </div>
    </div>
</div>
