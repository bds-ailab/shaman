<template>
  <div>
    <form ref="form" @submit.prevent="submitExperiment">
      <!-- Row for the experiment -->
      <div class="flex flex-row mb-12 justify-center">
        <!-- Experiment parameters -->
        <div class="mx-auto w-1/3">
          <p class="text-2xl">Select experiment parameters</p>

          <!-- Using a sbatch -->
          <!-- <div class="border-b-2 p-4">
            <input id="sbatch" type="file" name="sbatch" accept="sbatch" />
          </div> -->

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
            <p class="font-bold text-xl">Accelerator:</p>
            <label for="sbb">SBB:</label>
            <input
              id="sbb"
              type="radio"
              name="accelerator_name"
              value="sbb_slurm"
              required
              minlength="4"
              maxlength="8"
              size="10"
              class="form-radio text-pink-600 h-6 w-6 ml-2 border-pink-900"
            />

            <label for="fiol">FIOL:</label>
            <input
              id="fiol"
              type="radio"
              value="fiol"
              name="accelerator_name"
              required
              minlength="4"
              maxlength="8"
              size="10"
              class="form-radio text-pink-600 h-6 w-6 ml-2 border-pink-900"
            />
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
  methods: {
    onCmCodeChange(newCode) {
      this.code = newCode
    },
    submitExperiment() {
      // Note: During development requests are mocked.
      // Content of response is defined in @/plugins/mocks.js
      // await this.$axios
      //   // Perform a POST request
      //   .$post('/experiments', this.params)
      //   // If successfull then alert the user
      //   .then((response) => {
      //     alert(`Successfully created experiment ${response.id}`)
      //   })
      //   // If an error was encountered then alert the user
      //   .catch((e) => alert('Could not create experiment'))
      const formData = new FormData(this.$refs.form) // reference to form element
      const data = {} // need to convert it before using not with XMLHttpRequest
      for (const [key, val] of formData.entries()) {
        Object.assign(data, { [key]: val })
      }
      console.log(data)
      axios.post('/experiments/launch', data).catch(function(error) {
        alert(error)
      })
      this.$router.push({ path: '/browse' })
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
