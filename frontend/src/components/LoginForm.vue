<template>
    <div v-if="isRegister">
        <h2>Name</h2>
        <input ref="name" class="input-element" type="text" placeholder="your name" name="name">
    </div>
    <div>
        <h2>Email</h2>
        <input ref="email" class="input-element" type="email" placeholder="you@email.com" name="email">
    </div>
    <div>
        <h2>Password</h2>
        <input ref="password" class="input-element" type="password" placeholder="password" name="password">
    </div>
    <div v-if="isRegister">
        <h2>Confirm Password</h2>
        <input ref="confirmPassword" class="input-element" type="password" placeholder="password" name="password">
    </div>
    <div v-if="error!=''">
        <h2 class="error">{{error}}</h2>
    </div>
    <div class="self-center">
        <input v-if="!isRegister" @click="onSubmit" class="button" type="button" value="Log in">
        <input v-if="isRegister" @click="onSubmit" class="button" type="button" value="Register">
    </div>
</template>

<script>
export default {
    name: "LoginForm",
    props: {
        isRegister: false
    },
    data() {
        return {
            error: ''
        }
    },
    emits: ["onSubmit"],
    methods: {
        onSubmit() {
            // get data
            const email = this.$refs.email.value;
            const password = this.$refs.password.value;
            // if this is for registration
            if (this.isRegister) {
                const name = this.$refs.name.value;
                const confirmPassword = this.$refs.confirmPassword.value;
                // check password fields
                if (password != confirmPassword) {
                    this.error = "Passwords do not match."
                    return;
                }
                if (name.split(" ").length != 2) {
                    this.error = "Please enter your first name and last name separated by a space."
                    return;
                }
                // submit register
                this.error = '';
                this.$emit("onSubmit", {name:name, email:email, password:password, confirmPassword:confirmPassword});
                return;
            }
            // submit login
            this.error = '';
            this.$emit("onSubmit", {email:email, password:password});
        }
    },
}
</script>

<style scoped>
    .input-element {
        @apply border-b-2 p-1;
    }
    .error {
        @apply text-red-400;
    }
</style>