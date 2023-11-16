<template>
    <div class="bg-white w-full md:w-1/4 shadow-2xl text-center md:h-full p-4">
        <div class="flex flex-col items-flex relative h-full">
            <div class="flex items-center justify-center border-2 rounded-2xl border-light-200 shadow-xl h-44">
                <img src="../assets/logo.png" alt="Infrascan logo" class="m-4 w-32">
                <div>
                    <h1 class="w-full text-left">Analysis</h1>
                    <h1 class="title capitalize text-2xl text-left">{{ fetchedData.location.a }}</h1>
                </div>
            </div>
            <div class="results md:overflow-y-scroll small-results">
                <AnalysisSection title="overview" :fetchedData="fetchedData" type="overview"></AnalysisSection>
                <div v-for="item in fetchedData.text" :key="Math.random()">
                    <AnalysisSection :title="item.title" :fetchedData="fetchedData" type="factor"></AnalysisSection>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    import AnalysisSection from './AnalysisSection.vue';

    export default {
        name: "MainAnalysis",
        props: {
            fetchedData: null,
        },
        components: {
            AnalysisSection,
        },
    }
</script>

<style lang="css" scoped>


@media (min-width: 768px) {
    .small-results {
        height: 100%;
    }
}
</style>