<template>
    <div v-if="isShown">
        <div class="absolute top-0 left-0 blur" style="width: 100vw; height: 100vh; background-color: rgba(100,100,100,0.5);"></div>
        <div class="settings-box">
            <img src="../assets/logo.png" alt="Infrascan logo">
            <div class="w-full h-full flex flex-col justify-evenly items-center ml-4">
                <h1 class="font-bold">Welcome, {{ userStats.name }}</h1>
                <div class="self-start">
                    <h1 class="font-bold">Statistics</h1>
                    <h2>Tokens Used: {{ userStats.tokens_used }}</h2>
                    <h2>Account Age: {{ (new Date(userStats.account_age*1000)).toUTCString() }}</h2>
                    <h2>Is Admin Account: {{ userStats.tokens==-1?'Yes':'No' }}</h2>
                    <h2>Recent Searches: {{  userStats.searches }}</h2>
                </div>
                <h1 class="link" @click="logOut">Log Out</h1>
                <a class="link" href="https://forms.gle/HUByPmwBGCi2wdecA">Request More Tokens</a>
                <div class="self-center mb-2">
                    <input @click="onClose" class="button" type="button" value="Close">
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: "MainSettings",
    props: {
        userStats: null,
        isShown: false,
    },
    methods: {
        onClose() {
            this.$emit("onCloseSettings");
        },
        logOut() {
            localStorage.removeItem('secret');
            window.location.reload();
        }
    },
}
</script>

<style scoped>
.settings-box {
    @apply p-4 bg-white shadow-2xl absolute left-1/2 top-1/2 rounded-2xl flex flex-col items-center;
    transform: translate(-50%, -50%);
    width: min(95vw, 400px);
    height: min(95vh, 500px);
}
</style>