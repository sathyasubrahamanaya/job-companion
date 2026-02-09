<script lang="ts">
    import "../app.css";
    import Navbar from "$lib/components/Navbar.svelte";
    import Toast from "$lib/components/Toast.svelte";
</script>

<div class="min-h-screen bg-gray-50">
    <Navbar />
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <slot />
    </main>
    <Toast />
</div>
