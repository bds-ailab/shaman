<template>
  <!-- Copyright 2020 BULL SAS All rights reserved -->
  <!-- Flex column is used to easily center text vertically.
 -->
  <div class="flex flex-col md:w-1/2 mr-4">
    <div class="rounded-md px-3 py-3 mt-4 bg-gray-100 shadow-sm">
      <div class="text-xl mb-2">
        {{ title }}
      </div>
      <div
        v-for="(value, name) in data"
        :key="name"
        class="flex flex-row justify-between"
      >
        <div class="text-xl text-gray-600">{{ name }} :</div>
        <div class="text-xl font-bold" v-html="value"></div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    title: {
      type: String,
      default: ''
    },
    data: {
      type: Object,
      default: () => {}
    }
  }
}
</script>
