<template>
  <div class="m-2 w-1/4 border-2 border-pink-700 rounded-lg">
    <div class="accordion items-center justify-center p-4 font-bold">
      <a class="text-md cursor-pointer" @click="collapsed = !collapsed">
        <i
          :class="[collapsed ? 'fas fa-chevron-right' : 'fas fa-chevron-down']"
        ></i>
        {{ title }}
      </a>
    </div>
    <div v-if="!collapsed">
      <div class="text mx-3 mt-1">
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    id: {
      type: String,
      default: ''
    },
    title: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      collapsed: true
    }
  }
}
</script>
