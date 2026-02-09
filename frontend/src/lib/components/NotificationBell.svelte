<script lang="ts">
    import { onMount, onDestroy } from "svelte";
    import { getNotifications, markNotificationRead } from "$lib/api/candidate";
    import { UserRole, type Notification } from "$lib/api/types";
    import { goto } from "$app/navigation";
    import { authStore } from "$lib/stores/auth";

    let notifications: Notification[] = [];
    let unreadCount = 0;
    let isOpen = false;
    let loading = true;
    let interval: any;

    async function fetchNotifications() {
        if (!authStore.checkRole(UserRole.CANDIDATE)) {
            loading = false;
            return;
        }
        try {
            const res = await getNotifications();
            if (res.ErrorCode === 0) {
                notifications = res.Data || [];
                unreadCount = notifications.filter((n) => !n.is_read).length;
            }
        } catch (err) {
            console.error("Failed to fetch notifications", err);
        } finally {
            loading = false;
        }
    }

    // Manual mark read for UI update
    async function markNotificationReadUI(id: string) {
        try {
            await markNotificationRead(id);
            fetchNotifications();
        } catch (err) {
            console.error("Failed to mark notification as read", err);
        }
    }

    onMount(() => {
        fetchNotifications();
        // Poll every 30 seconds
        interval = setInterval(fetchNotifications, 30000);
    });

    onDestroy(() => {
        if (interval) clearInterval(interval);
    });

    async function handleRead(id: string) {
        try {
            await markNotificationRead(id);
            notifications = notifications.map((n) =>
                n.notification_id === id ? { ...n, is_read: true } : n,
            );
            unreadCount = notifications.filter((n) => !n.is_read).length;
        } catch (err) {
            console.error("Failed to mark notification as read", err);
        }
    }

    function timeAgo(dateString: string) {
        const date = new Date(dateString);
        const now = new Date();
        const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

        let interval = Math.floor(seconds / 31536000);
        if (interval >= 1) return interval + "y ago";
        interval = Math.floor(seconds / 2592000);
        if (interval >= 1) return interval + "mo ago";
        interval = Math.floor(seconds / 86400);
        if (interval >= 1) return interval + "d ago";
        interval = Math.floor(seconds / 3600);
        if (interval >= 1) return interval + "h ago";
        interval = Math.floor(seconds / 60);
        if (interval >= 1) return interval + "m ago";
        return "just now";
    }
</script>

<div class="relative">
    <button
        on:click={() => (isOpen = !isOpen)}
        class="relative p-2 text-gray-600 hover:text-primary-600 focus:outline-none transition-colors"
        aria-label="Notifications"
        title="Notifications"
    >
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
                d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
            />
        </svg>
        {#if unreadCount > 0}
            <span class="absolute top-1.5 right-1.5 flex h-4 w-4">
                <span
                    class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"
                ></span>
                <span
                    class="relative inline-flex rounded-full h-4 w-4 bg-red-500 text-[10px] text-white font-bold items-center justify-center"
                >
                    {unreadCount > 9 ? "9+" : unreadCount}
                </span>
            </span>
        {/if}
    </button>

    {#if isOpen}
        <!-- Backdrop -->
        <button
            on:click={() => (isOpen = false)}
            class="fixed inset-0 h-full w-full cursor-default z-40 outline-none"
        ></button>

        <div
            class="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-xl border border-gray-100 py-2 z-50 overflow-hidden"
        >
            <div
                class="px-4 py-2 border-b border-gray-50 flex justify-between items-center bg-gray-50/50"
            >
                <span class="font-bold text-gray-900">Notifications</span>
                {#if unreadCount > 0}
                    <span class="text-xs text-primary-600 font-medium"
                        >{unreadCount} unread</span
                    >
                {/if}
            </div>

            <div class="max-h-96 overflow-y-auto">
                {#if loading}
                    <div class="p-4 text-center text-gray-500 text-sm">
                        Loading...
                    </div>
                {:else if notifications.length === 0}
                    <div class="p-8 text-center">
                        <svg
                            class="w-12 h-12 text-gray-200 mx-auto mb-3"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0a2 2 0 01-2 2H6a2 2 0 01-2-2m16 0V9a2 2 0 00-2-2H6a2 2 0 00-2 2v2m16 4h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
                            />
                        </svg>
                        <p class="text-gray-500 text-sm">
                            No notifications yet
                        </p>
                    </div>
                {:else}
                    {#each notifications as n}
                        <button
                            class="w-full text-left p-4 border-b border-gray-50 hover:bg-gray-50 transition-colors cursor-pointer relative {n.is_read
                                ? 'opacity-75'
                                : 'bg-primary-50/30'}"
                            on:click={() => {
                                if (!n.is_read) handleRead(n.notification_id);
                                goto("/candidate/notifications");
                                isOpen = false;
                            }}
                        >
                            {#if !n.is_read}
                                <div
                                    class="absolute top-4 right-4 w-2 h-2 bg-primary-600 rounded-full"
                                ></div>
                            {/if}
                            <h4 class="font-bold text-gray-900 text-sm pr-4">
                                {n.title}
                            </h4>
                            <p
                                class="text-xs text-gray-600 mt-1 leading-relaxed line-clamp-2"
                            >
                                {n.message}
                            </p>
                            <span
                                class="text-[10px] text-gray-400 mt-2 block font-medium"
                                >{timeAgo(n.created_at)}</span
                            >
                        </button>
                    {/each}
                {/if}
            </div>

            <a
                href="/candidate/notifications"
                class="block text-center py-2 text-primary-600 text-xs font-bold hover:bg-gray-50 border-t border-gray-50"
                on:click={() => (isOpen = false)}
            >
                View all notifications
            </a>
        </div>
    {/if}
</div>
