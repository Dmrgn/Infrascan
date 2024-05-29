<template>
    <div class="relative h-full overflow-hidden w-full">
        <div id="map" class="h-full"></div>
        <div v-if="fetchedData != null" class="absolute left-1/2 top-4 z-[800] bg-white rounded-2xl p-2 shadow-2xl -light-200 border-2 flex items-end" style="transform: translate(-50%, 0);">
            <h2 class="title text-6xl ml-2">{{ fetchedData.score }}</h2>
            <p class="title text-sm mr-1">/ 100</p>
        </div>
        <div v-if="isLoggedIn" class="absolute right-4 top-4 z-[800] flex md:items-start md:flex-row flex-col-reverse items-end">
            <div class="box mr-2 border-light-200">
                <div class="flex h-12 items-center mx-2">
                    Tokens Remaining: <span class="font-bold text-xl ml-2">{{ userStats?.tokens }}</span>
                </div>
            </div>
            <div @click="onOpenSettings" class="bg-white rounded-2xl p-2 shadow-2xl border-light-200 border-2">
                <img class="settings-gear" width="48" height="48" src="https://img.icons8.com/material-outlined/64/settings--v1.png" alt="settings--v1"/>
            </div>
        </div>
        <AddressBar @onSearch="onSearch" :isShown="isLoggedIn" :isCentered="fetchedData == null" :addressValue="fetchedData?.location?.a"></AddressBar>
    </div>
</template>

<script>
import "leaflet/dist/leaflet.css"

import AddressBar from './AddressBar.vue';
import * as L from "leaflet/dist/leaflet-src.esm.js";

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
            contextMenu: null,
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
        const map = L.map("map", {zoomControl: false}).setView([58.559274, -91.144678], 5);
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> InfraScan',
            interactive: true,
        }).addTo(map);
        map.on("contextmenu", this.toggleContextMenu, this)
        this.homeIcon = null;
        this.map = map;
        this.contextMenu = L
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
                    if (this.homeIcon)
                        this.homeIcon.remove();
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
                    this.homeIcon = L.marker(newValue.location.g, {icon: L.icon({iconUrl: 'https://img.icons8.com/offices/30/cottage.png', iconAnchor: [16, 16], iconSize: [32, 32]})}).addTo(this.map);
                }, 2000)
            }
        }
    },
    methods: {
        onSearch(address, type) { // type is "address" or "latlng"
            this.$emit("onSearch", address, type)
        },
        onOpenSettings() {
            this.$emit("onOpenSettings")
        },
        toggleContextMenu(e) {
            this.contextMenu = L.popup()
                .setLatLng(e.latlng)
                .setContent(()=>{
                    const elm = document.createElement("input");
                    elm.value = "Analyze Here";
                    elm.classList.add("button");
                    elm.type = "button";
                    elm.onclick = ()=>{this.contextMenu.remove(); this.onSearch([e.latlng.lat, e.latlng.lng], "latlng");};
                    return elm;
                })
            this.map.openPopup(this.contextMenu);
        },

    },
}
</script>

<style lang="css" scoped>
    div:hover > .settings-gear {
        cursor:pointer;
        animation: rotate-gear 1s ease-in-out both infinite alternate-reverse;
    }
    @keyframes rotate-gear {
        from {transform: rotate(0deg);}
        to {transform: rotate(360deg);}
    }
</style>