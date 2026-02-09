<script lang="ts">
    import { goto } from "$app/navigation";
    import { employerSignup } from "$lib/api/employer";
    import { toastStore } from "$lib/stores/toast";

    let name = "";
    let email = "";
    let password = "";
    let confirmPassword = "";
    let loading = false;
    let error = "";

    async function handleSignup() {
        error = "";

        if (password !== confirmPassword) {
            error = "Passwords do not match";
            return;
        }

        loading = true;

        try {
            const response = await employerSignup({ name, email, password });
            toastStore.show(
                "success",
                "Account created successfully! Please log in to complete your profile.",
            );
            goto("/login");
        } catch (err: any) {
            error =
                err.response?.data?.Message ||
                err.response?.data?.detail ||
                "Signup failed. Please try again.";
            toastStore.show("error", error);
        } finally {
            loading = false;
        }
    }
</script>

<svelte:head>
    <title>Employer Signup - JobCompanion AI</title>
</svelte:head>

<div class="min-h-[calc(100vh-8rem)] flex items-center justify-center py-12">
    <div class="card max-w-lg w-full">
        <div class="text-center mb-8">
            <h1 class="text-3xl font-bold text-gray-900 mb-2">
                Create Employer Account
            </h1>
            <p class="text-gray-600">
                Find the best talent with AI-powered candidate matching
            </p>
        </div>

        <form on:submit|preventDefault={handleSignup} class="space-y-5">
            <div>
                <label for="name" class="label">Full Name</label>
                <input
                    id="name"
                    type="text"
                    bind:value={name}
                    required
                    class="input"
                    placeholder="Jane Smith"
                />
            </div>

            <div>
                <label for="email" class="label">Email Address</label>
                <input
                    id="email"
                    type="email"
                    bind:value={email}
                    required
                    class="input"
                    placeholder="you@company.com"
                />
            </div>

            <div>
                <label for="password" class="label">Password</label>
                <input
                    id="password"
                    type="password"
                    bind:value={password}
                    required
                    minlength="6"
                    class="input"
                    placeholder="At least 6 characters"
                />
            </div>

            <div>
                <label for="confirmPassword" class="label"
                    >Confirm Password</label
                >
                <input
                    id="confirmPassword"
                    type="password"
                    bind:value={confirmPassword}
                    required
                    class="input"
                    placeholder="Re-enter your password"
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
                {loading ? "Creating Account..." : "Create Account"}
            </button>
        </form>

        <div class="mt-6 text-center text-sm">
            <p class="text-gray-600">
                Already have an account?
                <a
                    href="/login"
                    class="text-primary-600 hover:text-primary-700 font-semibold"
                    >Sign in</a
                >
            </p>
            <p class="text-gray-600 mt-2">
                Looking for a job?
                <a
                    href="/signup/candidate"
                    class="text-primary-600 hover:text-primary-700 font-semibold"
                    >Sign up as Candidate</a
                >
            </p>
        </div>

        <div class="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p class="text-sm text-blue-800">
                <strong>Note:</strong> After creating your account, you'll need to
                complete your company profile before posting jobs.
            </p>
        </div>
    </div>
</div>
