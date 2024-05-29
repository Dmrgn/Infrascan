<!-- related to analysis section -->
<template>
    <div class="border-light-200 box mb-2">
        <div class="flex justify-stretch items-center cursor-pointer" @click="toggleExpand">
            <div :class="'expand-button ' + (isExpanded ? 'expanded' : '')">
                <div class="expand-button-left"></div>
                <div class="expand-button-right"></div>
            </div>
            <img v-if="icon!==null" class="w-8 h-8 m-2" :src="icon">
            <h1 class="capitalize text-lg mt-0 text-left font-bold">{{ title }}</h1>
        </div>
        <div v-if="isExpanded">
            <slot></slot>
        </div>
    </div>
</template>

<script>
export default {
    name: "AnalysisGroup",
    props: {
        title: null,
        icon: null
    },
    data() {
        return {
            isExpanded: false,
            score: null,
            color: null,
            content: null,
            iconData: null,
        }
    },
    methods: {
        toggleExpand() {
            this.isExpanded = !this.isExpanded;
        },
    },
}
</script>

<style lang="scss" scoped>

</style>