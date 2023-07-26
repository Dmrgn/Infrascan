<template>
    <div v-if="isLoading">
        <div class="absolute top-0 left-0 blur" style="width: 100vw; height: 100vh; background-color: rgba(100,100,100,0.5);"></div>
        <div class="spinner absolute bottom-0 left-1/2" style="transform: translate(-50%, -50%);">
            <div class="absolute bottom-4 left-0 w-32 h-16 rounded-2xl bg-white flex justify-evenly items-center" style="transform: translate(-50%, -50%);">
                <div class="loading-dot dot-1"></div>
                <div class="loading-dot dot-2"></div>
                <div class="loading-dot dot-3"></div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: "LoadingSpinner",
    props: {
        isLoading: true
    },
}
</script>

<style lang="css" scoped>
    .loading-dot {
        @apply w-6 aspect-square rounded-full
    }
    @keyframes fade-1 {
        from {background-color: gray;}
        to {background-color: rgb(200, 200, 200);}
    }
    .dot-1 {
        animation: fade-1 1000ms ease-in-out 0ms infinite alternate;
    }
    .dot-2 {
        animation: fade-1 700ms ease-in-out 0ms infinite alternate;
    }
    .dot-3 {
        animation: fade-1 900ms ease-in-out 0ms infinite alternate;
    }
</style>