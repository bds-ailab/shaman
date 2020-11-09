<template>
  <!-- Copyright 2020 BULL SAS All rights reserved -->
  <!-- Button trigger modal -->
  <div
    class="m-2 w-full sm:w-1/6 md:w-1/6 lg:w-1/6 px-2 mt-2 border-2 border-pink-700 rounded-lg"
  >
    <div
      class="items-center justify-center p-4 font-bold text-center m-auto"
      v-b-modal="id"
    >
      {{ title }}
    </div>

    <b-modal :id="id" :title="title" ok-only>
      <p class="my-4"><slot></slot></p>
    </b-modal>
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
