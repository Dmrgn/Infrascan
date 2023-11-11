<template>
    <div class="relative col-span-2 h-full overflow-hidden">
        <div id="map" class="h-full"></div>
        
        <div v-if="fetchedData != null" class="score-circle">
            <h2 class="absolute bottom-4 left-1/2 title text-6xl" style="transform: translate(-50%, 0);">{{ Math.round(fetchedData.score) }}</h2>
        </div>
        <div v-if="isLoggedIn" class="absolute right-4 top-4 z-[800] flex md:items-start md:flex-row flex-col-reverse items-end">
            <div class="bg-white rounded-2xl p-4 shadow-2xl md:mr-4 md:mt-0 mt-4">
                Tokens Remaining: <span class="font-bold text-xl">{{ userStats?.tokens }}</span>
            </div>
            <div @click="onOpenSettings" class="bg-white rounded-2xl p-2 shadow-2xl">
                <img class="settings-gear" width="64" height="64" src="https://img.icons8.com/material-outlined/64/settings--v1.png" alt="settings--v1"/>
            </div>
        </div>
        <AddressBar @onSearch="onSearch" :isShown="isLoggedIn" :isCentered="fetchedData == null" :addressValue="fetchedData?.location?.a"></AddressBar>
    </div>
</template>

<script>
import "leaflet/dist/leaflet.css"

import AddressBar from './AddressBar.vue';
import * as L from "leaflet/src/Leaflet.js";

export default {
    name: "MainMap",
    props: {
        fetchedData: null,
        isLoggedIn: false,
        userStats: null,
    },
    data() {
        return {
            map: [],
            polygons: [],
            homeIcon: null,
            colorCodes: {
                "grocery": "orange",
                "park": "green",
                "school": "brown",
                "shopping": "blue",
                "transit": "grey",
                "community center": "yellow",
                "restaurant": "purple"
            },
        }
    },
    mounted () {
        const map = L.map("map", {}).setView([58.559274, -91.144678], 5);
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> InfraScan'
        }).addTo(map);
        this.homeIcon = L.icon({iconUrl: 'https://img.icons8.com/offices/30/cottage.png', iconAnchor: [16, 16], iconSize: [32, 32]})
        this.map = map;
    },
    components: {
        AddressBar,
    },
    watch: {
        // wait for changes in fetched data to update the map image
        fetchedData(newValue) {
            if (newValue != null) {
                this.map.flyTo(newValue.location.g, 15, {
                    animate:true,
                    duration: 2,
                });
                setTimeout(()=>{
                    for (const polygon of this.polygons) {
                        polygon.remove();
                    }
                    for (const factor of newValue.results.results) {
                        for (const element of factor.results) {
                            const latlngs = element.geometry.map((x)=>{return [x.lat, x.lng]});
                            let polygon = null;
                            if (latlngs.length == 1) {
                                polygon = L.circle(latlngs[0], {color: this.colorCodes[factor.factor], radius: 10}).addTo(this.map);
                            } else {
                                polygon = L.polygon(latlngs, {color: this.colorCodes[factor.factor]}).addTo(this.map);
                            }
                            polygon.bindPopup(`${factor.factor}: ${element.name}`);
                            this.polygons.push(polygon);
                        }
                    }
                    this.polygons.push(L.marker(newValue.location.g, {icon: this.homeIcon}).addTo(this.map));
                }, 2000)
            }
        }
    },
    methods: {
        onSearch(address) {
            this.$emit("onSearch", address)
        },
        onOpenSettings() {
            this.$emit("onOpenSettings")
        }
    },
}
</script>

<style lang="css" scoped>
    .score-circle {
        @apply absolute top-0 left-1/2 bg-white shadow-2xl text-center z-[800];
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
    div:hover > .settings-gear {
        cursor:pointer;
        animation: rotate-gear 1s ease-in-out both infinite alternate-reverse;
    }
    @keyframes rotate-gear {
        from {transform: rotate(0deg);}
        to {transform: rotate(360deg);}
    }
</style>