<template>
  <b-row id="navbar-container">
    <b-navbar
      toggleable="xl"
      type="light"
      class="justify-content-md-center justify-content-start"
    >
      <b-navbar-toggle target="navbar-toggle-collapse" class="mr-4 ml-auto">
        <template v-slot:default="{ expanded }">
          <b-icon v-if="expanded" icon="chevron-bar-up"></b-icon>
          <b-icon v-else icon="chevron-bar-down"></b-icon>
        </template>
      </b-navbar-toggle>

      <b-collapse id="navbar-toggle-collapse" is-nav>
        <b-navbar-nav
          class="mx-auto justify-content-between align-items-center"
        >
          <b-nav-item
            v-for="link in navbarStructure"
            :key="link.path"
            :to="link.path"
          >
            {{ link.text }}
          </b-nav-item>
        </b-navbar-nav>
      </b-collapse>
    </b-navbar>
  </b-row>
</template>

<script>
export default {
  data() {
    return {
      navbarStructure: [
        { path: '/', text: 'Home' },
        { path: '/browse', text: 'Browse experiments' },
        { path: '/launch', text: 'Launch a new experiment' },
        {
          path: '/documentation',
          text: 'Documentation'
        },
        {
          path: '/relatedworks',
          text: 'Related Works'
        }
      ]
    }
  }
}
</script>

<style lang="stylus">
/* Import theme colors palette */
@import '../css/palette.styl';

#navbar-container nav {
  font-size: 1.5rem;
  margin-bottom: 4rem;
}

#navbar-container ul .nav-link {
  margin-left: 20px;
  margin-right: 20px;
  font-family: 'Roboto', sans-serif;
}

#navbar-container ul .nav-link:hover {
  color: $pastelGreenColor;
  border-bottom: 2px solid $pastelGreenColor;
}

#navbar-container ul .nuxt-link-exact-active {
  color: $accentColor;
  border-bottom: 2px solid $accentColor;
}
</style>
