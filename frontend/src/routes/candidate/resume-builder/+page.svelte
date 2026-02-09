<script lang="ts">
    import { onMount } from "svelte";
    import { authStore } from "$lib/stores/auth";
    import { buildResume, downloadResumePdf } from "$lib/api/resume";
    import type {
        ResumeInput,
        ResumeData,
        WorkExperience,
        Education,
        Project,
    } from "$lib/api/types";
    import {
        Loader2,
        Plus,
        Trash2,
        Wand2,
        Download,
        Eye,
        Edit3,
        ChevronRight,
        ChevronDown,
    } from "lucide-svelte";

    // --- State ---
    let user: any = null;
    let loading = false;
    let polishing = false;
    let previewHtml = "";
    let activeTab: "edit" | "preview" = "edit";
    let selectedTemplate = "classic";

    let formData: ResumeInput = {
        full_name: "",
        email: "",
        phone: "",
        linkedin_url: "",
        photo_url: "",
        professional_summary: "",
        skills: [],
        experience: [],
        education: [],
        projects: [],
    };

    let skillInput = "";

    $: user = $authStore.user;

    onMount(() => {
        if (user) {
            formData.full_name = user.name || "";
            formData.email = user.email || "";
        }
    });

    // --- Helpers ---
    function addExperience() {
        formData.experience = [
            ...formData.experience,
            { title: "", company: "", duration: "", description: [""] },
        ];
    }

    function removeExperience(index: number) {
        formData.experience = formData.experience.filter((_, i) => i !== index);
    }

    function addExpBullet(expIndex: number) {
        formData.experience[expIndex].description = [
            ...formData.experience[expIndex].description,
            "",
        ];
    }

    function removeExpBullet(expIndex: number, bulletIndex: number) {
        formData.experience[expIndex].description = formData.experience[
            expIndex
        ].description.filter((_, i) => i !== bulletIndex);
    }

    function addEducation() {
        formData.education = [
            ...formData.education,
            { degree: "", institution: "", year: "" },
        ];
    }

    function removeEducation(index: number) {
        formData.education = formData.education.filter((_, i) => i !== index);
    }

    function addProject() {
        formData.projects = [
            ...formData.projects,
            { name: "", description: "", tech_stack: [] },
        ];
    }

    function removeProject(index: number) {
        formData.projects = formData.projects.filter((_, i) => i !== index);
    }

    function addSkill() {
        if (skillInput.trim()) {
            formData.skills = [...formData.skills, skillInput.trim()];
            skillInput = "";
        }
    }

    function removeSkill(skill: string) {
        formData.skills = formData.skills.filter((s) => s !== skill);
    }

    // --- Handlers ---
    async function handlePolish() {
        polishing = true;
        try {
            const response = await buildResume(formData);
            if (response.ErrorCode === 0 && response.Data) {
                formData = { ...response.Data.json_data };
                previewHtml = response.Data.html_content;
                activeTab = "preview";
            }
        } catch (error) {
            console.error("Polishing failed:", error);
        } finally {
            polishing = false;
        }
    }

    async function handleDownload() {
        loading = true;
        try {
            // We use the current formData (it must match ResumeData schema for download)
            // If some fields are missing, the agent should have filled them or user did.
            await downloadResumePdf(formData as ResumeData, selectedTemplate);
        } catch (error) {
            console.error("Download failed:", error);
        } finally {
            loading = false;
        }
    }

    // Real-time preview update would ideally happen on backend but for now we rely on the Polish button
    // to get the polished HTML. We could also implement a basic local preview.
</script>

<div class="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
    <div class="max-w-7xl mx-auto">
        <!-- Header -->
        <div
            class="flex flex-col md:flex-row md:items-center md:justify-between mb-8 gap-4"
        >
            <div>
                <h1
                    class="text-3xl font-extrabold text-gray-900 tracking-tight"
                >
                    AI Resume Builder
                </h1>
                <p class="mt-2 text-lg text-gray-600">
                    Create a professional, AI-optimized resume in minutes.
                </p>
            </div>

            <div class="flex items-center gap-3">
                <button
                    on:click={handlePolish}
                    disabled={polishing}
                    class="btn btn-primary flex items-center gap-2 shadow-lg shadow-primary-200"
                >
                    {#if polishing}
                        <Loader2 class="w-4 h-4 animate-spin" />
                        Polishing...
                    {:else}
                        <Wand2 class="w-4 h-4" />
                        Polish with AI
                    {/if}
                </button>

                <div
                    class="flex border rounded-lg overflow-hidden bg-white shadow-sm"
                >
                    <button
                        on:click={() => (activeTab = "edit")}
                        class="px-4 py-2 text-sm font-medium {activeTab ===
                        'edit'
                            ? 'bg-primary-50 text-primary-700'
                            : 'text-gray-600 hover:bg-gray-50'}"
                    >
                        Edit
                    </button>
                    <button
                        on:click={() => (activeTab = "preview")}
                        class="px-4 py-2 text-sm font-medium {activeTab ===
                        'preview'
                            ? 'bg-primary-50 text-primary-700'
                            : 'text-gray-600 hover:bg-gray-50'}"
                    >
                        Preview
                    </button>
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <!-- Left: Form -->
            <div
                class="space-y-6 {activeTab === 'preview'
                    ? 'hidden lg:block'
                    : ''}"
            >
                <!-- Personal Info -->
                <div class="card p-6">
                    <h3
                        class="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2"
                    >
                        <span
                            class="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-sm"
                            >1</span
                        >
                        Personal Information
                    </h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="form-control">
                            <label class="label" for="full_name"
                                >Full Name</label
                            >
                            <input
                                type="text"
                                id="full_name"
                                bind:value={formData.full_name}
                                class="input"
                                placeholder="John Doe"
                            />
                        </div>
                        <div class="form-control">
                            <label class="label" for="email">Email</label>
                            <input
                                type="email"
                                id="email"
                                bind:value={formData.email}
                                class="input"
                                placeholder="john@example.com"
                            />
                        </div>
                        <div class="form-control">
                            <label class="label" for="phone"
                                >Phone (Optional)</label
                            >
                            <input
                                type="text"
                                id="phone"
                                bind:value={formData.phone}
                                class="input"
                                placeholder="+1 234 567 890"
                            />
                        </div>
                        <div class="form-control">
                            <label class="label" for="linkedin"
                                >LinkedIn URL (Optional)</label
                            >
                            <input
                                type="text"
                                id="linkedin"
                                bind:value={formData.linkedin_url}
                                class="input"
                                placeholder="linkedin.com/in/johndoe"
                            />
                        </div>
                        <div class="form-control md:col-span-2">
                            <label class="label" for="photo"
                                >Photo URL (Optional)</label
                            >
                            <input
                                type="text"
                                id="photo"
                                bind:value={formData.photo_url}
                                class="input"
                                placeholder="https://example.com/photo.jpg"
                            />
                        </div>
                    </div>
                </div>

                <!-- Professional Summary -->
                <div class="card p-6">
                    <h3
                        class="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2"
                    >
                        <span
                            class="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-sm"
                            >2</span
                        >
                        Professional Summary
                    </h3>
                    <p class="text-xs text-gray-500 mb-3">
                        Leave empty to let AI generate a summary based on your
                        experience.
                    </p>
                    <textarea
                        bind:value={formData.professional_summary}
                        class="textarea h-32"
                        placeholder="Write a brief summary of your career highlights..."
                    ></textarea>
                </div>

                <!-- Skills -->
                <div class="card p-6">
                    <h3
                        class="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2"
                    >
                        <span
                            class="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-sm"
                            >3</span
                        >
                        Skills
                    </h3>
                    <div class="flex gap-2 mb-4">
                        <input
                            type="text"
                            bind:value={skillInput}
                            on:keydown={(e: KeyboardEvent) =>
                                e.key === "Enter" && addSkill()}
                            class="input flex-1"
                            placeholder="Add a skill (e.g. Python, Project Management)"
                        />
                        <button
                            on:click={addSkill}
                            class="btn btn-secondary p-2"
                        >
                            <Plus class="w-5 h-5" />
                        </button>
                    </div>
                    <div class="flex flex-wrap gap-2">
                        {#each formData.skills as skill}
                            <span
                                class="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-gray-100 text-gray-700 text-sm font-medium"
                            >
                                {skill}
                                <button
                                    on:click={() => removeSkill(skill)}
                                    class="text-gray-400 hover:text-red-500"
                                >
                                    <Trash2 class="w-3 h-3" />
                                </button>
                            </span>
                        {/each}
                    </div>
                </div>

                <!-- Experience -->
                <div class="card p-6">
                    <div class="flex items-center justify-between mb-4">
                        <h3
                            class="text-lg font-bold text-gray-900 flex items-center gap-2"
                        >
                            <span
                                class="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-sm"
                                >4</span
                            >
                            Work Experience
                        </h3>
                        <button
                            on:click={addExperience}
                            class="btn btn-ghost text-primary-600 flex items-center gap-1 text-sm"
                        >
                            <Plus class="w-4 h-4" /> Add Experience
                        </button>
                    </div>

                    <div class="space-y-6">
                        {#each formData.experience as exp, i}
                            <div
                                class="p-4 border rounded-xl bg-gray-50 relative group"
                            >
                                <button
                                    on:click={() => removeExperience(i)}
                                    class="absolute top-2 right-2 p-1 text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                                >
                                    <Trash2 class="w-4 h-4" />
                                </button>
                                <div
                                    class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4"
                                >
                                    <div class="form-control">
                                        <label class="label" for={`title-${i}`}
                                            >Job Title</label
                                        >
                                        <input
                                            type="text"
                                            id={`title-${i}`}
                                            bind:value={exp.title}
                                            class="input bg-white"
                                            placeholder="Senior Developer"
                                        />
                                    </div>
                                    <div class="form-control">
                                        <label
                                            class="label"
                                            for={`company-${i}`}>Company</label
                                        >
                                        <input
                                            type="text"
                                            id={`company-${i}`}
                                            bind:value={exp.company}
                                            class="input bg-white"
                                            placeholder="Google"
                                        />
                                    </div>
                                    <div class="form-control md:col-span-2">
                                        <label
                                            class="label"
                                            for={`duration-${i}`}
                                            >Duration</label
                                        >
                                        <input
                                            type="text"
                                            id={`duration-${i}`}
                                            bind:value={exp.duration}
                                            class="input bg-white"
                                            placeholder="Jan 2020 - Present"
                                        />
                                    </div>
                                </div>
                                <div class="space-y-2">
                                    <label
                                        class="label font-semibold text-xs text-gray-500 uppercase"
                                        >Achievements (Bullet Points)</label
                                    >
                                    {#each exp.description as bullet, j}
                                        <div class="flex gap-2">
                                            <textarea
                                                bind:value={exp.description[j]}
                                                class="textarea bg-white h-20 text-sm"
                                                placeholder="Describe an achievement..."
                                            ></textarea>
                                            <button
                                                on:click={() =>
                                                    removeExpBullet(i, j)}
                                                class="text-gray-400 hover:text-red-500 self-start mt-2"
                                            >
                                                <Trash2 class="w-4 h-4" />
                                            </button>
                                        </div>
                                    {/each}
                                    <button
                                        on:click={() => addExpBullet(i)}
                                        class="text-xs text-primary-600 hover:underline font-medium flex items-center gap-1"
                                    >
                                        <Plus class="w-3 h-3" /> Add Bullet Point
                                    </button>
                                </div>
                            </div>
                        {/each}
                    </div>
                </div>

                <!-- Education -->
                <div class="card p-6">
                    <div class="flex items-center justify-between mb-4">
                        <h3
                            class="text-lg font-bold text-gray-900 flex items-center gap-2"
                        >
                            <span
                                class="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-sm"
                                >5</span
                            >
                            Education
                        </h3>
                        <button
                            on:click={addEducation}
                            class="btn btn-ghost text-primary-600 flex items-center gap-1 text-sm"
                        >
                            <Plus class="w-4 h-4" /> Add Education
                        </button>
                    </div>
                    <div class="space-y-4">
                        {#each formData.education as edu, i}
                            <div
                                class="p-4 border rounded-xl bg-gray-50 relative group"
                            >
                                <button
                                    on:click={() => removeEducation(i)}
                                    class="absolute top-2 right-2 p-1 text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                                >
                                    <Trash2 class="w-4 h-4" />
                                </button>
                                <div
                                    class="grid grid-cols-1 md:grid-cols-2 gap-4"
                                >
                                    <input
                                        type="text"
                                        bind:value={edu.institution}
                                        class="input bg-white"
                                        placeholder="University Name"
                                    />
                                    <input
                                        type="text"
                                        bind:value={edu.degree}
                                        class="input bg-white"
                                        placeholder="B.S. Computer Science"
                                    />
                                    <input
                                        type="text"
                                        bind:value={edu.year}
                                        class="input bg-white"
                                        placeholder="2016 - 2020"
                                    />
                                </div>
                            </div>
                        {/each}
                    </div>
                </div>
            </div>

            <!-- Right: Preview & Options -->
            <div
                class="space-y-6 {activeTab === 'edit'
                    ? 'hidden lg:block'
                    : ''}"
            >
                <!-- Download Bar -->
                <div
                    class="card p-6 sticky top-8 z-10 shadow-xl border-primary-100"
                >
                    <h3
                        class="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2"
                    >
                        <Download class="w-5 h-5 text-primary-600" />
                        Export Resume
                    </h3>

                    <div class="flex flex-col gap-4">
                        <div class="form-control">
                            <label class="label" for="template"
                                >Visual Template Style</label
                            >
                            <select
                                id="template"
                                bind:value={selectedTemplate}
                                class="select"
                            >
                                <option value="classic"
                                    >Classic (Traditional, ATS-friendly)</option
                                >
                                <option value="modern"
                                    >Modern (Clean, Navy accents)</option
                                >
                                <option value="creative"
                                    >Creative (Distinctive, Teal accents)</option
                                >
                            </select>
                        </div>

                        <button
                            on:click={handleDownload}
                            disabled={loading || !formData.full_name}
                            class="btn btn-primary w-full flex items-center justify-center gap-2 py-4 text-lg"
                        >
                            {#if loading}
                                <Loader2 class="w-6 h-6 animate-spin" />
                                Preparing PDF...
                            {:else}
                                <Download class="w-6 h-6" />
                                Download PDF
                            {/if}
                        </button>
                    </div>
                </div>

                <!-- Live Preview Display -->
                <div
                    class="card bg-gray-200 border-dashed border-2 border-gray-300 min-h-[800px] overflow-hidden flex flex-col"
                >
                    <div
                        class="bg-gray-800 text-white px-4 py-2 flex items-center justify-between"
                    >
                        <span
                            class="text-xs font-mono uppercase tracking-widest opacity-75"
                            >Live Preview</span
                        >
                        {#if !previewHtml}
                            <span
                                class="text-[10px] bg-yellow-500/20 text-yellow-300 px-2 py-0.5 rounded"
                                >Not Polished</span
                            >
                        {:else}
                            <span
                                class="text-[10px] bg-green-500/20 text-green-300 px-2 py-0.5 rounded"
                                >AI Optimized</span
                            >
                        {/if}
                    </div>

                    <div class="flex-1 bg-white p-4 overflow-auto">
                        {#if previewHtml}
                            <div class="resume-preview">
                                {@html previewHtml}
                            </div>
                        {:else}
                            <div
                                class="flex flex-col items-center justify-center h-full text-gray-400 space-y-4 text-center p-8"
                            >
                                <Wand2 class="w-16 h-16 opacity-20" />
                                <div>
                                    <p class="font-bold text-gray-500">
                                        No preview generated yet
                                    </p>
                                    <p class="text-sm">
                                        Click "Polish with AI" to see your
                                        resume come to life with professional
                                        formatting and enhanced wording.
                                    </p>
                                </div>
                            </div>
                        {/if}
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
    /* Scope styles for the generated HTML content */
    :global(.resume-preview) {
        width: 100%;
    }

    .card {
        @apply bg-white border border-gray-200 rounded-2xl transition-all duration-200;
    }

    .label {
        @apply block text-sm font-semibold text-gray-700 mb-1.5;
    }

    .input {
        @apply w-full px-4 py-2.5 rounded-xl border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-all;
    }

    .textarea {
        @apply w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-all resize-none;
    }

    .select {
        @apply w-full px-4 py-2.5 rounded-xl border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none bg-white transition-all;
    }

    .btn {
        @apply px-6 py-2.5 rounded-xl font-bold transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed transform active:scale-[0.98];
    }

    .btn-primary {
        @apply bg-primary-600 text-white hover:bg-primary-700;
    }

    .btn-secondary {
        @apply bg-secondary-100 text-secondary-700 hover:bg-secondary-200;
    }

    .btn-ghost {
        @apply bg-transparent hover:bg-gray-100;
    }
</style>
