<template>
  <!-- Copyright 2020 BULL SAS All rights reserved -->
  <div class="flex relative pt-10 pb-20 sm:items-center md:w-2/3 mx-auto">
    <div
      class="w-24 h-12 rounded-md mt-10 sm:mt-0 inline-flex items-center justify-center bg-pink-600 text-white relative z-10 text-xl p-4"
    >
      {{ date }}
    </div>

    <div
      class="flex md:pl-8 pl-6 sm:items-center items-start flex-wrap sm:flex-row ml-2"
    >
      <h2 class="font-medium title-font text-gray-900 mb-2 text-xl">
        {{ title }}
      </h2>
      <p class="leading-relaxed mb-4">
        {{ conference }}
      </p>
      <div class="flex flex-wrap">
        <div
          v-for="author in authors"
          :key="author"
          class="px-4 py-2 bg-pink-200 shadow rounded-full mx-1 text-center mt-1 font-bold"
        >
          {{ author }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    title: {
      type: String,
      default: 'Article title'
    },
    authors: {
      type: Array[String],
      default: ['Sophie Robert']
    },
    conference: {
      type: String,
      default: 'Unpublished'
    },
    date: {
      type: Number,
      default: 2018
    }
  }
}
</script>
