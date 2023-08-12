<template>
    <div>
        <h2 class="text-xl">Email Verification</h2>
    </div>
    <div class="m-4">
        <h2 class="text-center">A 6 character single-use email verification code has been sent to your inbox.<br>Please enter it below.</h2>
    </div>
    <div class="self-center">
        <input ref="code" class="input-element" type="text" placeholder="6 digit code...">
    </div>
    <div v-if="error!=''" class="m-4 text-center">
        <h2 class="text-red-400">{{error}}</h2>
    </div>
    <input @click="onEmailCode" class="button" type="button" value="Confirm">
</template>

<script>
    export default {
        name: "EmailCode",
        data() {
            return {
                error: ''
            }
        },
        methods: {
            onEmailCode() {
                const code = this.$refs.code.value;
                if (code.length != 6) {
                    this.error = "Please ensure the entered code is 6 characters long.";
                    return;
                }
                this.$emit("onEmailCode", code);
            }
        },
    }
</script>

<style scoped>
    .input-element {
        @apply border-b-2 p-1;
    }
</style>