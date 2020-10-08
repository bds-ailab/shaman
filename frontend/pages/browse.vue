<template>
  <div class="container-fluid">
    <!-- Page content is a single row -->
    <div v-if="!experiments" class="flex flex-col items-center">
      <div class="text-2xl font-bold">
        Whoops, it seems like there is no experiment yet ! Let's launch a new
        one to get <nuxt-link to="/launch">started</nuxt-link>
      </div>
      <div>
        <img :src="unicorn" width="500px" />
      </div>
    </div>
    <div v-else>
      <div class="flex flex-col w-2/3 mx-auto" v-if="!viewExperiment">
        <ExperimentTable
          id="mainTable"
          :experiments="experiments"
          :fields="fields"
          :perPage="perPage"
          :currentPage="currentPage"
          :sortBy="sortBy"
          :sortDesc="sortDesc"
          :onRowSelected="onRowSelected"
        >
        </ExperimentTable>
      </div>

      <!-- Sidebar table -->
      <!-- TODO: check why i can't use an experiment table component like above ... -->
      <div v-if="viewExperiment">
        <b-sidebar
          id="experimentSidebar"
          title="Browse experiments"
          backdrop
          width="500px"
        >
          <div>
            <div>
              <div>
                <b-pagination
                  :id="id"
                  v-model="currentPage"
                  :total-rows="Object.keys(experiments).length"
                  :per-page="perPage"
                  :aria-controls="id"
                  class="overflow-auto"
                ></b-pagination>
                <!-- @input="showExperiment(false)" -->
              </div>
              <!-- End of pagination -->
              <!-- Start of table -->
              <div>
                <div class="table-responsive">
                  <b-table
                    :id="id"
                    :ref="id"
                    selectable
                    select-mode="single"
                    striped
                    hover
                    :items="Object.values(experiments)"
                    :fields="reduced_fields"
                    :per-page="perPage"
                    :current-page="currentPage"
                    :sort-by.sync="sortBy"
                    :sort-desc.sync="sortDesc"
                    @row-selected="onRowSelected"
                  >
                    <template v-slot:cell(status)="data">
                      <p v-if="data.value === 'created'" key="created">
                        <i class="fas fa-sync text-blue-600"></i>
                      </p>
                      <p v-if="data.value === 'running'" key="running">
                        <i class="fas fa-sync fa-spin text-orange-600"></i>
                      </p>
                      <p v-if="data.value === 'finished'" key="finished">
                        <i
                          class="fas fa-sync fa-check-circle text-green-600"
                        ></i>
                      </p>
                      <p v-if="data.value === 'failed'" key="failed">
                        <i class="fas fa-times-circle text-red-600"></i>
                      </p>
                      <p v-if="data.value === 'stopped'" key="stopped">
                        <i class="fas fa-square text-purple-600"></i>
                      </p>
                    </template>
                  </b-table>
                </div>
              </div>
              <!-- End of table -->
            </div>
          </div>
        </b-sidebar>
        <div class="flex flex-row w-full">
          <div class="flex flex-col w-1/6">
            <!-- Button for full view of experiment through sidebar -->
            <div
              class="inline-block h-6 w-6 bg-pink-600 shaman-button mx-auto mb-4"
              @click="showExperiment(false)"
            >
              Back to full view
            </div>
            <div
              class="inline-block h-6 w-6 bg-pink-600 shaman-button mb-4 mx-auto"
              v-b-toggle.experimentSidebar
            >
              Browse experiments
            </div>
          </div>
          <div class="w-full">
            <!-- Include ExperimentDisplay wth name and objectID properties -->

            <ExperimentDisplay
              :key="objectId"
              :name="experimentName"
              :objectid="objectId"
            ></ExperimentDisplay>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import ExperimentTable from '../components/ExperimentTable'
import ExperimentDisplay from '../components/ExperimentDisplay'
import unicorn from '../assets/error_pictures/unicorn_2.svg'
// Load data using the REST API
export default {
  name: 'BrowsePage',
  components: { ExperimentDisplay, ExperimentTable },
  data() {
    return {
      sortBy: 'experiment_start',
      sortDesc: true,
      experiments: {},
      viewExperiment: false,
      selected: null,
      perPage: 10,
      currentPage: 1,
      currentPageSidebar: 5,
      default_fields: [
        { key: 'experiment_name', sortable: true },
        { key: 'experiment_start', sortable: true, sortDirection: 'asc' },
        { key: 'component', sortable: true },
        { key: 'status', sortable: false }
      ],
      reduced_fields: [
        { key: 'experiment_name', sortable: true },
        { key: 'status', sortable: false }
      ],
      fields: [],
      unicorn
    }
  },
  computed: {
    experimentName() {
      return this.selected ? this.selected.experiment_name : undefined
    },
    objectId() {
      if (this.selected) {
        return this.selected._id
      } else {
        return undefined
      }
    }
  },
  mounted() {
    axios
      .get('/experiments/')
      .then((response) => {
        this.fields = this.default_fields
        response.data.forEach((exp) => (this.experiments[exp._id] = exp))
        // Listen to websocket
        this.ws = new WebSocket('ws://mimsy.farm:5000/experiments/stream')
        this.ws.onmessage = (event) => {
          const experimentUpdate = JSON.parse(event.data)
          experimentUpdate._id = experimentUpdate.id
          if (this.experiments[experimentUpdate._id]) {
            this.$set(
              this.experiments[experimentUpdate._id],
              'status',
              experimentUpdate.status
            )
          } else {
            this.$set(this.experiments, experimentUpdate._id, experimentUpdate)
          }
        }
      })
      .catch((e) => alert("It seems like I can't reach the API right now !"))
  },
  beforeDestroy() {
    this.ws.close()
  },
  methods: {
    showExperiment(viewExperiment) {
      if (viewExperiment !== this.viewExperiment) {
        this.viewExperiment = viewExperiment
      }
    },
    onRowSelected(item) {
      this.selected = item[0]
      this.showExperiment(true)
    },
    selectAllRows() {
      this.$refs.experimentTable.selectAllRows()
    },
    clearSelected() {
      this.$refs.experimentTable.clearSelected()
    },
    hideExperiment() {
      this.showExperiment(false)
    }
  }
}
</script>
