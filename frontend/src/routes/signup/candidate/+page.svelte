<script lang="ts">
    import { goto } from "$app/navigation";
    import { candidateSignup } from "$lib/api/candidate";
    import { toastStore } from "$lib/stores/toast";

    let name = "";
    let email = "";
    let password = "";
    let confirmPassword = "";
    let file: File | null = null;
    let loading = false;
    let error = "";

    let fileInput: HTMLInputElement;

    function handleFileChange(e: Event) {
        const target = e.target as HTMLInputElement;
        if (target.files && target.files[0]) {
            const selectedFile = target.files[0];
            if (selectedFile.type !== "application/pdf") {
                error = "Only PDF files are allowed";
                file = null;
                return;
            }
            file = selectedFile;
            error = "";
        }
    }

    async function handleSignup() {
        error = "";

        if (password !== confirmPassword) {
            error = "Passwords do not match";
            return;
        }

        if (!file) {
            error = "Please upload your resume (PDF only)";
            return;
        }

        loading = true;

        try {
            const response = await candidateSignup({
                name,
                email,
                password,
                file,
            });
            toastStore.show(
                "success",
                "Account created successfully! Please log in.",
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
    <title>Candidate Signup - JobCompanion AI</title>
</svelte:head>

<div class="min-h-[calc(100vh-8rem)] flex items-center justify-center py-12">
    <div class="card max-w-lg w-full">
        <div class="text-center mb-8">
            <h1 class="text-3xl font-bold text-gray-900 mb-2">
                Create Candidate Account
            </h1>
            <p class="text-gray-600">
                Join JobCompanion and find your dream job with AI
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
                    placeholder="John Doe"
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

            <div>
                <label for="resume" class="label"
                    >Upload Resume (PDF only)</label
                >
                <div class="mt-1">
                    <input
                        bind:this={fileInput}
                        id="resume"
                        type="file"
                        accept=".pdf"
                        on:change={handleFileChange}
                        required
                        class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
                    />
                    <p class="text-xs text-gray-500 mt-2">
                        Our AI will automatically extract your skills,
                        experience, and education
                    </p>
                </div>
                {#if file}
                    <p class="text-sm text-green-600 mt-2 flex items-center">
                        <svg
                            class="w-4 h-4 mr-1"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                        >
                            <path
                                fill-rule="evenodd"
                                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                clip-rule="evenodd"
                            />
                        </svg>
                        {file.name} ({(file.size / 1024).toFixed(0)} KB)
                    </p>
                {/if}
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
                Looking to hire?
                <a
                    href="/signup/employer"
                    class="text-primary-600 hover:text-primary-700 font-semibold"
                    >Sign up as Employer</a
                >
            </p>
        </div>
    </div>
</div>
