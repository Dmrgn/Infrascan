<!-- related to analysis section -->
<template>
    <div class="flex flex-col justify-between" style="min-height: 20vh;">
        <div ref="messages" class="flex flex-col items-start overflow-y-auto overflow-x-clip" style="max-height: 25vh;">
            <div v-for="message in chatData" :key="message.message" class="box relative text-left mb-6 mx-2 mr-4" :style="'min-width: 3rem; ' + (message.from=='user' ? 'background-color:rgb(248 173 173); border-color:rgb(255,200,200); align-self:end; margin-right: 0.5rem; margin-left:1rem;':'')">
                {{ message.message }}
                <div v-if="message.from=='bot'" class="absolute bottom-{-8px} w-8 h-6" style="background: linear-gradient(to right bottom, white 0 50%, transparent 50% 100%);"></div>
                <div v-if="message.from=='user'" class="absolute bottom-{-8px} right-2 w-8 h-6" style="background: linear-gradient(to left bottom, rgb(248 173 173) 0 50%, transparent 50% 100%);"></div>
            </div>
        </div>
        <div class="flex w-full">
            <textarea ref="input" @keyup="onKeyUp" maxlength="200" :placeholder="placeholder" class="box relative text-left w-full mr-2 border-light-200 resize-none overflow-y-auto" style="max-height: 100px; min-height: 60px; background-color: transparent;"></textarea>
            <input class="button box w-12" type="button" value=">" />
        </div>
    </div>
</template>

<script>
const PLACE_HOLDERS = [
    "Create a heat map which shows the accessibility of fire stations.",
    "How many fast food resturants are in the area?",
    "Compare the schools in the area.",
    "Show me where movie theaters are located.",
    "How tall are the buildings in this area?", 
    "How long would it take me to drive to the nearest grocery store?",
];
export default {
    name: "AnalysisChat",
    props: {
        title: null,
    },
    data() {
        return {
            chatData: [
                {from:"bot", message:"Hi! Ask me questions about this analysis using the text box below."},
            ],
            placeholder: PLACE_HOLDERS[Math.floor(Math.random()*PLACE_HOLDERS.length)],
        }
    },
    methods: {
        onKeyUp(e) {
            console.log(e);
            const messageContent = this.$refs.input.value.trim();
            if (e.key === "Enter" && !e.shiftKey && messageContent.length > 0) {
                this.$emit("onSendMessage", messageContent);
                this.chatData.push({from:"user", message:messageContent});
                setTimeout(()=>{
                    this.$refs.input.value = "";
                    this.$refs.messages.scrollTop = 1e10;
                },0);
            }
        },
    },
}
</script>

<style scoped>

</style>