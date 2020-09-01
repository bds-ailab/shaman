import Vue from 'vue'
import VueNativeSock from 'vue-native-websocket'

Vue.use(VueNativeSock, 'ws://localhost:5000/', {
  connectManually: true
})
