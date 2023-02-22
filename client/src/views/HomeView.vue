<script>
import { fetchAlignments } from "../api/alignment.js";

export default {
  name: "HomeComponent",
  components: {},
  data() {
    return {
      alignments: [],
    };
  },
  created() {
    this.fetchAlignments();
  },
  methods: {
    fetchAlignments() {
      fetchAlignments().then((response) => {
        console.log("RESP in component", response);
        this.alignments = response;
      });
    },
  },
};
</script>

<template>
  <main>
    <p>You've come across the alignment protoype.</p>

    <h2>Available Alignments</h2>

    <div>{{ alignments }}</div>
  </main>
</template>
