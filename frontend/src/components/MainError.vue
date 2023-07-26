<template>
    <div v-if="error != ''" class="absolute top-1/2 left-1/2 w-1/6 h-1/6">
        <div class="bg-white rounded-2xl w-full h-full shadow-2xl" style="transform: translate(-50%, -50%);">
            <h1 class="m-4 pt-3 mt-0">
                {{ error }}
            </h1>
            <input @click="onClose" class="absolute bottom-0 bg-gray-200 left-1/2 w-1/6 rounded hover:bg-blue-400 transition-colors" style="transform: translate(-50%, -50%);" type="button" value="Ok">
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

</style>