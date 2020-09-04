<template>
  <div>
    <div>
      <b-pagination
        v-model="currentPage"
        :total-rows="Object.keys(experiments).length"
        :per-page="perPage"
        aria-controls="experimentTable"
        class="overflow-auto"
        @input="showExperiment(false)"
      ></b-pagination>
    </div>
    <!-- End of pagination -->

    <!-- Start of table -->
    <div>
      <div class="table-responsive">
        <b-table
          id="experimentTable"
          ref="experimentTable"
          selectable
          select-mode="single"
          striped
          hover
          :items="Object.values(experiments)"
          :fields="fields"
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
              <i class="fas fa-sync fa-check-circle text-green-600"></i>
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
      <!-- Ugly test workaround: copy pasting -->
    </div>
    <!-- End of table -->
  </div></template
>

<script>
export default {
  props: {
    experiments: {
      type: Object,
      default: {}
    },
    fields: {
      type: Object,
      default: ''
    },
    perPage: {
      type: int,
      default: 10
    },
    currentPage: {
      type: int,
      default: 0
    },
    sortBy: {
      type: String,
      default: ''
    },
    sortDesc: {
      type: String,
      default: ''
    },
    onRowSelected: {
      type: Function,
      default: function() {}
    }
  }
}
</script>
