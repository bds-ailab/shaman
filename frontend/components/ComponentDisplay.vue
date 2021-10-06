<!-- Copyright 2020 BULL SAS All rights reserved -->
<template>
  <div class="rounded-md px-3 py-3 mt-4 bg-gray-100 shadow-sm h-full">
    <div class="text-xl font-semibold mb-2">
      Component name: {{ componentName }}
    </div>
    <div
      v-for="(informationValue, informationName) in componentInformation"
      :key="informationName"
    >
      <div v-if="informationValue">
        <div
          v-if="informationName.trim() != 'parameters'"
          class="flex flex-row"
        >
          <div class="text-xl text-gray-600 mr-2">{{ informationName }}:</div>
          <div class="my-auto">{{ informationValue }}</div>
        </div>
        <div v-else class="flex flex-row">
          <div class="text-xl text-gray-600">{{ informationName }}:</div>
          <div class="flex flex-wrap">
            <div
              v-for="(parameterValue, parameterName) in informationValue"
              :key="parameterName"
              class="flex flex-col mx-4 my-2"
            >
              <div class="font-bold">{{ parameterName }}</div>
              <div
                v-for="(optionValue, optionName) in parameterValue"
                :key="optionName"
              >
                <div class="flex flex-row" v-if="optionValue">
                  <p class="font-medium">{{ optionName }}</p>
                  : {{ optionValue }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    componentName: {
      type: String,
      default: 'Undefined'
    },
    componentInformation: {
      type: Object,
      default: () => {}
    }
  }
}
</script>
