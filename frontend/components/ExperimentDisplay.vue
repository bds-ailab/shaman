<template>
  <!-- Start of experiment view column
    NOTE: An experiment is a column because its direct child are positioned vertically
  -->
  <div>
    <!-- Start of execution results row.
      NOTE: It is a row because its elements are positioned horinzontally
    -->
    <b-row class="content-left">
      <b-col md="2"><b>Experiment step:</b> {{ experimentStep }}</b-col>

      <b-col md="1">
        <p v-if="experimentStatus === 'created'" key="created">
          <i class="fas fa-sync text-blue-600"></i>
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
      </b-col>
      <b-col md="2"><b>Experiment start:</b> {{ experimentStart }}</b-col>
      <b-col md="2"><b>Experiment name:</b> {{ experimentName }}</b-col>
    </b-row>
    <!--Start of KPI row. -->
    <div class="flex flex-row justify-center mt-2">
      <AccordionText key="expParam" title="Optimizer">
        <div class="mb-4">
          <li v-for="(value, key) in experimentParameters" :key="key">
            <span>
              <b>{{ key }} </b> {{ value.split('.').slice(-1)[0] }}</span
            >
          </li>
        </div>
      </AccordionText>

      <AccordionText key="noiseParam" title="Noise reduction">
        <div>
          <li v-for="(value, key) in noiseReductionParameters" :key="key">
            <span>
              <b>{{ key }} </b> {{ value.split('.').slice(-1)[0] }}</span
            >
          </li>
        </div>
      </AccordionText>
      <AccordionText key="sbatch" title="Sbatch">
        <div>
          <pre v-highlightjs>
            <code class="bash">
            {{ sbatch }}
            </code>
            </pre>
        </div>
      </AccordionText>
      <AccordionText key="censoring" title="Pruning strategy">
        <div>
          <li v-for="(value, key) in pruningStrategyParameters" :key="key">
            <span>
              <b>{{ key }} </b> {{ value.split('.').slice(-1)[0] }}</span
            >
          </li>
        </div>
      </AccordionText>
      <!-- Each element of the row is a KPIBox component -->
    </div>
    <!-- End of KPI row -->
    <b-row>
      <!-- Chart div is inside a flex and takes 3/4 of width -->
      <b-col md="9">
        <!-- <canvas id="executionTimes" class="w-full"></canvas> -->
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
      </b-col>
      <!-- Results are inside a column because they are positioned vertically -->
      <b-col md="3">
        <KPIBox
          v-for="kpi in kpiInfo"
          :key="kpi.description"
          :value="kpi.value"
          :description="kpi.description"
          class="mx-auto"
        ></KPIBox>
      </b-col>
    </b-row>
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
      ioDurations: {}
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
            formatter: (value) => value.toFixed(2)
          }
        },
        // tooltip: {
        //   custom: (series) => {
        //     let resampledNbr = 1
        //     if (this.experimentStatus === 'finished') {
        //       resampledNbr = this.resampledNbr[series.dataPointIndex]
        //     }
        //     return (
        //       '<div class="arrow_box">' +
        //       '<span>' +
        //       '<b>Elapsed time </b>' +
        //       series.series[series.seriesIndex][series.dataPointIndex] +
        //       '<span>' +
        //       '<b>Number of resamples:</b>' +
        //       resampledNbr +
        //       '</span>' +
        //       '</div>'
        //     )
        //   }
        // },
        stroke: {
          curve: 'smooth'
        }
      }
    },
    sbatch() {
      console.log(this.experiment.sbatch)
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
            description: 'Optimized accelerator',
            value: this.experiment.accelerator
          },
          {
            description: 'Gain compared to default',
            value:
              parseFloat(this.experiment.improvement_default).toFixed(2) + '%'
          },
          {
            description: 'Average noise',
            value: parseFloat(this.experiment.average_noise).toFixed(3)
          },
          {
            description: '% of explored space',
            value: parseFloat(this.experiment.explored_space).toFixed(3)
          }
        ]
      } else {
        return [
          {
            description: 'Optimized accelerator',
            value: ''
          },
          {
            description: 'Gain compared to default',
            value: 0
          },
          {
            description: 'Average noise',
            value: 0
          },
          {
            description: '% of explored space',
            value: 0
          }
        ]
      }
    },
    resampledNbr() {
      return this.experiment.resampled_nbr
    },
    acceleratorName() {
      return this.experiment.accelerator
    },
    experimentParameters() {
      return this.experiment.experiment_parameters
    },
    noiseReductionParameters() {
      return this.experiment.noise_reduction_strategy
        ? this.experiment.noise_reduction_strategy
        : { '': 'Noise reduction disabled for this experiment' }
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
      if (this.experimentStatus === 'finished') {
        return [
          {
            data: this.experiment.averaged_execution_time,
            name: 'Averaged execution time'
          },
          {
            data: this.experiment.min_execution_time,
            name: 'Min execution times'
          },
          {
            data: this.experiment.max_execution_time,
            name: 'Max execution time'
          } //,
          // {
          //   data: this.ioDurations.min_duration_read,
          //   name: 'Min duration read'
          // },
          // {
          //   data: this.ioDurations.average_duration_read,
          //   name: 'Average duration read'
          // },
          // {
          //   data: this.ioDurations.max_duration_read,
          //   name: 'Max duration read'
          // },
          // {
          //   data: this.ioDurations.min_duration_write,
          //   name: 'Min duration write'
          // },
          // {
          //   data: this.ioDurations.average_duration_read,
          //   name: 'Average duration write'
          // },
          // {
          //   data: this.ioDurations.max_duration_read,
          //   name: 'Max duration write'
          // }
        ]
      } else {
        return [
          {
            data: this.experiment.execution_time,
            name: 'Execution time'
          }
        ]
      }
    }
  },
  mounted() {
    axios
      .all([
        axios.get('/experiments/' + this.objectid)
        // axios.get('/io_durations/' + this.objectid)
      ])
      .then(
        axios.spread((experimentResponse, ioDurationResponse) => {
          this.experiment = experimentResponse.data
          //          this.ioDurations = ioDurationResponse.data
        })
      )
      .catch((e) => console.log(e))
    // Listen to websocket
    this.ws = new WebSocket(
      'ws://localhost:5000/experiments/' + this.objectid + '/stream'
    )
    this.ws.onmessage = (event) => {
      const expUpdate = JSON.parse(event.data)
      this.$set(this.experiment, 'parameters', expUpdate.parameters)
      this.$set(this.experiment, 'execution_time', expUpdate.execution_time)
    }
  },
  beforeDestroy() {
    this.ws.close()
  }
}
</script>
