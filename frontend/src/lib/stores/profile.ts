import { writable } from 'svelte/store';
import type { CandidateProfile, EmployerProfile } from '$lib/api/types';

export const candidateProfile = writable<CandidateProfile | null>(null);
export const employerProfile = writable<EmployerProfile | null>(null);
