<!-- related to analysis group -->
<template>
    <div class="border-light-200 box mb-2">
        <div class="flex justify-stretch items-center cursor-pointer" @click="toggleExpand">
            <div :class="'expand-button ' + (isExpanded ? 'expanded' : '')">
                <div class="expand-button-left"></div>
                <div class="expand-button-right"></div>
            </div>
            <img class="w-8 h-8 m-2" :src="iconData[title]">
            <div class="mt-0 ml-2 w-full md:w-1/2">
                <h1 class="capitalize text-lg mt-0 text-left font-bold">{{ title }}</h1>
                <div class="w-full bg-gray-200 rounded-full h-6">
                    <div class="h-6 rounded-full" :style="`background-color: ${color}; width: ${score}%`">
                        <h2 class="font-bold ml-2">{{ score }}/100</h2>
                    </div>
                </div>
            </div>
        </div>
        <div v-if="isExpanded">
            <hr class="mt-3">
            <p class="m-2 text-justify">{{ content }}</p>
        </div>
    </div>
</template>

<script>

export default {
    name: "AnalysisSection",
    props: {
        fetchedData: null,
        title: null,
        type: null,
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
    created() {
        this.iconData = {
            "grocery": "https://img.icons8.com/offices/30/ingredients.png",
            "community center": "https://img.icons8.com/offices/30/children.png",
            "park": "https://img.icons8.com/offices/30/park-bench.png",
            "shopping": "https://img.icons8.com/offices/30/cash-register.png",
            "transit": "https://img.icons8.com/offices/30/train.png",
            "school": "https://img.icons8.com/offices/30/school.png",
            "restaurant": "https://img.icons8.com/offices/30/restaurant-pickup.png",
            "home": "https://img.icons8.com/offices/30/cottage.png",
            "overview": "https://img.icons8.com/office/30/search--v1.png",
        }
    },
    mounted () {
        this.updateData();
    },
    watch: {
        fetchedData(newValue, oldValue) {
            this.updateData();
        }
    },
    methods: {
        toggleExpand() {
            this.isExpanded = !this.isExpanded;
        },
        updateData() {
            switch (this.type) {
                case "factor":
                    const data = this.fetchedData.results.results.filter((x) => { return x.factor == this.title })[0];
                    this.score = data.score;
                    this.color = this.scoreToColor(this.score);
                    this.content = this.fetchedData.text[this.title].text;
                    break;
                case "overview":
                    this.score = this.fetchedData.score;
                    this.color = this.scoreToColor(this.score);
                    this.content = this.fetchedData.overview;
            }
        },
        scoreToColor(score) {
            const dist = (100 - Math.abs((100 - score) - (score))) / 100 + 0.5
            return `rgb(${(100 - score) / 100 * 255 * dist}, ${(score - 20) / 100 * 255 * dist}, 0)`
        },
    },
}
</script>

<style lang="css" scoped>
    
</style>