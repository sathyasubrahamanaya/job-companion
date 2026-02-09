<script lang="ts">
	import { toastStore, type Toast } from '$lib/stores/toast';
	
	let toasts: Toast[] = [];
	
	toastStore.subscribe(value => {
		toasts = value;
	});
	
	function getToastClass(type: 'success' | 'error' | 'info'): string {
		switch(type) {
			case 'success':
				return 'bg-green-50 border-green-500 text-green-800';
			case 'error':
				return 'bg-red-50 border-red-500 text-red-800';
			case 'info':
				return 'bg-blue-50 border-blue-500 text-blue-800';
		}
	}
</script>

<div class="fixed top-4 right-4 z-50 space-y-2">
	{#each toasts as toast (toast.id)}
		<div class="card border-l-4 {getToastClass(toast.type)} animate-slide-in shadow-lg max-w-md">
			<div class="flex items-start justify-between">
				<p class="font-medium">{toast.message}</p>
				<button 
					on:click={() => toastStore.remove(toast.id)}
					class="ml-4 text-gray-500 hover:text-gray-700"
				>
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
					</svg>
				</button>
			</div>
		</div>
	{/each}
</div>

<style>
	@keyframes slide-in {
		from {
			transform: translateX(100%);
			opacity: 0;
		}
		to {
			transform: translateX(0);
			opacity: 1;
		}
	}
	
	.animate-slide-in {
		animation: slide-in 0.3s ease-out;
	}
</style>
