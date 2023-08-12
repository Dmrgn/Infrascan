<template>
    <div v-if="error != ''" class="absolute top-0 left-0 blur" style="width: 100vw; height: 100vh; background-color: rgba(100,100,100,0.5);"></div>
    <div v-if="error != ''" class="absolute top-1/2 left-1/2">
        <div class="error-box" style="transform: translate(-50%, -50%);">
            <h1 class="m-4 pt-3 my-0 text-red-400 text-lg">Error:</h1>
            <h1 class="m-4 pt-3 mt-0">
                {{ error }}
            </h1>
            <div class="self-center mb-2">
                <input @click="onClose" class="button" type="button" value="Ok">
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: "MainError",
    props: {
        error: {
            type: String,
            default: ""
        },
    },
    methods: {
        onClose() {
            this.$emit('onClose')
        }
    },
}
</script>

<style lang="css" scoped>
    .error-box {
        @apply bg-white rounded-2xl w-full h-full shadow-2xl flex flex-col;
        width: min(95vw, 400px);
        height: min(95vh, 300);
    }
</style>