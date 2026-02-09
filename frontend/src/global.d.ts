import type { HTMLAttributes } from 'svelte/elements';

declare global {
    namespace svelteHTML {
        type HTMLAttributes<T> = HTMLAttributes<T>;
    }
}

export { };
