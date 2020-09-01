<template>
  <div
    class="w-full sm:w-1/2 md:w-1/3 lg:w-1/4 xl:w-1/6 px-2"
    data-aos="fade-in"
    data-aos-duration="1500"
    data-aos-anchor-placement="top-bottom"
  >
    <nuxt-link :to="link">
      <div
        class="rounded overflow-hidden shadow h-full bg-gray-100 border-1 border-pink-200"
      >
        <img class="mx-auto mt-5 w-16" :src="computedIcon" />
        <div class="px-6 py-4">
          <div class="font-bold text-center text-xl mb-2">{{ title }}</div>
          <p class="text-gray-700 text-base text-center">
            {{ text }}
          </p>
        </div>
      </div>
    </nuxt-link>
  </div>
</template>

<script>
export default {
  props: {
    icon: {
      type: String,
      default: 'feather.svg'
    },
    title: {
      type: String,
      default: ''
    },
    text: {
      type: String,
      default: ''
    },
    link: {
      type: String,
      default: '/'
    }
  },
  computed: {
    computedIcon() {
      return require('../assets/home_icons/' + this.icon)
    }
  }
}
</script>

<style lang="stylus">
/* Import theme colors palette */
@import '../css/palette.styl';

.home-button {
    border: solid 2px $accentColor;
    color:black;
    margin: 20px;
    height: 90%;
    }

a:hover {
    text-decoration: none;
    color: $accentColor;
    }

.home-button:hover {
    background-color: $softerAccent;
    color: black;
    }

.card-title {
    font-size: 1.5rem;
    }
</style>
