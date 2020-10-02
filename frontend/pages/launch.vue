<template>
  <div>
    <form ref="form" @submit.prevent="submitExperiment" v-if="componentsName">
      <!-- Row for the experiment -->
      <div class="flex flex-row mb-12 justify-center">
        <!-- Experiment parameters -->
        <div class="mx-auto w-1/3">
          <p class="text-2xl">Select experiment parameters</p>

          <div class="border-b-2 p-4">
            <label for="experiment_name" class="font-bold text-xl"
              >Experiment name:</label
            >
            <input
              id="experiment_name"
              type="text"
              name="experiment_name"
              required
              minlength="4"
              maxlength="8"
              size="10"
              class="form-textarea ml-2"
            />
          </div>

          <div class="border-b-2 p-4">
            <p class="font-bold text-xl">Components:</p>
            <div class="flex flex-row">
              <div v-for="component in componentsName" :key="component">
                <label for="component">{{ component }} </label>
                <input
                  :id="component"
                  v-model="selected_component"
                  type="radio"
                  name="component_name"
                  :value="component"
                  required
                  minlength="4"
                  maxlength="8"
                  size="10"
                  class="form-radio text-pink-600 h-6 w-6 ml-2 border-pink-900 mr-4"
                />
              </div>
            </div>
          </div>
          <div class="border-b-2 p-4">
            <p class="font-bold text-xl">Parametric space:</p>
            <div
              v-for="(parameter, parameterName) in componentParameters"
              :key="parameter"
            >
              <p class="font-bold text-xl">{{ parameterName }}</p>
              <p>
                <label for="min" class="font-bold">Minimum:</label>
                <input
                  :id="'parameter_min_' + parameterName"
                  type="number"
                  :name="'parameter_min_' + parameterName"
                  min="0"
                  class="h-6 w-12 font-bold border-pink-900 border-2
                rounded-sm text-center text-pink-600 mr-4"
                />
                <label for="max" class="font-bold">Maximum:</label>
                <input
                  :id="'parameter_max_' + parameterName"
                  type="number"
                  :name="'parameter_max_' + parameterName"
                  min="0"
                  class="h-6 w-12 font-bold border-pink-900 border-2 rounded-sm text-center text-pink-600 mr-4"
                />
                <label for="step" class="font-bold">Step:</label>
                <input
                  :id="'parameter_step_' + parameterName"
                  type="number"
                  :name="'parameter_step_' + parameterName"
                  min="0"
                  class="h-6 w-12 font-bold border-pink-900 border-2 rounded-sm text-center text-pink-600 mr-4"
                />
              </p>
            </div>
          </div>

          <div class="border-b-2 p-4">
            <label for="nbr_iteration" class="font-bold text-xl"
              >Number of iterations:</label
            >

            <input
              id="iterations"
              type="number"
              name="nbr_iteration"
              min="2"
              max="20"
              class="h-6 w-12 font-bold border-pink-900 border-2 rounded-sm text-center text-pink-600"
            />
          </div>

          <!-- Using a text input -->
          <div class="border-b-2 p-4">
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
            <textarea id="sbatch" :value="code" type="text" name="sbatch">
            </textarea>
          </div>
        </div>

        <!-- Configuration form -->

        <div class="mx-auto w-1/3">
          <p class="text-2xl">Build the configuration</p>

          <ExperimentForm :options="formOptions"></ExperimentForm>
        </div>
      </div>

      <!-- Button for starting the experiment -->
      <div class="flex flex-row">
        <div class="mx-auto">
          <button
            type="submit"
            class="border-2 rounded-md bg-pink-600 p-4 text-2xl text-white"
          >
            Run the experiment
          </button>
        </div>
      </div>
    </form>
    <div v-else class="flex flex-col items-center">
      <div class="text-2xl font-bold">
        I can't find any registered component ! Please refer to the
        documentation to add one.
      </div>
      <div>
        <img src="../assets/error_pictures/popojojo.jpg" width="500px" />
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import ExperimentForm from '../components/ExperimentForm'

export default {
  components: { ExperimentForm },
  async asyncData({ $content, params }) {
    const formOptionsFile = await $content('experimentFormOptions').fetch()
    return { formOptions: formOptionsFile.form_options }
  },
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
    })
  },
  methods: {
    onCmCodeChange(newCode) {
      this.code = newCode
    },
    submitExperiment() {
      const formData = new FormData(this.$refs.form) // reference to form element
      const data = {} // need to convert it before using not with XMLHttpRequest
      for (const [key, val] of formData.entries()) {
        console.log(key)
        console.log(val)
        Object.assign(data, { [key]: val })
      }
      console.log(data)
      axios
        .post('/experiments/launch', data)
        .then((response) => {
          this.$router.push({ path: '/browse' })
        })
        .catch(function(error) {
          alert(error)
        })
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
