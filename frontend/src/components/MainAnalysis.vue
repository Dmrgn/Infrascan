<template>
    <div class=" w-full md:w-1/4 text-center md:h-full p-4 absolute top-0 z-[800]">
        <div class="flex flex-col items-flex relative h-full">
            <div class="box mb-2 flex items-center justify-center border-light-200 shadow-xl h-44">
                <img src="../assets/logo.png" alt="Infrascan logo" class="m-4 w-32">
                <div>
                    <h1 class="w-full text-left">Analysis</h1>
                    <h1 class="title capitalize text-2xl text-left">{{ fetchedData.location.a }}</h1>
                </div>
            </div>
            <div class="md:overflow-y-scroll overflow-x-hidden">
                <AnalysisSection title="overview" :fetchedData="fetchedData" type="overview"></AnalysisSection>
                <AnalysisGroup title="Breakdown" icon="https://img.icons8.com/office/48/test-partial-passed.png">
                    <div v-for="item in fetchedData.text" :key="Math.random()">
                        <AnalysisSection :title="item.title" :fetchedData="fetchedData" type="factor"></AnalysisSection>
                    </div>
                </AnalysisGroup>
                <!-- <AnalysisGroup title="Inspect" icon="https://img.icons8.com/office/48/messaging-.png">
                    <AnalysisChat @onSendMessage="onSendMessage"></AnalysisChat>
                </AnalysisGroup> -->
            </div>
        </div>
    </div>
</template>

<script>
    import AnalysisSection from './AnalysisSection.vue';
    import AnalysisGroup from './AnalysisGroup.vue';
    import AnalysisChat from './AnalysisChat.vue';

    export default {
        name: "MainAnalysis",
        props: {
            fetchedData: null,
        },
        components: {
            AnalysisSection,
            AnalysisGroup,
            AnalysisChat
        },
        methods: {
            onSendMessage(messageContent) {
                this.$emit("onSendMessage", messageContent);
            }
        },
    }
</script>

<style lang="css" scoped>
/* hide scrollbar */
::-webkit-scrollbar {
    @apply w-0;
}

@media (min-width: 768px) {
    .small-results {
        height: 100%;
    }
}
</style>

<style>
    .expand-button {
        width: 48px;
        height: 48px;
        position: relative;
    }
    .expand-button-left {
        width: 30%;
        height: 2px;
        top:45%;
        left: 24%;
        position: absolute;
        background-color: black;
        transform: rotate(-40deg);
        transition: transform 100ms linear;
    }
    .expand-button-right {
        width: 30%;
        height: 2px;
        top: 45%;
        right: 24%;
        position: absolute;
        background-color: black;
        transform: rotate(-140deg);
        transition: transform 100ms linear;
    }
    .expand-button.expanded > .expand-button-left {
        transform: rotate(40deg);
    }
    .expand-button.expanded > .expand-button-right {
        transform: rotate(-220deg);
    }
</style>