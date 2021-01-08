<template>
  <!-- Copyright 2020 BULL SAS All rights reserved -->

  <!-- Start of experiment view column
    NOTE: An experiment is a column because its direct child are positioned vertically
  -->
  <div>
    <!-- Start of execution results row.
      NOTE: It is a row because its elements are positioned horinzontally
    -->
    <div class="flex flex-wrap justify-around">
      <div>
        <b>Experiment step:</b> {{ experimentStep }}
        <p v-if="experimentStatus === 'created'" key="created">
          <i class="fas fa-sync text-blue-600"></i>Staging the experiment
        </p>
        <p v-if="experimentStatus === 'running'" key="running">
          <i class="fas fa-sync fa-spin text-orange-600"></i>
        </p>
        <p v-if="experimentStatus === 'finished'" key="finished">
          <i class="fas fa-sync fa-check-circle text-green-600"></i>
        </p>
        <p v-if="experimentStatus === 'failed'" key="failed">
          <i class="fas fa-times-circle text-red-600"></i>
        </p>
        <p v-if="experimentStatus === 'stopped'" key="stopped">
          <i class="fas fa-square text-purple-600"></i>
        </p>
      </div>
      <div md="2"><b>Experiment start:</b> {{ experimentStart }}</div>
      <div md="2"><b>Experiment name:</b> {{ experimentName }}</div>
    </div>

    <div class="flex flex-wrap justify-center">
      <!--Start of KPI row. -->
      <div class="flex flex-wrap justify-left mt-2 ">
        <div class="w-full lg:w-1/6 xl:w-1/6">
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
        <AccordionText id="expParam" title="Optimizer">
          <div>
            <li v-for="(value, key) in experimentParameters" :key="key">
              <span>
                <b>{{ key }} </b> {{ value }}</span
              >
            </li>
          </div>
        </AccordionText>

        <AccordionText id="noiseParam" title="Noise reduction">
          <li v-for="(value, key) in noiseReductionParameters" :key="key">
            <span>
              <b>{{ key }} </b> {{ value }}</span
            >
          </li>
        </AccordionText>
        <AccordionText id="sbatch" title="Sbatch">
          <div>
            <pre v-highlightjs>
            <code class="bash">
            {{ sbatch }}
            </code>
            </pre>
          </div>
        </AccordionText>
        <AccordionText id="censoring" title="Pruning strategy">
          <div>
            <li v-for="(value, key) in pruningStrategyParameters" :key="key">
              <span>
                <b>{{ key }} </b> {{ value }}</span
              >
            </li>
          </div>
        </AccordionText>
      </div>

      <div class="w-full xl:w-5/6 lg:w-5/6">
        <div class="flex flex-row items-center">
          <div class="ml-2 flex flex-row">
            <b>Optimal parameters:</b>
            <div
              class="ml-2 flex flex-row"
              v-for="bestParam in bestParameters"
              :key="bestParam"
            >
              <div class="ml-2" v-for="(param, name) in bestParam" :key="param">
                <b>{{ name }}</b
                >: {{ param }}
              </div>
            </div>
          </div>
          <div class="ml-6 flex flex-row">
            <b>Optimal performance</b>
            <div class="ml-2">{{ bestTime }}</div>
          </div>
        </div>

        <div id="wrapper">
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
              :options="chartOptionsParameters"
            ></apexchart>
          </div>
        </div>
      </div>
      <!-- Results are inside a column because they are positioned vertically -->
      <div class="w-full lg:w-1/6 xl:w-1/6">
        <div class="flex flex-col">
          <KPIBox
            v-for="kpi in kpiInfo"
            :key="kpi.description"
            :value="kpi.value"
            :description="kpi.description"
            :tooltip="kpi.tooltip"
            class="mx-auto"
          ></KPIBox>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import KPIBox from '../components/KPIBox'
import AccordionText from '../components/AccordionText'

export default {
  components: { KPIBox, AccordionText },
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
  computed: {
    chartOptionsParameters() {
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
            minWidth: 40
          }
        },
        stroke: {
          curve: 'smooth'
        }
      }
    },
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
              '<b>Elapsed time:   </b>' +
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
    sbatch() {
      return this.experiment.sbatch
        ? this.experiment.sbatch // .replace('\n', '<br>')
        : ''
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
      return this.step + '/' + this.totalSteps
    },
    experimentStart() {
      return this.experiment.experiment_start
    },
    experimentName() {
      return this.experiment.experiment_name
    },
    kpiInfo() {
      if (this.experiment) {
        return [
          {
            description: 'Optimized component',
            value: this.experiment.component,
            tooltip: 'The name of the optimized component'
          },
          {
            description: 'Gain compared to default',
            value:
              parseFloat(this.experiment.improvement_default).toFixed(2) + '%',
            tooltip:
              'Time gain compared to the default parametrization, expressed in percentage.'
          },
          {
            description: 'Average noise',
            value: parseFloat(this.experiment.average_noise).toFixed(3) + 's',
            tooltip: 'Standard error within each tested parametrization'
          },
          {
            description: 'Explored space',
            value: parseFloat(this.experiment.explored_space).toFixed(3) + '%',
            tooltip:
              'Ratio of different tested parametrization compared to the total of possible parametrizations'
          }
        ]
      } else {
        return [
          {
            description: 'Optimized component',
            value: '',
            tooltip: 'The name of the optimized component'
          },
          {
            description: 'Gain compared to default',
            tooltip:
              'Time gain compared to the default parametrization, expressed in percentage.',
            value: 0
          },
          {
            description: 'Average noise',
            value: 0,
            tooltip: 'Standard error within each tested parametrization'
          },
          {
            description: '% of explored space',
            tooltip:
              'Ratio of different tested parametrization compared to the total of possible parametrizations',
            value: 0
          }
        ]
      }
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
        serieData.push({ name: key, data: value })
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
