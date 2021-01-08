<template>
  <!-- Copyright 2020 BULL SAS All rights reserved -->
  <!-- Button trigger modal -->
  <div :id="id" class="rounded-md mt-4 bg-gray-100 shadow-sm h-13">
    <div
      class="items-center justify-center p-4 font-bold text-center m-auto"
      v-b-modal="id"
    >
      {{ title }}
      <br />
      <i class="fas fa-plus-circle"></i>
    </div>

    <b-popover
      :target="id"
      triggers="hover"
      placement="left"
      custom-class="wide-popover"
    >
      <template><slot></slot></template>
    </b-popover>
  </div>
</template>

<script>
export default {
  props: {
    title: {
      type: String,
      default: ''
    },
    id: {
      type: String,
      default: ''
    }
  }
}
</script>

<style scoped>
.wide-popover {
  max-width: 600px;
  font-size: 1rem;
}
</style>
