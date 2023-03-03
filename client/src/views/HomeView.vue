<script>
import { fetchAlignments } from "../api/alignment.js";

export default {
  name: "HomeComponent",
  components: {},
  data() {
    return {
      alignmentData: {},
    };
  },
  created() {
    this.fetchAlignments();
  },
  methods: {
    fetchAlignments() {
      fetchAlignments().then((response) => {
        console.log("RESP in component", response);
        this.alignmentData = response;
      });
    },
  },
};
</script>

<template>
  <main>
    <p>You've come across the alignment protoype.</p>

    <h2>Available Alignments</h2>

    <div v-for="alignment in alignmentData.alignments" :key="alignment.id">
      <h2>{{ alignment.id }}</h2>
      <ul>
        <li>source: {{ alignment.source }}</li>
        <li>target: {{ alignment.target }}</li>
      </ul>
    </div>
  </main>
</template>
