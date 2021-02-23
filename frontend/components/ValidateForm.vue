<template>
  <div class="flex flex-col mt-8">
    <div class="mx-auto mb-4">
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
        size="20"
        class="form-textarea ml-2"
        v-tooltip.right="'Name to identify the experiment'"
      />
    </div>
    <div
      v-tooltip.right="
        'Maximum number of iterations the application will run for. Note that the initialization budget will be added to this value.'
      "
      class="mx-auto"
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
  </div>
</template>
