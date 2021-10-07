<template>
  <!-- Copyright 2020 BULL SAS All rights reserved -->

  <!-- Start of experiment view column
    NOTE: An experiment is a column because its direct child are positioned vertically
  -->
  <div>
    <div
      class="flex w-full bg-blue-600 text-white h-20 m-auto text-2xl items-center justify-center"
    >
      Experiment
      <b
        ><pre> {{ experimentName }} </pre></b
      >
      with component
      <b
        ><pre> {{ componentName }} </pre></b
      >
    </div>
    <div>
      <!-- Start of execution results row.
      NOTE: It is a row because its elements are positioned horinzontally
    -->
      <div class="flex flex-wrap">
        <div class="flex flex-row w-2/3 mb-2 justify-center md:justify-start">
          <InfoBox :data="experimentInfo" title="Experiment information">
          </InfoBox>

          <InfoBox :data="gainInfo" title="Gain"> </InfoBox>
        </div>
        <div class="flex flex-wrap mx-auto">
          <OptimalConfiguration
            :bestParameters="bestParameters"
            :optimalTime="bestTime"
          ></OptimalConfiguration>
        </div>
      </div>
    </div>

    <div class="flex flex-col">
      <div class="flex flex-row justify-around">
        <div>
          <input
            type="checkbox"
            id="rawDataCheckbox"
            v-model="rawData"
            class="form-checkbox h-6 w-6 text-pink-600 border-gray-900"
          />
          <label class="text-xl font-semibold pt-3" for="checkbox"
            >Plot raw data</label
          >
        </div>
        <div class="text-xl font-semibold pt-3">
          <i class="fas fa-square text-purple-600"></i> Stop experiment
        </div>
      </div>
      <div class="flex flex-row">
        <div id="wrapper" class="w-5/6">
          <div id="time-chart">
            <apexchart
              type="area"
              height="500"
              :series="executionTimes"
              :options="chartOptionsTimes"
            ></apexchart>
          </div>
          <div
            v-for="data in parsedParameters"
            :id="data['name']"
            :key="data['name']"
          >
            <apexchart
              type="area"
              height="100"
              :series="[data]"
              :options="chartOptionsParameters(data.labels)"
            ></apexchart>
          </div>
        </div>
        <div class="w-1/6">
          <ModalBox id="sbatch" title="Sbatch">
            <div>
              <pre v-highlightjs>
            <code class="bash">
            {{ sbatch }}
            </code>
            </pre>
            </div>
          </ModalBox>

          <ModalBox id="expParam" title="Optimizer">
            <div>
              <li v-for="(value, key) in experimentParameters" :key="key">
                <span>
                  <b>{{ key }} </b> {{ value }}</span
                >
              </li>
            </div>
          </ModalBox>

          <ModalBox id="noiseParam" title="Noise reduction">
            <li v-for="(value, key) in noiseReductionParameters" :key="key">
              <span>
                <b>{{ key }} </b> {{ value }}</span
              >
            </li>
          </ModalBox>

          <ModalBox id="censoring" title="Pruning strategy">
            <div>
              <li v-for="(value, key) in pruningStrategyParameters" :key="key">
                <span>
                  <b>{{ key }} </b> {{ value }}</span
                >
              </li>
            </div>
          </ModalBox>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import InfoBox from '../components/InfoBox'
import OptimalConfiguration from '../components/OptimalConfiguration'
import ModalBox from '../components/ModalBox'

export default {
  components: { InfoBox, OptimalConfiguration, ModalBox },
  props: {
    name: {
      default: 'no name',
      type: String
    },
    objectid: {
      default: '',
      type: String
    }
  },
  data() {
    return {
      experiment: {},
      rawData: true
    }
  },
  methods: {
    getExperimentIcon(experimentStatus) {
      let icon = ''
      switch (experimentStatus) {
        case 'created':
          icon = '<i class="fas fa-sync text-blue-600"></i>'
          break
        case 'running':
          icon = '<i class="fas fa-sync fa-spin text-orange-600"></i>'
          break
        case 'finished':
          icon = '<i class="fas fa-sync fa-check-circle text-green-600"></i>'
          break
        case 'failed':
          icon = '<i class="fas fa-times-circle text-red-600"></i>'
          break
        case 'stopped':
          icon = '<i class="fas fa-square text-purple-600"></i>'
          break
      }
      return icon
    },
    getIntHash(value) {
      let hash = 0
      const len = value.length
      for (let i = 0; i < len; i++) {
        hash = (hash << 5) - hash + value.charCodeAt(i)
        hash |= 0 // to 32bit integer
      }
      return hash
    },
    getArrayHash(strArray) {
      const hashedStrArray = []
      strArray.forEach((str, i) => hashedStrArray.push(this.getIntHash(str)))
      return hashedStrArray
    },
    chartOptionsParameters(labels) {
      return {
        chart: {
          height: 350,
          type: 'area',
          group: 'performance',
          id: 'time'
        },
        tooltip: {
          shared: true,
          custom: (series) => {
            const name = series.w.config.series[series.seriesIndex].name
            if (labels) {
              return (
                '<div class="arrow_box">' +
                '<span>' +
                '<b> Parameter &#32;' +
                name +
                '&#32;: </b>' +
                labels[series.dataPointIndex] +
                '</span>' +
                '</div>'
              )
            } else {
              return (
                '<div class="arrow_box">' +
                '<span>' +
                '<b> Parameter &#32;' +
                name +
                '&#32;: </b>' +
                series.series[series.seriesIndex][series.dataPointIndex] +
                '</span>' +
                '</div>'
              )
            }
          }
        },
        dataLabels: {
          enabled: typeof labels !== 'undefined',
          formatter: (val, context) => {
            if (labels) {
              return labels[context.dataPointIndex]
            } else {
              return val
            }
          }
        },
        yaxis: {
          labels: {
            minWidth: 40,
            formatter: (val, context) => {
              if (labels) {
                return ''
              } else {
                return val
              }
            }
          }
        },
        stroke: {
          curve: 'smooth'
        }
      }
    }
  },
  computed: {
    chartOptionsTimes() {
      return {
        chart: {
          height: 350,
          type: 'area',
          group: 'performance',
          id: 'time'
        },
        dataLabels: {
          enabled: false
        },
        yaxis: {
          labels: {
            minWidth: 40,
            formatter: (value) => value.toFixed(3)
          }
        },
        tooltip: {
          shared: true,
          custom: (series) => {
            let resampledNbr = 1
            let truncatedNbr = 0
            if (this.experimentStatus === 'finished' && !this.rawData) {
              resampledNbr = this.resampledNbr[series.dataPointIndex]
            }
            truncatedNbr = this.truncated[series.dataPointIndex]
            return (
              '<div class="arrow_box">' +
              '<span>' +
              '<b>Performance value:   </b>' +
              series.series[series.seriesIndex][series.dataPointIndex] +
              '<span> <br/>' +
              '<b>Number of resamples:  </b>' +
              resampledNbr +
              '</span> <br/>' +
              '<span>' +
              '<b>Pruned:  </b>' +
              truncatedNbr +
              '</span>' +
              '</div>'
            )
          }
        },
        stroke: {
          curve: 'smooth'
        }
      }
    },
    experimentInfo() {
      return {
        'Experiment start': this.experimentStart,
        'Experiment step': this.experimentStep,
        Status: this.getExperimentIcon(this.experimentStatus)
      }
    },
    gainInfo() {
      return {
        'Gain compared to default': this.gainDefault,
        'Average noise': this.averageNoise,
        'Explored space': this.experiment.explored_space + ' %'
      }
    },
    sbatch() {
      return this.experiment.sbatch
        ? this.experiment.sbatch // .replace('\n', '<br>')
        : ''
    },
    gainDefault() {
      if (this.experiment.improvement_default) {
        return this.experiment.improvement_default.toFixed(2) + ' %'
      } else {
        return '0' + ' %'
      }
    },
    averageNoise() {
      if (this.experiment.average_noise) {
        return this.experiment.average_noise.toFixed(2) + ' s'
      } else {
        return '0' + ' s'
      }
    },
    step() {
      if (this.experiment.parameters) {
        return this.experiment.parameters.length
      }
      return 0
    },
    totalSteps() {
      if (this.experiment.experiment_parameters) {
        return (
          this.experiment.experiment_budget +
          parseFloat(this.experiment.experiment_parameters.initial_sample_size)
        )
      } else {
        return 0
      }
    },
    experimentStep() {
      if (
        (this.experimentStatus === 'finished') &
        (this.step < this.totalSteps)
      ) {
        return this.step + '/' + this.totalSteps + ' (early stop)'
      } else {
        return this.step + '/' + this.totalSteps
      }
    },
    experimentStart() {
      return this.experiment.experiment_start
    },
    experimentName() {
      return this.experiment.experiment_name
    },
    resampledNbr() {
      return this.experiment.resampled_nbr
    },
    truncated() {
      return this.experiment.truncated
    },
    componentName() {
      return this.experiment.component
    },
    bestParameters() {
      return this.experiment.best_parameters
    },
    bestTime() {
      return this.experiment.best_fitness
    },
    experimentParameters() {
      return this.experiment.experiment_parameters
    },
    defaultTime() {
      if (this.experiment.default_run) {
        return this.experiment.default_run.fitness
      } else {
        return 0
      }
    },
    noiseReductionParameters() {
      if (this.experiment.noise_reduction_strategy) {
        if (Object.keys(this.experiment.noise_reduction_strategy).length > 0) {
          return this.experiment.noise_reduction_strategy
        } else {
          return { '': 'Noise reduction disabled for this experiment' }
        }
      } else {
        return { '': 'Noise reduction disabled for this experiment' }
      }
    },
    pruningStrategyParameters() {
      return this.experiment.pruning_strategy
        ? this.experiment.pruning_strategy
        : { '': 'Pruning strategy disabled for this experiment' }
    },
    testedParameters() {
      return this.experiment.parameters
    },
    parsedParameters() {
      const parameterObj = {}
      // Contains the data for the graphs
      const serieData = []
      if (this.experiment.parameters) {
        this.testedParameters.forEach(function(parameters, index) {
          for (const [key, value] of Object.entries(parameters)) {
            if (parameterObj[key]) {
              parameterObj[key].push(value)
            } else {
              parameterObj[key] = [value]
            }
          }
        })
      }

      for (const [key, value] of Object.entries(parameterObj)) {
        // Check if value can be converted to a float
        if (parseFloat(value[0])) {
          serieData.push({ name: key, data: value })
        } else {
          serieData.push({
            name: key,
            data: this.getArrayHash(value),
            labels: value
          })
        }
      }
      return serieData
    },
    experimentStatus() {
      return this.experiment.status
    },
    executionTimes() {
      // Format the data for apex chart formatting
      if ((this.experimentStatus === 'finished') & !this.rawData) {
        return [
          {
            data: this.experiment.averaged_fitness,
            name: 'Averaged execution time'
          },
          {
            data: this.experiment.min_fitness,
            name: 'Min execution times'
          },
          {
            data: this.experiment.max_fitness,
            name: 'Max execution time'
          }
        ]
      } else {
        return [
          {
            data: this.experiment.fitness,
            name: 'Execution time'
          }
        ]
      }
    }
  },
  mounted() {
    axios
      .get('/experiments/' + this.objectid)
      .then((response) => {
        this.experiment = response.data
      })
      .catch((e) => console.log(e))
    // Listen to websocket
    this.ws = new WebSocket(
      'ws://localhost:5000/experiments/' + this.objectid + '/stream'
    )
    this.ws.onmessage = (event) => {
      const expUpdate = JSON.parse(event.data)
      this.$set(this.experiment, 'parameters', expUpdate.parameters)
      this.$set(this.experiment, 'fitness', expUpdate.fitness)
      this.$set(
        this.experiment,
        'improvement_default',
        expUpdate.improvement_default
      )
      this.$set(this.experiment, 'average_noise', expUpdate.average_noise)
      this.$set(this.experiment, 'explored_space', expUpdate.explored_space)
      this.$set(this.experiment, 'best_parameters', expUpdate.best_parameters)
      this.$set(this.experiment, 'best_fitness', expUpdate.best_fitness)

      this.$set(this.experiment, 'status', expUpdate.status)
      if (expUpdate.status === 'finished') {
        this.experiment = expUpdate
        this.ws.close()
      }
    }
  },
  destroyed() {
    this.ws.close()
  }
}
</script>

<style>
/* Tooltip style: taken from https://github.com/Akryum/v-tooltip#style-examples*/
.tooltip {
  display: block !important;
  z-index: 10000;
}

.tooltip .tooltip-inner {
  background: #d53f8c;
  opacity: 0.8;
  color: white;
  border-radius: 16px;
  padding: 5px 10px 4px;
  font-size: 1rem;
}

.tooltip .tooltip-arrow {
  width: 0;
  height: 0;
  border-style: solid;
  position: absolute;
  margin: 5px;
  border-color: #d53f8c;
  z-index: 1;
}

.tooltip[x-placement^='top'] {
  margin-bottom: 5px;
}

.tooltip[x-placement^='top'] .tooltip-arrow {
  border-width: 5px 5px 0 5px;
  border-left-color: transparent !important;
  border-right-color: transparent !important;
  border-bottom-color: transparent !important;
  bottom: -5px;
  left: calc(50% - 5px);
  margin-top: 0;
  margin-bottom: 0;
}

.tooltip[x-placement^='bottom'] {
  margin-top: 5px;
}

.tooltip[x-placement^='bottom'] .tooltip-arrow {
  border-width: 0 5px 5px 5px;
  border-left-color: transparent !important;
  border-right-color: transparent !important;
  border-top-color: transparent !important;
  top: -5px;
  left: calc(50% - 5px);
  margin-top: 0;
  margin-bottom: 0;
}

.tooltip[x-placement^='right'] {
  margin-left: 5px;
}

.tooltip[x-placement^='right'] .tooltip-arrow {
  border-width: 5px 5px 5px 0;
  border-left-color: transparent !important;
  border-top-color: transparent !important;
  border-bottom-color: transparent !important;
  left: -5px;
  top: calc(50% - 5px);
  margin-left: 0;
  margin-right: 0;
}

.tooltip[x-placement^='left'] {
  margin-right: 5px;
}

.tooltip[x-placement^='left'] .tooltip-arrow {
  border-width: 5px 0 5px 5px;
  border-top-color: transparent !important;
  border-right-color: transparent !important;
  border-bottom-color: transparent !important;
  right: -5px;
  top: calc(50% - 5px);
  margin-left: 0;
  margin-right: 0;
}

.tooltip.popover .popover-inner {
  background: #f9f9f9;
  color: black;
  padding: 24px;
  border-radius: 5px;
  box-shadow: 0 5px 30px rgba(black, 0.1);
}

.tooltip.popover .popover-arrow {
  border-color: #f9f9f9;
}

.tooltip[aria-hidden='true'] {
  visibility: hidden;
  opacity: 0;
  transition: opacity 0.15s, visibility 0.15s;
}

.tooltip[aria-hidden='false'] {
  visibility: visible;
  opacity: 1;
  transition: opacity 0.15s;
}
</style>
