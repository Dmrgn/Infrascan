<template>
    <div>
        <input :class="'address-bar'+(this.isCentered?' centered':'')" ref="input" @keypress="onButtonPress" placeholder="Enter an address here..." type="text">
    </div>
</template>

<script>
export default {
    name: "AddressBar",
    props: {
        isCentered: true
    },
    methods: {
        async onButtonPress(e) {
            if (e.key === "Enter") {
                this.$emit("onSearch", this.$refs.input.value)
            }
        },
    },
}
</script>

<style lang="css" scoped>
    .address-bar {
        @apply absolute bottom-2 left-1/2 p-4 bg-white rounded-2xl shadow-2xl outline-none;
        transform: translateX(-50%);
    }

    .centered {
        @apply bottom-1/2;
        transform: translate(-50%, 50%);
    }
</style>