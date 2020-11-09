<template>
  <!-- Copyright 2020 BULL SAS All rights reserved -->
  <div class="main">
    <logo />
    <div class="hero mx-auto text-center text-6xl font-bold">
      SHAMan UI
    </div>
    <div class="mx-auto text-center text-2xl font-semibold">
      UI for Smart HPC Application MANager
    </div>
    <div class="flex flex-wrap mt-8 -mx-2 justify-center">
      <HomeButtons
        v-for="button in buttons"
        :key="button.title"
        :icon="button.icon"
        :title="button.title"
        :text="button.text"
        :link="button.link"
      ></HomeButtons>
    </div>
  </div>
</template>

<script>
import Logo from '~/components/Logo.vue'
import HomeButtons from '~/components/HomeButtons'

export default {
  components: {
    Logo,
    HomeButtons
  },
  data() {
    return {
      buttons: [
        {
          icon: 'microscope.png',
          title: 'Explore experiments',
          text: 'Analyze previously run experiments',
          link: '/browse'
        },
        {
          icon: 'chemist.png',
          title: 'Create new experiment',
          text: 'Define and launch a new experiment',
          link: '/launch'
        },
        {
          icon: 'report.png',
          title: 'Read the documentation',
          text: 'Access the user and the technical documentation',
          link: '/documentation'
        },
        {
          icon: 'molecules.png',
          title: 'Related works',
          text: 'Read different publications about the SHAMan project',
          link: '/relatedworks'
        }
      ]
    }
  }
}
</script>

<style>
.main {
  max-height: 100vh;
}

.title {
  font-family: 'Quicksand', 'Source Sans Pro', -apple-system, BlinkMacSystemFont,
    'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  display: block;
  font-weight: 300;
  font-size: 100px;
  color: #35495e;
  letter-spacing: 1px;
}

.subtitle {
  font-weight: 300;
  font-size: 42px;
  color: #526488;
  word-spacing: 5px;
  padding-bottom: 15px;
}
</style>
