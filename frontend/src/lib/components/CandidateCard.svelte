<script lang="ts">
    import {
        UserRole,
        InvitationStatus,
        type PotentialCandidate,
    } from "$lib/api/types";
    import {
        inviteCandidate,
        remindCandidate,
        getResumeUrl,
        updateEmployerMemo,
    } from "$lib/api/employer";
    import { toastStore } from "$lib/stores/toast";

    export let candidate: PotentialCandidate;
    export let jobId: string;

    let inviting = false;
    let invited = candidate.is_invited || false;
    let reminding = false;
    let reminded = false;

    let memoEmployerInput = candidate.memo_employer || "";
    let savingMemo = false;

    function getScoreColor(score: number) {
        if (score > 0.8) return "text-green-600 bg-green-50 border-green-200";
        if (score > 0.6) return "text-blue-600 bg-blue-50 border-blue-200";
        return "text-gray-600 bg-gray-50 border-gray-200";
    }

    async function handleInvite() {
        if (invited || inviting) return;

        inviting = true;
        try {
            const res = await inviteCandidate(candidate.candidate_id, jobId);
            if (res.ErrorCode === 0) {
                invited = true;
                toastStore.show("success", `Invite sent to ${candidate.name}!`);
            } else {
                toastStore.show(
                    "error",
                    res.Message || "Failed to send invite.",
                );
            }
        } catch (err) {
            toastStore.show(
                "error",
                "An error occurred while sending the invite.",
            );
        } finally {
            inviting = false;
        }
    }

    async function handleRemind() {
        if (reminded || reminding) return;

        reminding = true;
        try {
            const res = await remindCandidate(candidate.candidate_id, jobId);
            if (res.ErrorCode === 0) {
                reminded = true;
                toastStore.show("success", "Reminder sent!");
            } else {
                toastStore.show(
                    "error",
                    res.Message || "Failed to send reminder",
                );
            }
        } catch (err) {
            toastStore.show("error", "Error sending reminder");
        } finally {
            reminding = false;
        }
    }

    async function handleViewResume() {
        try {
            const url = getResumeUrl(candidate.candidate_id);
            const response = await fetch(url, {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem("access_token")}`,
                },
            });

            if (!response.ok) {
                if (response.status === 401) {
                    toastStore.show(
                        "error",
                        "Session expired. Please login again.",
                    );
                } else {
                    toastStore.show("error", "Failed to load resume.");
                }
                return;
            }

            const blob = await response.blob();
            const blobUrl = window.URL.createObjectURL(blob);
            window.open(blobUrl, "_blank");
        } catch (err) {
            toastStore.show(
                "error",
                "An error occurred while opening the resume.",
            );
        }
    }

    async function handleSaveEmployerMemo() {
        if (!candidate.invitation_id) return;
        savingMemo = true;
        try {
            const res = await updateEmployerMemo(
                candidate.invitation_id,
                memoEmployerInput,
            );
            if (res.ErrorCode === 0) {
                toastStore.show("success", "Memo updated.");
                candidate.memo_employer = memoEmployerInput;
            } else {
                toastStore.show(
                    "error",
                    res.Message || "Failed to update memo.",
                );
            }
        } catch (err) {
            toastStore.show("error", "Error updating memo.");
        } finally {
            savingMemo = false;
        }
    }
</script>

<div class="card hover:shadow-md transition-shadow relative overflow-hidden">
    <!-- Match Score Badge -->
    <div class="absolute top-0 right-0">
        <div
            class="px-4 py-1 rounded-bl-lg font-bold text-sm border-l border-b {getScoreColor(
                candidate.match_score,
            )}"
        >
            {Math.round(candidate.match_score * 100)}% Match
        </div>
    </div>

    <div class="flex items-start gap-4">
        <!-- Avatar Placeholder -->
        <div
            class="w-12 h-12 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 font-bold text-xl flex-shrink-0"
        >
            {candidate.name.charAt(0)}
        </div>

        <div class="flex-1 min-w-0">
            <h3 class="text-xl font-bold text-gray-900 truncate pr-20">
                {candidate.name}
            </h3>

            <div class="flex items-center gap-4 text-sm text-gray-600 mt-1">
                <span class="flex items-center gap-1">
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
                            d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                        />
                    </svg>
                    {candidate.experience_years} years exp
                </span>
                {#if candidate.locations && candidate.locations.length > 0}
                    <span class="flex items-center gap-1">
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
                                d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                            />
                        </svg>
                        {candidate.locations[0]}
                    </span>
                {/if}
            </div>

            <div class="mt-4">
                <h4
                    class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2"
                >
                    Key Skills
                </h4>
                <div class="flex flex-wrap gap-2">
                    {#each candidate.skills.slice(0, 8) as skill}
                        <span
                            class="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-md"
                        >
                            {skill}
                        </span>
                    {/each}
                    {#if candidate.skills.length > 8}
                        <span
                            class="px-2 py-1 bg-gray-50 text-gray-400 text-xs rounded-md"
                        >
                            +{candidate.skills.length - 8} more
                        </span>
                    {/if}
                </div>
            </div>

            <div class="mt-6 flex items-center gap-3">
                <button
                    on:click={handleViewResume}
                    class="btn btn-secondary text-sm py-2 px-6 shadow-sm border-gray-200 hover:border-primary-300 transition-all flex items-center gap-2"
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
                            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                        />
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                        />
                    </svg>
                    View Resume
                </button>

                {#if invited}
                    <button
                        on:click={handleRemind}
                        class="btn {reminded
                            ? 'bg-gray-100 text-gray-500 cursor-default'
                            : 'btn-primary'} text-sm py-2 px-6 flex items-center gap-2"
                        disabled={reminding || reminded}
                    >
                        {#if reminding}
                            <div
                                class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"
                            ></div>
                            <span>Reminding...</span>
                        {:else if reminded}
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
                            <span>Reminded</span>
                        {:else}
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
                                    d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                                />
                            </svg>
                            <span>Remind</span>
                        {/if}
                    </button>
                {:else}
                    <button
                        on:click={handleInvite}
                        class="btn {invited
                            ? 'bg-green-100 text-green-700 cursor-default'
                            : 'btn-primary'} text-sm py-2 px-6 flex items-center gap-2"
                        disabled={inviting || invited}
                    >
                        {#if inviting}
                            <div
                                class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"
                            ></div>
                            <span>Inviting...</span>
                        {:else if invited}
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
                            <span>Invited</span>
                        {:else}
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
                                    d="M12 4v16m8-8H4"
                                />
                            </svg>
                            <span>Invite to Interview</span>
                        {/if}
                    </button>
                {/if}
            </div>

            {#if invited}
                <div
                    class="mt-6 pt-6 border-t border-gray-50 flex flex-col gap-4"
                >
                    <div
                        class="flex items-center justify-between bg-gray-50/50 p-2 rounded-lg border border-gray-100"
                    >
                        <span
                            class="text-xs font-bold text-gray-500 uppercase px-2"
                            >Inv. Status:</span
                        >
                        <span
                            class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider {candidate.invitation_status ===
                            InvitationStatus.ACCEPTED
                                ? 'bg-green-100 text-green-700 border border-green-200'
                                : candidate.invitation_status ===
                                    InvitationStatus.REJECTED
                                  ? 'bg-red-100 text-red-700 border border-red-200'
                                  : 'bg-yellow-100 text-yellow-700 border border-yellow-200'}"
                        >
                            {candidate.invitation_status || "PENDING"}
                        </span>
                    </div>

                    {#if candidate.memo_candidate}
                        <div
                            class="bg-primary-50/30 p-3 rounded-lg border border-primary-100 italic text-xs text-gray-600"
                        >
                            <span
                                class="font-bold block not-italic text-primary-700 mb-1"
                                >Candidate's Response:</span
                            >
                            "{candidate.memo_candidate}"
                        </div>
                    {/if}

                    <div class="space-y-2">
                        <label
                            class="text-xs font-bold text-gray-700 block"
                            for="memo-employer-{candidate.candidate_id}"
                            >Employer Memo (e.g. Schedule Info):</label
                        >
                        <div class="flex gap-2">
                            <input
                                type="text"
                                id="memo-employer-{candidate.candidate_id}"
                                bind:value={memoEmployerInput}
                                placeholder="Add schedule details or notes..."
                                class="flex-1 text-xs border-gray-200 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                            />
                            <button
                                on:click={handleSaveEmployerMemo}
                                disabled={savingMemo}
                                class="btn btn-secondary text-[10px] py-1 px-3 whitespace-nowrap"
                            >
                                {savingMemo ? "Saving..." : "Save"}
                            </button>
                        </div>
                    </div>
                </div>
            {/if}
        </div>
    </div>
</div>
