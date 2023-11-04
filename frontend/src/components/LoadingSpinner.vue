<template>
    <div v-if="isLoading">
        <div class="absolute top-0 left-0 blur z-[800]" style="width: 100vw; height: 100vh; background-color: rgba(100,100,100,0.5);"></div>
        <div class="spinner absolute bottom-0 left-1/2 z-[800]" style="transform: translate(-50%, -50%);">
            <div class="absolute bottom-4 left-0 w-32 h-32 rounded-2xl bg-white flex justify-evenly items-center" style="transform: translate(-50%, -50%);">
                <img style="height: 115px;" src="../assets/logo.png">
                <div class="scanning-bar"></div>
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

    .scanning-bar {
        @apply absolute left-2 top-2 w-28 h-1 bg-red-500 rounded;
        animation: scan 2s linear 0s infinite alternate;
    }
    @keyframes scan {
        0% {top:10px}
        25% {top:55px}
        45% {top:45px}
        55% {top:55px}
        65% {top:65px}
        75% {top:55px}
        100% {top:90px}
    }
</style>