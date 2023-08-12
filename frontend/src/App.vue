<script setup>
import MainAnalysis from './components/MainAnalysis.vue';
import MainMap from './components/MainMap.vue';
import MainError from './components/MainError.vue';
import MainLogin from './components/MainLogin.vue';
import LoadingSpinner from './components/LoadingSpinner.vue';
</script>

<template>
    <main>
        <div :class="'grid'+(fetchedData != null ? ' grid-cols-3' : ' grid-cols-2')" style="width: 100vw; height: 100vh;">
            <MainAnalysis v-if="fetchedData != null" :fetchedData="fetchedData"></MainAnalysis>
            <MainMap @onSearch="onSearch" :isLoggedIn="isLoggedIn" :fetchedData="fetchedData"></MainMap>
        </div>
        <MainLogin @onLogin="login" @onRegister="register" @onEmailCode="sendEmailCode" :isWaitingForEmailCode="isWaitingForEmailCode" :isLoggedIn="isLoggedIn"></MainLogin>
        <MainError @onClose="this.error = ''" :error="error"></MainError>
        <LoadingSpinner :isLoading="isLoading" :serverUrl="serverUrl"></LoadingSpinner>
    </main>
</template>

<script>
import { useCookies } from "vue3-cookies";
const { cookies } = useCookies();

export default {
    name:"App",
    data() {
        return {
            fetchedData: null,
            error: "",
            serverUrl: "http://127.0.0.1:5000",
            sessionSecret: "",
            emailSecret: "",
            isLoading: false,
            isLoggedIn: false,
            isWaitingForEmailCode: false,
        }
    },
    mounted () {
        // check to see if we have cookies indicating that we are logged in
        this.sessionSecret = localStorage.getItem("secret") ?? ""
        this.emailSecret = localStorage.getItem("email-secret") ?? ""
        this.isLoggedIn = this.sessionSecret != ""
    },
    methods: {
        async login(email, password) { // request login secret cookie
            const response = await this.fetchData(`${this.serverUrl}/login?email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`)
            if (response === null) return;
            localStorage.setItem("secret", response["secret"]);
            this.sessionSecret = response["secret"];
            this.isLoggedIn = true;
        },
        async register(name, email, password) { // start registration process
            const response = await this.fetchData(`${this.serverUrl}/register?name=${encodeURIComponent(name)}&email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`)
            if (response === null) return;
            localStorage.setItem("email-secret", response["secret"]);
            this.emailSecret = response["secret"];
            this.isWaitingForEmailCode = true;
        },
        async sendEmailCode(code) { // finish registration by sending email confirmation code to the server
            const response = await this.fetchData(`${this.serverUrl}/emailcode?code=${encodeURIComponent(code)}&secret=${encodeURIComponent(this.emailSecret)}`)
            if (response === null) return;
            localStorage.removeItem("email-secret");
            localStorage.setItem("secret", response["secret"]);
            this.sessionSecret = response["secret"];
            this.isWaitingForEmailCode = false;
            this.isLoggedIn = true;
        },
        async onSearch(address) {
            this.fetchedData = await this.fetchData(`${this.serverUrl}/fetch?address=${address}&secret=${encodeURIComponent(this.sessionSecret)}`)
            // this.fetchedData = {
            //     "results": [{
            //         "description": "grocery",
            //         "results": [{
            //             "distance": 0.5028478109028561,
            //             "g": {
            //                 "lat": 43.84922299999999,
            //                 "lng": -79.53276900000002
            //             },
            //             "name": "Fortinos Vaughan Major MacKenzie",
            //             "rating": 4.4,
            //             "score": 8.750162384320342,
            //             "types": ["grocery_or_supermarket", "pharmacy", "bakery", "store", "health", "food", "point_of_interest", "establishment"]
            //         }, {
            //             "distance": 0.532776682241682,
            //             "g": {
            //                 "lat": 43.8448273,
            //                 "lng": -79.5350888
            //             },
            //             "name": "Maple Grocery",
            //             "rating": 3.9,
            //             "score": 7.3201401825443515,
            //             "types": ["grocery_or_supermarket", "store", "food", "point_of_interest", "establishment"]
            //         }, {
            //             "distance": 0.8867134387068373,
            //             "g": {
            //                 "lat": 43.8516657,
            //                 "lng": -79.5361581
            //             },
            //             "name": "Longo's Maple",
            //             "rating": 4.1,
            //             "score": 4.623816242121408,
            //             "types": ["supermarket", "grocery_or_supermarket", "bakery", "store", "food", "point_of_interest", "establishment"]
            //         }],
            //         "score": 20.6941188089861
            //     }, {
            //         "description": "community center",
            //         "results": [{
            //             "distance": 0.860398389075355,
            //             "g": {
            //                 "lat": 43.8520117,
            //                 "lng": -79.5221134
            //             },
            //             "name": "Mario Ferri",
            //             "rating": 3,
            //             "score": 3.486756876920716,
            //             "types": ["point_of_interest", "establishment"]
            //         }],
            //         "score": 3.486756876920716
            //     }, {
            //         "description": "park",
            //         "results": [{
            //             "distance": 0.7705819759551665,
            //             "g": {
            //                 "lat": 43.8389185,
            //                 "lng": -79.5283778
            //             },
            //             "name": "Brett Yerex Park",
            //             "rating": 4.2,
            //             "score": 5.450425952143425,
            //             "types": ["park", "point_of_interest", "establishment"]
            //         }, {
            //             "distance": 0.3545628004243003,
            //             "g": {
            //                 "lat": 43.8447912,
            //                 "lng": -79.53276939999999
            //             },
            //             "name": "Emmitt Road Park",
            //             "rating": 4.2,
            //             "score": 11.845574310034555,
            //             "types": ["park", "point_of_interest", "establishment"]
            //         }, {
            //             "distance": 0.2742219457719119,
            //             "g": {
            //                 "lat": 43.8434324,
            //                 "lng": -79.5292948
            //             },
            //             "name": "West Maple Creek Park",
            //             "rating": 4.2,
            //             "score": 15.316060821380837,
            //             "types": ["park", "point_of_interest", "establishment"]
            //         }],
            //         "score": 32.612061083558814
            //     }, {
            //         "description": "shopping",
            //         "results": [{
            //             "distance": 0.5240042283351586,
            //             "g": {
            //                 "lat": 43.8454411,
            //                 "lng": -79.53510729999999
            //             },
            //             "name": "Peace plaza",
            //             "rating": 4.3,
            //             "score": 8.206040652881287,
            //             "types": ["shopping_mall", "point_of_interest", "establishment"]
            //         }],
            //         "score": 8.206040652881287
            //     }, {
            //         "description": "transit",
            //         "results": [{
            //             "distance": 0.8513152102148265,
            //             "g": {
            //                 "lat": 43.8384335,
            //                 "lng": -79.525945
            //             },
            //             "name": "Melville Av / Parktree Dr",
            //             "rating": 3,
            //             "score": 3.5239591211379393,
            //             "types": ["transit_station", "point_of_interest", "establishment"]
            //         }, {
            //             "distance": 0.39131504795793104,
            //             "g": {
            //                 "lat": 43.84251949999999,
            //                 "lng": -79.530187
            //             },
            //             "name": "Melville Av / Eddington Pl",
            //             "rating": 3,
            //             "score": 7.666457029075253,
            //             "types": ["transit_station", "point_of_interest", "establishment"]
            //         }, {
            //             "distance": 0.20159434240402815,
            //             "g": {
            //                 "lat": 43.8467525,
            //                 "lng": -79.53077499999999
            //             },
            //             "name": "Melville Av / Avro Rd",
            //             "rating": 3,
            //             "score": 14.881370003864035,
            //             "types": ["transit_station", "point_of_interest", "establishment"]
            //         }],
            //         "score": 26.071786154077227
            //     }, {
            //         "description": "school",
            //         "results": [{
            //             "distance": 0.3832589528281903,
            //             "g": {
            //                 "lat": 43.84300409999999,
            //                 "lng": -79.5258947
            //             },
            //             "name": "Maple Creek Public School",
            //             "rating": 3.8,
            //             "score": 9.914967339858823,
            //             "types": ["primary_school", "point_of_interest", "school", "establishment"]
            //         }, {
            //             "distance": 0.8733737977756257,
            //             "g": {
            //                 "lat": 43.8500868,
            //                 "lng": -79.5194296
            //             },
            //             "name": "Joseph A. Gibson Public School",
            //             "rating": 3.4,
            //             "score": 3.8929493976798666,
            //             "types": ["point_of_interest", "school", "establishment"]
            //         }, {
            //             "distance": 0.7296291385010508,
            //             "g": {
            //                 "lat": 43.8395045,
            //                 "lng": -79.53093090000002
            //             },
            //             "name": "Maple High School",
            //             "rating": 3.6,
            //             "score": 4.9340134734693235,
            //             "types": ["secondary_school", "point_of_interest", "school", "establishment"]
            //         }],
            //         "score": 18.741930211008015
            //     }, {
            //         "description": "restaurant",
            //         "results": [{
            //             "distance": 0.6963202517249836,
            //             "g": {
            //                 "lat": 43.8489993,
            //                 "lng": -79.5360999
            //             },
            //             "name": "Kelseys Original Roadhouse",
            //             "rating": 4.1,
            //             "score": 5.88809529787929,
            //             "types": ["restaurant", "food", "point_of_interest", "establishment"]
            //         }, {
            //             "distance": 0.5855672105442582,
            //             "g": {
            //                 "lat": 43.8471337,
            //                 "lng": -79.5356779
            //             },
            //             "name": "Pita Land Maple",
            //             "rating": 4.4,
            //             "score": 7.514081937597564,
            //             "types": ["restaurant", "food", "point_of_interest", "establishment"]
            //         }, {
            //             "distance": 0.5351933018500519,
            //             "g": {
            //                 "lat": 43.8432362,
            //                 "lng": -79.5342041
            //             },
            //             "name": "Pollo Loco Churrasqueria",
            //             "rating": 4.7,
            //             "score": 8.781873733757651,
            //             "types": ["restaurant", "food", "point_of_interest", "establishment"]
            //         }],
            //         "score": 22.184050969234505
            //     }],
            //     "score": 18.856677822380952,
            //     "text": [
            //         {"title":"Grocery Stores", "text":"The property is conveniently located near several grocery stores, including Parkway Fine Foods, All Season Food Market, and Sobeys Urban Fresh Rosebury Square. These grocery options provide residents with easy access to fresh produce and daily essentials, making grocery shopping a convenient and enjoyable experience."},
            //         {"title":"Community Center", "text":"Within a reasonable distance from the property, residents can find the Fairbank Memorial Community Recreation Centre. This center offers various recreational programs, sports facilities, and community events. It serves as a hub for residents to come together, engage in activities, and foster a strong sense of community spirit."},
            //         {"title":"Parks", "text":"The area boasts several parks, such as Cy Townsend Park, Glen Cedar Park, and Cedarvale Park. These green spaces offer a wonderful opportunity for outdoor activities, picnics, and social gatherings. The presence of nearby parks enhances the quality of life for residents, providing them with spaces for relaxation and recreational pursuits."},
            //         {"title":"Shopping", "text":"The Upper Village, a shopping mall located close to the property, offers a range of retail outlets and services. This allows residents to conveniently access shopping options without having to travel far."},
            //         {"title":"Transit", "text":"With transit stations like Marlee Ave at Roselawn Ave, Marlee Ave at Whitmore Ave, and Vaughan Rd at Arlington Ave nearby, residents can easily commute to various destinations within the city. This accessibility to public transportation encourages sustainability and reduces dependency on private vehicles."},
            //         {"title":"Schools", "text":"Families with children will appreciate the proximity to schools such as Cedarvale Community School, West Preparatory Junior Public School, and Humewood Community School. These educational institutions provide convenient access to quality education for the younger members of the community."},
            //         {"title":"Restaurants", "text":"The area offers a diverse range of dining options, including Restaurant Canadian Caribbean, Crystal's Eatery, and Hot Pot Restaurant. These restaurants provide residents with various culinary experiences, making dining out a delightful social activity."},
            //     ],
            //     "overview": "Overall, the property's surroundings present a dynamic and inviting community atmosphere, making it an attractive choice for individuals or families seeking an active and involved lifestyle.",
            //     "mapUrl": "https://media.wired.com/photos/59269cd37034dc5f91bec0f1/master/w_2560%2Cc_limit/GoogleMapTA.jpg"
            // };
        },
        async fetchData(address) {
            this.isLoading = true;
            try {
                const response = await(await fetch(address, {
                    method: "GET",
                    headers: {
                        "Ngrok-Skip-Browser-Warning": "69420",
                    },
                    credentials: "include"
                })).json()
                if (response["error"] == undefined) {
                    this.isLoading = false;
                    return response
                }
                if (response["login"] != undefined) {
                    this.isLoggedIn = false;
                    localStorage.removeItem("secret");
                    localStorage.removeItem("email-secret");
                    this.sessionSecret = "";
                    this.emailSecret = "";
                }
                this.error = response.error;
                this.isLoading = false;
                return null;
            } catch (e) {
                this.error = "An error occured while communicating with our server.";
                this.isLoading = false;
                return null;
            }
        },
    },
}
</script>

<style>
.button {
    @apply rounded bg-gray-200 p-4 hover:bg-red-400 hover:text-white transition-colors cursor-pointer;
}
.link {
    @apply underline text-red-400 hover:text-gray-400 cursor-pointer;
}
</style>