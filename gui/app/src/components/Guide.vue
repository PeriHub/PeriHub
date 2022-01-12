<template>
    <v-container  fluid style="height:100%;">
        <v-col>
            <v-navigation-drawer dark >
                <v-list
                dense
                nav
                class="py-0"
                >

                <v-divider></v-divider>

                    <v-list-item
                        v-for="item in items"
                        :key="item.title"
                        link
                        :to="item.route"
                    >
                        <v-list-item-icon>
                        <v-icon>{{ item.icon }}</v-icon>
                        </v-list-item-icon>

                        <v-list-item-content>
                        <v-list-item-title>{{ item.title }}</v-list-item-title>
                        </v-list-item-content>
                    </v-list-item>
                </v-list>
            </v-navigation-drawer>
            <router-view class="view two" name="b"></router-view>
        </v-col>
    </v-container>
</template>

<script>
  export default {
    data () {
      return {
            items: [
                { title: 'Introduction', icon: 'mdi-view-dashboard', route: '/guide/introduction' },
                { title: 'Getting started', icon: 'mdi-image', route: '/guide/gettingStarted' },
                { title: 'Examples', icon: 'mdi-help-box', route: '/guide/examples' },
            ],
        }
    },
  }
</script>
<style>
</style>