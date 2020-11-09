<template>
  <!-- Copyright 2020 BULL SAS All rights reserved -->
  <div class="container">
    <div class="flex flex-col w-full min-h-screen">
      <div class="flew flex-row w-full">
        <h1
          class="text-left text-blue-900 font-semibold tracking-wide text-2xl md:text-3xl xm:text-4xl"
        >
          Publications related to the SHAMan framework
        </h1>
      </div>
      <div class="mt-8">
        <PublicationItem
          v-for="publication in publications"
          :key="publication.title"
          :date="publication.date"
          :title="publication.title"
          :authors="publication.authors"
          :conference="publication.conference"
        ></PublicationItem>
      </div>
    </div>
  </div>
</template>

<script>
import PublicationItem from '~/components/PublicationItem.vue'

export default {
  components: {
    PublicationItem
  },
  async asyncData({ $content, params }) {
    const relatedWorks = await $content('publications').fetch()
    return { publications: relatedWorks.publications }
  }
}
</script>
