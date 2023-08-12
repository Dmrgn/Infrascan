<template>
    <div v-if="!isLoggedIn" :class="'login-box'+(isRegister?' is-register':'')">
        <img src="../assets/logo.png" alt="Infrascan logo">
        <form class="w-full h-full">
            <div class="flex flex-col justify-evenly items-center w-full h-full">
                <LoginForm @onSubmit="onSubmit" v-if="!isWaitingForEmailCode" :isRegister="isRegister"></LoginForm>
                <EmailCode @onEmailCode="onEmailCode" v-if="isWaitingForEmailCode"></EmailCode>
            </div>
        </form>
        <span v-if="!isRegister">New? <input @click="isRegister=!isRegister" type="button" class="link" value="Register"></span>
        <span v-if="isRegister">Already have an account? <input @click="isRegister=!isRegister" type="button" class="link" value="Log in"></span>
    </div>
</template>

<script>
import LoginForm from './LoginForm.vue';
import EmailCode from './EmailCode.vue';

export default {
    name: "MainLogin",
    props: {
        isLoggedIn: false,
        isWaitingForEmailCode: false,
    },
    components: {
        LoginForm,
        EmailCode
    },
    data() {
        return {
            isRegister: false,
        }
    },
    methods: {
        onSubmit(data) {
            if (this.isRegister) {
                this.$emit("onRegister", data.name, data.email, data.password);
                return;
            }
            this.$emit("onLogin", data.email, data.password);
        },
        onEmailCode(code) {
            this.$emit("onEmailCode", code);
        },
    },
}
</script>

<style scoped>
.login-box {
    @apply p-4 bg-white shadow-2xl absolute left-1/2 top-1/2 rounded-2xl flex flex-col items-center;
    transform: translate(-50%, -50%);
    width: min(95vw, 400px);
    height: min(95vh, 500px);
}
.login-box.is-register {
    height: min(95vh, 650px);
}
</style>