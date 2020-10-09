<template>
  <div>
    <b-button v-b-toggle.sidebar-1 class="bg-pink-700"
      ><i class="fas fa-bars"></i
    ></b-button>
    <b-sidebar id="sidebar-1" title="" shadow>
      <div class="flex flex-col justify-items-center">
        <div class="mb-4">
          <logo />
        </div>
        <div class="ml-6 my-auto">
          <div
            v-for="link in navbarStructure"
            :key="link.path"
            class="mx-auto mb-4 menu"
          >
            <nuxt-link :to="link.path" class="text-xl"
              ><i :class="link.icon" class="mr-4"></i>{{ link.text }}</nuxt-link
            >
          </div>
        </div>
      </div>
    </b-sidebar>
  </div>
</template>

<script>
import Logo from '~/components/Logo.vue'

export default {
  components: {
    Logo
  },
  data() {
    return {
      navbarStructure: [
        { path: '/', text: 'HOME', icon: 'fas fa-home' },
        {
          path: '/browse',
          text: 'EXPLORE',
          icon: 'fas fa-microscope'
        },
        {
          path: '/launch',
          text: 'CREATE',
          icon: 'fas fa-flask'
        },
        {
          path: '/documentation',
          text: 'USER MANUAL',
          icon: 'fas fa-book'
        },
        {
          path: '/relatedworks',
          text: 'RELATED WORKS',
          icon: 'fas fa-scroll'
        }
      ]
    }
  }
}
</script>

<style lang="stylus">
/* Import theme colors palette */
@import '../css/palette.styl';

.menu {
  font-family: 'Roboto';
}
</style>
