<script lang="ts">
    import { onMount } from "svelte";
    import { page } from "$app/stores";
    import { goto } from "$app/navigation";
    import { authStore } from "$lib/stores/auth";
    import { chatInteraction } from "$lib/api/interview";
    import { UserRole } from "$lib/api/types";
    import { toastStore } from "$lib/stores/toast";

    interface Message {
        sender: "user" | "ai";
        content: string;
        timestamp: Date;
    }

    let messages: Message[] = [];
    let userMessage = "";
    let loading = false;
    let chatContainer: HTMLDivElement;

    $: sessionId = $page.params.sessionId as string;

    onMount(() => {
        if (
            !$authStore.isAuthenticated ||
            $authStore.user?.role !== UserRole.CANDIDATE
        ) {
            goto("/login");
            return;
        }

        // Initial AI greeting
        messages = [
            {
                sender: "ai",
                content:
                    "Hello! I'm your AI interviewer. I'm here to help you practice for your interview. Let's get started! Can you tell me about yourself and your background?",
                timestamp: new Date(),
            },
        ];
    });

    async function sendMessage() {
        if (!userMessage.trim()) return;

        const msg = userMessage;
        userMessage = "";

        // Add user message
        messages = [
            ...messages,
            {
                sender: "user",
                content: msg,
                timestamp: new Date(),
            },
        ];

        scrollToBottom();
        loading = true;

        try {
            const response = await chatInteraction(sessionId, msg);
            const aiResponse =
                response.Data?.response ||
                response.Data?.message || // Fallback for consistency
                "I'm sorry, I didn't quite understand that. Could you rephrase?";

            messages = [
                ...messages,
                {
                    sender: "ai",
                    content: aiResponse,
                    timestamp: new Date(),
                },
            ];

            scrollToBottom();
        } catch (err: any) {
            toastStore.show("error", "Failed to send message");
        } finally {
            loading = false;
        }
    }

    function scrollToBottom() {
        setTimeout(() => {
            if (chatContainer) {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        }, 100);
    }

    function endInterview() {
        toastStore.show("success", "Interview session ended");
        goto("/candidate/jobs/search");
    }
</script>

<svelte:head>
    <title>AI Interview - JobCompanion AI</title>
</svelte:head>

<div class="max-w-4xl mx-auto">
    <div class="card h-[calc(100vh-12rem)] flex flex-col">
        <!-- Header -->
        <div
            class="flex items-center justify-between pb-4 border-b border-gray-200"
        >
            <div>
                <h1 class="text-2xl font-bold text-gray-900">
                    AI Interview Session
                </h1>
                <p class="text-sm text-gray-600">Session ID: {sessionId}</p>
            </div>
            <button on:click={endInterview} class="btn btn-secondary">
                End Interview
            </button>
        </div>

        <!-- Messages -->
        <div
            bind:this={chatContainer}
            class="flex-1 overflow-y-auto py-4 space-y-4"
        >
            {#each messages as message}
                <div
                    class="flex {message.sender === 'user'
                        ? 'justify-end'
                        : 'justify-start'}"
                >
                    <div class="max-w-[70%]">
                        <div
                            class="flex items-start gap-2 {message.sender ===
                            'user'
                                ? 'flex-row-reverse'
                                : ''}"
                        >
                            <div
                                class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 {message.sender ===
                                'user'
                                    ? 'bg-primary-600'
                                    : 'bg-secondary-600'}"
                            >
                                {#if message.sender === "user"}
                                    <span
                                        class="text-white text-xs font-semibold"
                                        >{$authStore.user?.name?.charAt(0) ||
                                            "U"}</span
                                    >
                                {:else}
                                    <svg
                                        class="w-5 h-5 text-white"
                                        fill="none"
                                        stroke="currentColor"
                                        viewBox="0 0 24 24"
                                    >
                                        <path
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                            stroke-width="2"
                                            d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                                        />
                                    </svg>
                                {/if}
                            </div>
                            <div>
                                <div
                                    class="px-4 py-2 rounded-lg {message.sender ===
                                    'user'
                                        ? 'bg-primary-600 text-white'
                                        : 'bg-gray-100 text-gray-900'}"
                                >
                                    <p class="whitespace-pre-line">
                                        {message.content}
                                    </p>
                                </div>
                                <p
                                    class="text-xs text-gray-500 mt-1 {message.sender ===
                                    'user'
                                        ? 'text-right'
                                        : ''}"
                                >
                                    {message.timestamp.toLocaleTimeString([], {
                                        hour: "2-digit",
                                        minute: "2-digit",
                                    })}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            {/each}

            {#if loading}
                <div class="flex justify-start">
                    <div class="max-w-[70%]">
                        <div class="flex items-start gap-2">
                            <div
                                class="w-8 h-8 rounded-full bg-secondary-600 flex items-center justify-center"
                            >
                                <svg
                                    class="w-5 h-5 text-white"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                >
                                    <path
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        stroke-width="2"
                                        d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                                    />
                                </svg>
                            </div>
                            <div class="px-4 py-2 bg-gray-100 rounded-lg">
                                <div class="flex gap-1">
                                    <div
                                        class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                                        style="animation-delay: 0ms"
                                    ></div>
                                    <div
                                        class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                                        style="animation-delay: 150ms"
                                    ></div>
                                    <div
                                        class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                                        style="animation-delay: 300ms"
                                    ></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            {/if}
        </div>

        <!-- Input -->
        <div class="pt-4 border-t border-gray-200">
            <form on:submit|preventDefault={sendMessage} class="flex gap-2">
                <input
                    type="text"
                    bind:value={userMessage}
                    placeholder="Type your response..."
                    class="input flex-1"
                    disabled={loading}
                />
                <button
                    type="submit"
                    class="btn btn-primary px-6"
                    disabled={loading || !userMessage.trim()}
                >
                    Send
                </button>
            </form>
        </div>
    </div>
</div>
