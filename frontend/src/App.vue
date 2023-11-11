<script setup>
import MainAnalysis from './components/MainAnalysis.vue';
import MainMap from './components/MainMap.vue';
import MainError from './components/MainError.vue';
import MainLogin from './components/MainLogin.vue';
import LoadingSpinner from './components/LoadingSpinner.vue';
import MainSettings from './components/MainSettings.vue';
</script>

<template>
    <main>
        <div :class="'md:grid'+(fetchedData != null ? ' grid-cols-3' : ' grid-cols-2')" style="width: 100vw; height: 100vh;">
            <MainAnalysis v-if="fetchedData != null" :fetchedData="fetchedData"></MainAnalysis>
            <MainMap @onSearch="onSearch" @onOpenSettings="openSettings" :isLoggedIn="isLoggedIn" :userStats="userStats" :fetchedData="fetchedData"></MainMap>
        </div>
        <MainLogin @onLogin="login" @onRegister="register" @onEmailCode="sendEmailCode" :isWaitingForEmailCode="isWaitingForEmailCode" :isLoggedIn="isLoggedIn"></MainLogin>
        <MainError @onClose="error = ''" :error="error"></MainError>
        <MainSettings @onCloseSettings="isSettings=false" :isShown="isSettings" :userStats="userStats"></MainSettings>
        <LoadingSpinner :isLoading="isLoading" :serverUrl="serverUrl"></LoadingSpinner>
    </main>
</template>

<script>

export default {
    name:"App",
    data() {
        return {
            fetchedData: null,
            userStats: null,
            error: "",
            serverUrl: "https://1ca6-174-93-12-41.ngrok-free.app",
            sessionSecret: "",
            emailSecret: "",
            isLoading: false,
            isLoggedIn: false,
            isSettings: false,
            isWaitingForEmailCode: false,
        }
    },
    mounted () {
        // check to see if we have cookies indicating that we are logged in
        this.sessionSecret = localStorage.getItem("secret") ?? ""
        // fetch user stats
        if (this.sessionSecret != "") {
            this.userStats = this.fetchUserStats()
            // session is invalid if user stats request fails
            if (this.userStats == null) {
                this.sessionSecret = null;
                localStorage.removeItem("secret");
            }
        }
        this.emailSecret = localStorage.getItem("email-secret") ?? ""
        this.isLoggedIn = this.sessionSecret != ""
    },
    methods: {
        async login(email, password) { // request login secret cookie
            const response = await this.fetchData(`${this.serverUrl}/login?email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`)
            if (response === null) return;
            localStorage.setItem("secret", response["secret"]);
            this.sessionSecret = response["secret"];
            this.userStats = response["stats"];
            console.log(response);
            this.isLoggedIn = true;
        },
        async register(name, email, password) { // start registration process
            const response = await this.fetchData(`${this.serverUrl}/register?name=${encodeURIComponent(name)}&email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`)
            if (response === null) return;
            localStorage.setItem("email-secret", response["secret"]);
            this.emailSecret = response["secret"];
            this.userStats = response["stats"];
            this.isWaitingForEmailCode = true;
        },
        async sendEmailCode(code) { // finish registration by sending email confirmation code to the server
            const response = await this.fetchData(`${this.serverUrl}/emailcode?code=${encodeURIComponent(code)}&secret=${encodeURIComponent(this.emailSecret)}`)
            // clear email-secret either way to prevent users from getting stuck
            localStorage.removeItem("email-secret");
            this.isWaitingForEmailCode = false;
            if (response === null) return;
            localStorage.setItem("secret", response["secret"]);
            this.sessionSecret = response["secret"];
            this.isLoggedIn = true;
        },
        async fetchUserStats() { // request user stats with secret
            const response = await this.fetchData(`${this.serverUrl}/userstats?secret=${encodeURIComponent(this.sessionSecret)}`)
            this.userStats = response;
        },
        async onSearch(address) {
            this.fetchedData = await this.fetchData(`${this.serverUrl}/fetch?address=${address}&secret=${encodeURIComponent(this.sessionSecret)}`)
            this.userStats = this.fetchedData?.stats ?? this.userStats;
        },
        async fetchData(address) {
            window.scrollTo(0, 0);
            this.isLoading = true;
            try {
                const response = await(await fetch(address, {
                    method: "GET",
                    headers: {
                        "Ngrok-Skip-Browser-Warning": "69420",
                    }
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
                    this.userStats = null;
                }
                this.error = response.error;
                this.isLoading = false;
                return null;
            } catch (e) {
                this.error = "An error occured while communicating with our server.";
                localStorage.removeItem("email-secret");
                this.emailSecret = "";
                this.isLoading = false;
                return null;
            }
        },
        openSettings() {
            this.isSettings = true;
            window.scrollTo(0, 0);
        }
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