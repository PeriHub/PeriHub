<template>
    <v-container fluid style="height:100%;">
        <v-row fluid style="height:100%;">
            <v-col
            cols="12"
            sm="2">
                <v-navigation-drawer padding-left=0 >
                    <v-list
                    dense
                    nav
                    class="py-0"
                    >


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
                        
                        <v-divider></v-divider>

                        <v-list-group
                        prepend-icon="mdi-account-circle">
                            <template v-slot:activator>
                                <v-list-item-title>Examples</v-list-item-title>
                            </template>
                            <v-list-item
                                v-for="item in examples"
                                :key="item.title"
                                link
                                :to="item.route"
                            >
                            <v-list-item-title>{{ item.title }}</v-list-item-title>
                
                            <v-list-item-icon>
                                <v-icon>{{ item.icon }}</v-icon>
                            </v-list-item-icon>
                            </v-list-item>
                        </v-list-group>
                    </v-list>
                </v-navigation-drawer>
            </v-col>
            <v-col style="height:100%; padding: 0px"
            cols="12"
            sm="10">
                <router-view class="view two" name="b"></router-view>
            </v-col>
        </v-row>
    </v-container>
</template>

<script>
    export default {
        data () {
        return {
                items: [
                    { title: 'Introduction', icon: 'mdi-view-dashboard', route: '/guide/introduction' },
                    { title: 'Getting started', icon: 'mdi-image', route: '/guide/gettingStarted' },
                ],
                examples: [
                    { title: 'Dogbone', icon: 'mdi-view-dashboard', route: '/guide/examples/dogbone' },
                    { title: 'GIICmodel', icon: 'mdi-view-dashboard', route: '/guide/examples/giicmodel' },
                    { title: 'DCBmodel', icon: 'mdi-view-dashboard', route: '/guide/examples/dcbmodel' },
                    { title: 'FE Files', icon: 'mdi-image', route: '/guide/examples/fefiles' }
                ],     
            }
        },
    }
</script>
<style>
</style>