<template>
  <!-- Copyright 2020 BULL SAS All rights reserved -->
  <div>
    <form ref="form" @submit.prevent="submitExperiment">
      <!-- Fill out parameters of the experiment -->
      <div class="flex flex-row justify-around">
        <div>
          <button v-on:click="showExperiment()">
            <span
              v-bind:class="{
                underline: experimentShow,
                'no-underline': !experimentShow
              }"
              >Parametrize experiment</span
            >
          </button>
        </div>
        <div>
          <button v-on:click="showBBO()">
            <span
              v-bind:class="{ underline: bboShow, 'no-underline': !bboShow }"
              >Parametrize optimizer</span
            >
          </button>
        </div>
        <div>
          <button v-on:click="validate()">
            <i class="fas fa-check-circle"></i>
            Finalize experiment
          </button>
        </div>
      </div>
      <ExperimentForm v-show="experimentShow & !validateExperiment" />

      <!-- Fill out parameters of BBO -->
      <BBOForm v-if="bboShow & !validateExperiment" :options="formOptions" />

      <div v-if="validateExperiment" class="flex flex-col justify-items-center">
        <ValidateForm />
        <div class="mx-auto">
          <button
            type="submit"
            class="border-2 rounded-md bg-pink-600 p-4 text-xl text-white"
          >
            Run the experiment
          </button>
        </div>
      </div>

      <!-- Validate form + give name to the experiment -->
    </form>

    <!-- <form ref="form" @submit.prevent="submitExperiment" v-if="componentsName">
    
      <div class="flex flex-wrap justify-center">
        
        <div class="w-full md:w-1/3 lg:w-1/3 mx-auto">
          <div>
            <p class="text-2xl">Select experiment parameters</p>
          </div> -->

    <!-- <div class="border-b-2 p-4">
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
              v-tooltip.right="'Name to identify the experiment'"
            />
          </div> -->

    <!-- <div
            class="border-b-2 p-4"
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
            <textarea id="sbatch" :value="code" type="text" name="sbatch">
            </textarea>
          </div>

          <div class="border-b-2 p-4">
            <p class="font-bold text-xl">Components:</p>
            <div class="flex flex-row">
              <label for="component" class="mt-2"> Select a component: </label>
              <select
                id="component"
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
                class="flex flex-col"
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

          <div
            v-tooltip.right="
              'Maximum number of iterations the application will run for. Note that the initialization budget will be added to this value.'
            "
            class="border-b-2 p-4"
          >
            <label for="nbr_iteration" class="font-bold text-xl"
              >Number of iterations:</label
            >

            <input
              id="iterations"
              type="number"
              name="nbr_iteration"
              min="2"
              max="200"
              required
              class="h-6 w-12 font-bold border-pink-900 border-2 rounded-sm text-center text-pink-600"
            />
          </div>
        </div> -->

    <!-- Configuration form -->

    <!-- <div class="w-full md:w-1/3 lg:w-1/3 mx-auto">
          <p class="text-2xl">Build the configuration</p>

          <ExperimentForm :options="formOptions"></ExperimentForm>
        </div> -->
    <!-- </div> -->

    <!-- Button for starting the experiment -->
    <!-- <div class="flex flex-row">
        <div class="mx-auto">
          <button
            type="submit"
            class="border-2 rounded-md bg-pink-600 p-4 text-2xl text-white"
          >
            Run the experiment
          </button>
        </div>
      </div>
    </form> -->
    <!-- <div v-else class="flex flex-col items-center">
      <div class="text-2xl font-bold">
        Looking for registered components ...
      </div>
      <div>
        <img src="../assets/error_pictures/unicorn.svg" width="500px" />
      </div>
    </div> -->
  </div>
</template>

<script>
import axios from 'axios'
import ExperimentForm from '../components/ExperimentForm'
import BBOForm from '../components/BBOForm'
import ValidateForm from '../components/ValidateForm'

export default {
  components: { ExperimentForm, BBOForm, ValidateForm },
  async asyncData({ $content, params }) {
    const formOptionsFile = await $content('experimentFormOptions').fetch()
    // console.log(formOptionsFile.form_options)
    return { formOptions: formOptionsFile.form_options }
  },
  data() {
    return {
      experimentShow: true,
      bboShow: false,
      everythingFilled: false,
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
    showExperiment() {
      this.experimentShow = true
      this.bboShow = false
      this.validateExperiment = false
    },
    showBBO() {
      this.experimentShow = false
      this.bboShow = true
      this.validateExperiment = false
    },
    validate() {
      this.experimentShow = false
      this.bboShow = false
      this.validateExperiment = true
    },
    submitExperiment() {
      const formData = new FormData(this.$refs.form) // reference to form element
      const data = {} // need to convert it before using not with XMLHttpRequest
      for (const [key, val] of formData.entries()) {
        Object.assign(data, { [key]: val })
      }
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
