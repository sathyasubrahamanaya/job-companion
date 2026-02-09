import { writable } from 'svelte/store';

export interface Toast {
    id: number;
    type: 'success' | 'error' | 'info';
    message: string;
}

function createToastStore() {
    const { subscribe, update } = writable<Toast[]>([]);
    let idCounter = 0;

    return {
        subscribe,
        show: (type: 'success' | 'error' | 'info', message: string, duration = 4000) => {
            const id = idCounter++;
            const toast: Toast = { id, type, message };

            update((toasts) => [...toasts, toast]);

            if (duration > 0) {
                setTimeout(() => {
                    update((toasts) => toasts.filter((t) => t.id !== id));
                }, duration);
            }
        },
        remove: (id: number) => {
            update((toasts) => toasts.filter((t) => t.id !== id));
        }
    };
}

export const toastStore = createToastStore();
