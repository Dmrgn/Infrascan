<template>
    <div class="relative col-span-2 h-full">
        <div :class="'image'+(fetchedData == null ? ' is-placeholder' : '')" ref="mapImage"></div>
        <div v-if="fetchedData != null" class="score-circle">
            <h2 class="absolute bottom-4 left-1/2 title text-6xl" style="transform: translate(-50%, 0);">{{ Math.round(fetchedData.score) }}</h2>
        </div>
        <AddressBar @onSearch="onSearch" :isCentered="fetchedData == null"></AddressBar>
    </div>
</template>

<script>
import AddressBar from './AddressBar.vue';

export default {
    name: "MainMap",
    props: {
        fetchedData: null
    },
    components: {
        AddressBar,
    },
    watch: {
        // what for changes in fetched data to update the map image
        fetchedData(newValue) {
            if (newValue != null) {
                this.$refs.mapImage.style.backgroundImage = `url("${newValue.mapUrl}")`;
            }
        }
    },
    methods: {
        onSearch(address) {
            this.$emit("onSearch", address)
        }
    },
}
</script>

<style lang="css" scoped>
    .score-circle {
        @apply absolute top-0 left-1/2 bg-white shadow-2xl text-center;
        width: 164px;
        transform: translate(-50%, -50%);
        border-radius: 100%;
        aspect-ratio: 1/1;
    }
    .image {
        width: 100%;
        height: 100%;
        background-position: 50%;
        background-size: cover;
        background-image: url(https://media.wired.com/photos/59269cd37034dc5f91bec0f1/191:100/w_1280,c_limit/GoogleMapTA.jpg);
    }

    .is-placeholder {
        @apply blur-sm;
    }
</style>