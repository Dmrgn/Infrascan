<template>
    <div class="bg-white container w-full shadow-2xl">
        <div class="m-4 text-center">
            <h1 class="title text-4xl w-full">Analysis</h1>
            <div class="results snap-y" style="max-height: 90vh;">
                <!-- remember to add snap -->
                <div v-for="item in fetchedData.text" :key="Math.random()">
                    <div class="flex mt-4">
                        <img class="w-8 h-8 m-2" :src="iconData[item.title].icon">
                        <h1 class="capitalize text-lg">{{ item.title }}</h1>
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
            fetchedData: {
                type: String,
                default: "No results"
            },
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
    @apply text-left overflow-scroll;
}
.results h1 {
    @apply font-bold mt-2
}
</style>