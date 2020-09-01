<template>
  <!-- Flex column is used to easily center text vertically.
 -->
  <b-col>
    <div
      class="kpi shadow-xl rounded-md px-3 py-3 mt-4 bg-pink-100 border-2 border-pink-700"
    >
      <div class="text-2xl font-bold tracking-widest pt-2 pb-1">
        {{ value }}
      </div>
      <div class="text-xs md:text-sm lg:text-base text-gray-600">
        {{ description }}
      </div>
    </div>
  </b-col>
</template>

<script>
export default {
  props: {
    value: {
      type: String,
      default: '0'
    },
    description: {
      type: String,
      default: ''
    }
  },
  computed: {
    computedIcon() {
      return require('../assets/home_icons/' + this.icon)
    }
  }
}
</script>
