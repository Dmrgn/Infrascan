<template>
    <div class="bg-white container w-full shadow-2xl text-center md:h-full">
        <div class="m-4 flex flex-col relative">
            <div class="flex items-center">
                <img src="../assets/logo.png" alt="Infrascan logo" class="ml-4">
                <h1 class="title text-5xl w-full">Analysis</h1>
            </div>
            <hr class="h-px my-8 bg-gray-200 border-0">
            <div class="text-center mt-2">
                <h1 class="capitalize text-2xl">{{ fetchedData.location.a }}</h1>
            </div>
            <div class="results md:overflow-y-scroll small-results">
                <div v-for="item of fetchedData.text" :key="Math.random()">
                    <hr class="h-px my-8 bg-gray-200 border-0">
                    <div class="section-grid">
                        <div class="flex">
                            <img class="w-8 h-8 m-2" width="48" height="48" :src="(isSectionExpanded?.[item.title]) ? 'https://img.icons8.com/material-sharp/24/circled-chevron-up.png' : 'https://img.icons8.com/material-outlined/48/circled-chevron-down.png'" alt="circled-chevron-down"/>
                            <div class="flex justify-center">
                                <img class="w-8 h-8 m-2" :src="iconData[item.title].icon">
                                <h1 class="capitalize text-lg">{{ item.title }}</h1>
                            </div>
                        </div>
                        <div class="w-full bg-gray-200 rounded-full h-6 mt-2">
                            <div class="h-6 rounded-full" :style="`background-color: ${scoreToColor(fetchedData.results.results.filter((x)=>{return x.factor == item.title})[0]?.score)}; width: ${fetchedData.results.results.filter((x)=>{return x.factor == item.title})[0]?.score}%`">
                                <h2 class="font-bold ml-2">{{fetchedData.results.results.filter((x)=>{return x.factor == item.title})[0]?.score}}/100</h2>
                            </div>
                        </div>
                    </div>
                    <p>{{ item.text }}</p>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    export default {
        name: "MainAnalysis",
        props: {
            fetchedData: null,
        },
        data() {
            return {
                isSectionExpanded: {}
            }
        },
        methods: {
            scoreToColor(score) {
                const dist = (100-Math.abs((100-score) - (score)))/100 + 0.5
                return `rgb(${(100-score)/100*255*dist}, ${(score-20)/100*255*dist}, 0)`
            }
        },
        watch: {
            fetchedData(newValue, oldValue) {
                console.log(newValue);
                this.isSectionExpanded = {};
                for (const item of this.fetchedData.text) {
                    console.log(item);
                }
            }
        },
        data() {
            return {
                iconData: {
                    "grocery":{
                        "label":"G",
                        "color": "pink",
                        "icon":"https://img.icons8.com/offices/30/ingredients.png"
                    },
                    "community center":{
                        "label":"C",
                        "color": "blue",
                        "icon":"https://img.icons8.com/offices/30/children.png"
                    },
                    "park":{
                        "label":"P",
                        "color": "green",
                        "icon":"https://img.icons8.com/offices/30/park-bench.png"
                    },
                    "shopping":{
                        "label":"S",
                        "color": "gray",
                        "icon":"https://img.icons8.com/offices/30/cash-register.png"
                    },
                    "transit":{
                        "label":"T",
                        "color": "blue",
                        "icon":"https://img.icons8.com/offices/30/train.png"
                    },
                    "school":{
                        "label":"S",
                        "color": "yellow",
                        "icon":"https://img.icons8.com/offices/30/school.png"
                    },
                    "restaurant":{
                        "label":"R",
                        "color": "orange",
                        "icon":"https://img.icons8.com/offices/30/restaurant-pickup.png"
                    },
                    "home":{
                        "label":"H",
                        "color": "red",
                        "icon":"https://img.icons8.com/offices/30/cottage.png"
                    }
                }
            }
        },
    }
</script>

<style lang="css" scoped>
.results {
    @apply text-left;
}
.section-grid {
    @apply grid grid-cols-2;
}

@media (min-width: 768px) {
    .small-results {
        height: 77vh;
    }

    .section-grid {
        @apply grid grid-cols-2;
    }
}

.results h1 {
    @apply font-bold mt-2
}
</style>