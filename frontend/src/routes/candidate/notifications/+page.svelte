<script lang="ts">
    import { onMount } from "svelte";
    import {
        getNotifications,
        markNotificationRead,
        acceptInvitation,
        rejectInvitation,
        updateCandidateMemo,
    } from "$lib/api/candidate";
    import { type Notification, InvitationStatus } from "$lib/api/types";
    import { goto } from "$app/navigation";
    import { toastStore } from "$lib/stores/toast";

    let notifications: Notification[] = [];
    let loading = true;
    let memoInputs: Record<string, string> = {};
    let updatingId: string | null = null;

    async function fetchNotifications() {
        try {
            const res = await getNotifications();
            if (res.ErrorCode === 0) {
                // Sort by unread first, then by date desc
                notifications = (res.Data || []).sort((a, b) => {
                    if (a.is_read !== b.is_read) return a.is_read ? 1 : -1;
                    return (
                        new Date(b.created_at).getTime() -
                        new Date(a.created_at).getTime()
                    );
                });
                // Initialize memo inputs
                notifications.forEach((n) => {
                    if (n.notification_id && n.memo_candidate) {
                        memoInputs[n.notification_id] = n.memo_candidate;
                    }
                });
            }
        } catch (err) {
            console.error("Failed to fetch notifications", err);
            toastStore.show("error", "Failed to load notifications.");
        } finally {
            loading = false;
        }
    }

    onMount(fetchNotifications);

    async function handleRead(id: string) {
        try {
            const res = await markNotificationRead(id);
            if (res.ErrorCode === 0) {
                notifications = notifications.map((n) =>
                    n.notification_id === id ? { ...n, is_read: true } : n,
                );
            }
        } catch (err) {
            console.error("Failed to mark notification as read", err);
        }
    }

    async function handleAccept(id: string) {
        updatingId = id;
        try {
            const res = await acceptInvitation(id);
            if (res.ErrorCode === 0) {
                toastStore.show("success", "Invitation accepted!");
                fetchNotifications();
            }
        } catch (err) {
            toastStore.show("error", "Failed to accept invitation.");
        } finally {
            updatingId = null;
        }
    }

    async function handleReject(id: string) {
        updatingId = id;
        try {
            const res = await rejectInvitation(id);
            if (res.ErrorCode === 0) {
                toastStore.show("success", "Invitation rejected.");
                fetchNotifications();
            }
        } catch (err) {
            toastStore.show("error", "Failed to reject invitation.");
        } finally {
            updatingId = null;
        }
    }

    async function handleSaveMemo(id: string) {
        const memo = memoInputs[id] || "";
        updatingId = id;
        try {
            const res = await updateCandidateMemo(id, memo);
            if (res.ErrorCode === 0) {
                toastStore.show("success", "Memo updated.");
                fetchNotifications();
            }
        } catch (err) {
            toastStore.show("error", "Failed to update memo.");
        } finally {
            updatingId = null;
        }
    }

    async function markAllAsRead() {
        const unread = notifications.filter((n) => !n.is_read);
        if (unread.length === 0) return;

        try {
            await Promise.all(
                unread.map((n) => markNotificationRead(n.notification_id)),
            );
            notifications = notifications.map((n) => ({ ...n, is_read: true }));
            toastStore.show("success", "All notifications marked as read.");
        } catch (err) {
            toastStore.show("error", "Failed to mark all as read.");
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

<svelte:head>
    <title>Notifications - JobCompanion AI</title>
</svelte:head>

<div class="max-w-4xl mx-auto py-8 px-4">
    <div
        class="flex flex-col md:flex-row md:justify-between md:items-end gap-4 mb-8"
    >
        <div>
            <h1 class="text-3xl font-bold text-gray-900 tracking-tight">
                Notifications
            </h1>
            <p class="text-gray-600 mt-2">
                Manage your interview invitations and system updates in one
                place.
            </p>
        </div>
        {#if notifications.some((n) => !n.is_read)}
            <button
                on:click={markAllAsRead}
                class="text-primary-600 hover:text-primary-700 font-bold text-sm flex items-center gap-2 group transition-all"
            >
                <div
                    class="p-1.5 bg-primary-50 rounded-lg group-hover:bg-primary-100 transition-colors"
                >
                    <svg
                        class="w-4 h-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M5 13l4 4L19 7"
                        />
                    </svg>
                </div>
                Mark all as read
            </button>
        {/if}
    </div>

    {#if loading}
        <div class="space-y-4">
            {#each Array(3) as _}
                <div class="card p-6 border-gray-100 shadow-sm">
                    <div class="flex items-center gap-4 animate-pulse">
                        <div class="w-12 h-12 bg-gray-200 rounded-full"></div>
                        <div class="flex-1 space-y-3">
                            <div class="h-4 bg-gray-200 rounded w-1/4"></div>
                            <div class="h-3 bg-gray-100 rounded w-3/4"></div>
                        </div>
                    </div>
                </div>
            {/each}
        </div>
    {:else if notifications.length === 0}
        <div
            class="card p-12 text-center bg-gray-50/50 border-dashed border-2 border-gray-200"
        >
            <div
                class="w-24 h-24 bg-white rounded-full flex items-center justify-center mx-auto mb-6 shadow-sm border border-gray-100"
            >
                <svg
                    class="w-12 h-12 text-gray-300"
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
            </div>
            <h3 class="text-2xl font-bold text-gray-900 mb-2">
                Workspace clear!
            </h3>
            <p class="text-gray-500 max-w-sm mx-auto">
                You don't have any notifications at the moment. Keep building
                your profile to attract more employers!
            </p>
            <button
                on:click={() => goto("/candidate/jobs/search")}
                class="btn btn-primary mt-8 px-8"
            >
                Browse AI Matches
            </button>
        </div>
    {:else}
        <div class="space-y-4">
            {#each notifications as n}
                <div
                    class="card overflow-hidden transition-all border-l-4 {n.is_read
                        ? 'border-transparent opacity-75'
                        : 'border-primary-600 bg-white shadow-lg ring-1 ring-primary-100'}"
                >
                    <div class="p-6 flex gap-5">
                        <div class="flex-shrink-0">
                            <div
                                class="w-12 h-12 rounded-xl flex items-center justify-center {n.type ===
                                'INVITE'
                                    ? 'bg-secondary-50 text-secondary-600'
                                    : 'bg-primary-50 text-primary-600'}"
                            >
                                {#if n.type === "INVITE"}
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
                                            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                                        />
                                    </svg>
                                {:else}
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
                                            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                                        />
                                    </svg>
                                {/if}
                            </div>
                        </div>

                        <div class="flex-1 min-w-0">
                            <div class="flex justify-between items-start mb-1">
                                <h3
                                    class="text-lg font-bold text-gray-900 truncate pr-4"
                                >
                                    {n.title}
                                </h3>
                                <span
                                    class="text-xs text-gray-400 whitespace-nowrap font-medium"
                                    >{timeAgo(n.created_at)}</span
                                >
                            </div>

                            <p
                                class="text-gray-700 text-sm leading-relaxed mb-4"
                            >
                                {n.message}
                            </p>

                            {#if n.type === "INVITE"}
                                <div
                                    class="bg-gray-50 rounded-lg p-4 mb-4 border border-gray-100"
                                >
                                    <div
                                        class="flex flex-wrap items-center justify-between gap-4 mb-4"
                                    >
                                        <div class="flex items-center gap-2">
                                            <span
                                                class="text-xs font-bold text-gray-500 uppercase"
                                                >Status:</span
                                            >
                                            <span
                                                class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider {n.invitation_status ===
                                                InvitationStatus.ACCEPTED
                                                    ? 'bg-green-100 text-green-700 border border-green-200'
                                                    : n.invitation_status ===
                                                        InvitationStatus.REJECTED
                                                      ? 'bg-red-100 text-red-700 border border-red-200'
                                                      : 'bg-yellow-100 text-yellow-700 border border-yellow-200'}"
                                            >
                                                {n.invitation_status ||
                                                    "PENDING"}
                                            </span>
                                        </div>

                                        {#if !n.invitation_status || n.invitation_status === InvitationStatus.PENDING}
                                            <div class="flex gap-2">
                                                <button
                                                    on:click={() =>
                                                        handleAccept(
                                                            n.notification_id,
                                                        )}
                                                    disabled={updatingId ===
                                                        n.notification_id}
                                                    class="btn btn-primary text-[10px] py-1 px-3"
                                                >
                                                    Accept Invite
                                                </button>
                                                <button
                                                    on:click={() =>
                                                        handleReject(
                                                            n.notification_id,
                                                        )}
                                                    disabled={updatingId ===
                                                        n.notification_id}
                                                    class="btn btn-secondary text-[10px] py-1 px-3"
                                                >
                                                    Decline
                                                </button>
                                            </div>
                                        {/if}
                                    </div>

                                    {#if n.memo_employer}
                                        <div
                                            class="mb-4 bg-white p-3 rounded border border-gray-100 italic text-xs text-gray-600"
                                        >
                                            <span
                                                class="font-bold block not-italic text-gray-900 mb-1"
                                                >Employer Memo:</span
                                            >
                                            "{n.memo_employer}"
                                        </div>
                                    {/if}

                                    <div class="space-y-2">
                                        <label
                                            class="text-xs font-bold text-gray-700 block"
                                            for="memo-candidate-{n.notification_id}"
                                            >Your Memo (visible to employer):</label
                                        >
                                        <div class="flex gap-2">
                                            <input
                                                type="text"
                                                id="memo-candidate-{n.notification_id}"
                                                bind:value={
                                                    memoInputs[
                                                        n.notification_id
                                                    ]
                                                }
                                                placeholder="Add a comment or preferred date..."
                                                class="flex-1 text-xs border-gray-200 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                                            />
                                            <button
                                                on:click={() =>
                                                    handleSaveMemo(
                                                        n.notification_id,
                                                    )}
                                                disabled={updatingId ===
                                                    n.notification_id}
                                                class="btn btn-secondary text-[10px] py-1 px-3 whitespace-nowrap"
                                            >
                                                Save
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            {/if}

                            <div
                                class="flex items-center justify-between gap-4"
                            >
                                <div class="flex items-center gap-2">
                                    {#if !n.is_read}
                                        <span
                                            class="px-2 py-0.5 bg-primary-600 text-white text-[10px] font-bold rounded uppercase tracking-wider"
                                            >New</span
                                        >
                                    {/if}
                                    {#if n.type === "INVITE"}
                                        <span
                                            class="px-2 py-0.5 bg-secondary-100 text-secondary-700 text-[10px] font-bold rounded uppercase tracking-wider border border-secondary-200"
                                            >Interview Invitation</span
                                        >
                                    {/if}
                                </div>

                                <div class="flex items-center gap-3">
                                    {#if !n.is_read}
                                        <button
                                            on:click={() =>
                                                handleRead(n.notification_id)}
                                            class="text-xs font-bold text-gray-400 hover:text-primary-600 transition-colors px-3 py-1.5"
                                        >
                                            Dismiss
                                        </button>
                                    {/if}
                                    {#if n.job_id}
                                        <button
                                            on:click={() => {
                                                if (!n.is_read)
                                                    handleRead(
                                                        n.notification_id,
                                                    );
                                                goto(
                                                    `/candidate/jobs/${n.job_id}`,
                                                );
                                            }}
                                            class="btn btn-secondary text-xs py-1.5 px-4 shadow-sm border-gray-200 hover:border-primary-300"
                                        >
                                            View Job Details
                                        </button>
                                    {/if}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            {/each}
        </div>
    {/if}
</div>
