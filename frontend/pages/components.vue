<template>
  <!-- Copyright 2020 BULL SAS All rights reserved -->
  <div>
    <div
      class="flex w-full bg-blue-600 text-white h-20 m-auto text-2xl items-center justify-center"
    >
      Registered components
    </div>
    <div class="flex flex-wrap justify-center">
      <div
        v-for="(componentInformation, componentName) in componentsObject"
        :key="componentName"
        class="md:w-1/4 sm:w-full m-4"
      >
        <ComponentDisplay
          :componentName="componentName"
          :componentInformation="componentInformation"
        ></ComponentDisplay>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import ComponentDisplay from '../components/ComponentDisplay'

export default {
  components: { ComponentDisplay },
  data() {
    return {
      componentsObject: {}
    }
  },
  computed: {
    componentInformation() {
      return this.componentsObject[this.selected_component]
    }
  },
  mounted() {
    axios.get('/components').then((response) => {
      this.componentsObject = response.data.components
    })
  }
}
</script>
