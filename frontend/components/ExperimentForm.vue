<template>
  <div class="flex flex-col">
    <div
      class="border-b-2 p-4 mx-auto w-1/3"
      v-tooltip.right="
        'Enter a valid sbatch. If the sbatch is not valid, the experiment will fail.'
      "
    >
      <label for="sbatch" class="font-bold text-xl align-top"
        >Sbatch content:</label
      >
      <codemirror
        id="sbatchCm"
        name="sbatch"
        :options="cmOption"
        :v-model="code"
        :value="code"
        required
        class="form-textarea ml-2"
        @input="onCmCodeChange"
      >
      </codemirror>
      <textarea id="sbatch" :value="code" type="text" name="sbatch"> </textarea>
    </div>

    <div class="flex flex-row mx-auto">
      <div class="border-b-2 p-4">
        <p class="font-bold text-xl">Components:</p>
        <div class="flex flex-row">
          <label for="component" class="mt-2"> Select a component: </label>
          <select
            id="component"
            name="component_name"
            v-model="selected_component"
            v-tooltip.right="'The component to optimize'"
            required
            class="form-select h-10 w-52 ml-4 border-pink-900 border-solid"
          >
            <option
              v-for="component in componentsName"
              :key="component"
              :value="component"
              >{{ component }}</option
            >
          </select>
        </div>
      </div>
      <div class="border-b-2 p-4">
        <p class="font-bold text-xl">Parametric space:</p>
        <div class="flex flex-wrap justify-between">
          <div
            v-for="(parameter, parameterName) in componentParameters"
            :key="parameter"
            v-tooltip.right="
              'Fill in the minimum value, the maximum value and the step value that can take the parameter.'
            "
            class="flex flex-col ml-4"
          >
            <p class="font-bold text-xl">{{ parameterName }}</p>
            <div class="flex flex-row">
              <div class="flex flex-col my-auto mr-2">
                <label for="min" class="font-bold">Min:</label>
                <label for="max" class="font-bold">Max:</label>
                <label for="step" class="font-bold">Step:</label>
              </div>

              <div class="flex flex-col">
                <input
                  :id="'parameter_min_' + parameterName"
                  type="number"
                  :name="'parameter_min_' + parameterName"
                  min="0"
                  required
                  class="h-6 w-24 font-bold border-pink-900 border-2
                rounded-sm text-center text-pink-600 mr-4  m-auto"
                />
                <input
                  :id="'parameter_max_' + parameterName"
                  type="number"
                  :name="'parameter_max_' + parameterName"
                  min="0"
                  required
                  class="h-6 w-24 font-bold border-pink-900 border-2 rounded-sm text-center text-pink-600 mr-4  m-auto"
                />
                <input
                  :id="'parameter_step_' + parameterName"
                  type="number"
                  :name="'parameter_step_' + parameterName"
                  min="0"
                  required
                  class="h-6 w-24 font-bold border-pink-900 border-2 rounded-sm text-center text-pink-600 mr-4  m-auto"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      code: 'Write your sbatch here !',
      componentsName: null,
      selected_component: 'unknown',
      componentsObject: {},
      cmOption: {
        tabSize: 4,
        size: 5,
        styleActiveLine: true,
        lineNumbers: true,
        line: true,
        mode: 'application/x-sh',
        theme: 'erlang-dark'
      }
    }
  },
  computed: {
    componentParameters() {
      return this.componentsObject[this.selected_component]
    }
  },
  mounted() {
    axios.get('/components/parameters').then((response) => {
      this.componentsObject = response.data
      this.componentsName = Object.keys(this.componentsObject)
      console.log(this.componentsName)
    })
  },
  methods: {
    onCmCodeChange(newCode) {
      this.code = newCode
    }
  }
}
</script>

<style scoped>
/* Hide text area */
#sbatch {
  display: none;
}
</style>
