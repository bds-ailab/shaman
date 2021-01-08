<template>
  <!-- Copyright 2020 BULL SAS All rights reserved -->
  <div class="flex flex-col mx-auto w-2/3 border-b-2 p-4 justify-center">
    <div v-for="(value, key) in options" :key="key" class="mb-8 content-center">
      <div>
        <input
          v-if="value.type != 'static'"
          :id="value.varname"
          v-model="value.vmodel"
          :type="value.type"
          :label="value.label"
          :name="value.varname"
          :value="value.vmodel"
          :class="getInputClass(value.type)"
          class="text-pink-600 border-gray-900"
          v-tooltip.left="value.description"
        />
        <label :for="value.varname" class="font-bold text-xl ml-2">{{
          value.label
        }}</label
        ><br />

        <!-- {{ value.vmodel }} -->
      </div>
      <div>
        <div v-if="value.vmodel">
          <div
            v-for="(derivedValue, derivedKey) in value.derived_options"
            :key="derivedKey"
            class="ml-12"
          >
            <p v-tooltip.left="derivedValue.description" class="font-bold">
              {{ derivedValue.label }}
            </p>
            <div
              v-for="(option, optionKey) in derivedValue.options"
              :key="optionKey"
              class="flex flex-row"
            >
              <input
                :id="option.varname"
                v-tooltip.left="option.description"
                v-model="derivedValue.vmodel"
                :type="derivedValue.type"
                :name="derivedValue.varname"
                :value="option.varname"
                :class="getInputClass(derivedValue.type)"
                class="text-pink-600"
                required
              />
              <label
                v-tooltip.left="option.description"
                :for="option.varname"
                class="ml-2"
                >{{ option.label }}</label
              ><br />

              <div
                v-if="derivedValue.vmodel === option.varname"
                class="flex flex-row"
              >
                <div
                  v-for="(suboptionValue, suboptionKey) in option.options"
                  :key="suboptionKey"
                  class="ml-12 flex flex-col"
                >
                  <p class="font-bold">{{ suboptionValue.label }}</p>
                  <div
                    v-for="(subsubOption, subsubKey) in suboptionValue.options"
                    :key="subsubKey"
                  >
                    <input
                      :id="suboptionKey"
                      v-tooltip.left="subsubOption.description"
                      :type="suboptionValue.type"
                      :name="suboptionKey"
                      :value="subsubOption.varname"
                      :min="subsubOption.min"
                      :max="subsubOption.max"
                      :class="getInputClass(suboptionValue.type)"
                      class="text-pink-600"
                      :step="subsubOption.step"
                      required
                    />
                    <label :for="suboptionValue.varname" class="ml-2"
                      >{{ subsubOption.label }}
                      {{ subsubOption.description }}</label
                    ><br />
                  </div>
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
    options: {
      type: Object,
      default: () => {}
    }
  },
  methods: {
    getInputClass(inputType) {
      if (inputType === 'number') {
        return 'h-6 w-12 font-bold border-black border-2 rounded-sm text-center'
      } else {
        return 'form-' + inputType + ' h-6 w-6'
      }
    }
  }
  // data() {},
  //   beforeMount() {
  //     for (const [, option] of Object.entries(this.options)) {
  //       option.vmodel = false
  //     }
  //   }
}
</script>
