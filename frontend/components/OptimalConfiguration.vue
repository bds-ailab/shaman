<template>
  <!-- Copyright 2020 BULL SAS All rights reserved -->
  <!-- Flex column is used to easily center text vertically.
 -->
  <div
    v-b-modal.modal-optim
    class="flex flex-col md:w-2/3 mr-4 rounded-md px-3 py-3 mt-4 bg-gray-100 shadow-sm text-center"
  >
    <div class="text-2xl font-bold mb-2 my-auto">
      Optimal configuration <br />
      <i class="fas fa-plus-circle"></i>
    </div>
    <b-modal
      cancel-title="Close"
      ok-title="Export"
      id="modal-optim"
      title="Optimal configuration"
    >
      <div class="mb-2"><b>Optimal time</b>: {{ optimalTime }}</div>
      <hr />

      <div class="mt-2" v-for="bestParam in bestParameters" :key="bestParam">
        <div
          class="flex flex-row"
          v-for="(param, name) in bestParam"
          :key="param"
        >
          <b>{{ name }}</b
          >: {{ param }}
        </div>
      </div>
    </b-modal>
  </div>
</template>

<script>
export default {
  props: {
    bestParameters: {
      type: Object,
      default: () => {}
    },
    optimalTime: {
      type: Number,
      default: 0
    }
  }
}
</script>
