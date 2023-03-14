<script>
import { fetchAlignments, fetchLinks } from "@/api/alignment.js";

export default {
  name: "HomeComponent",
  components: {},
  data() {
    return {
      alignments: [],
      selectedAlignment: "",
      linkQueryScope: "",
      loading: false,
      links: null,
      linkQueryResponseTime: "",
    };
  },
  created() {
    this.fetchAlignments();
  },
  methods: {
    fetchAlignments() {
      this.loading = true;
      fetchAlignments().then((response) => {
        this.alignments = response;
        this.loading = false;
      });
    },
    fetchLinks() {
      this.loading = true;
      this.links = null;
      fetchLinks(this.selectedAlignment, this.linkQueryScope).then(
        (response) => {
          this.links = response.response;
          this.linkQueryResponseTime = response.time;
          this.loading = false;
        }
      );
    },
  },
  computed: {
    summarizedLinks() {
      return this.links.map((link) => {
        const sourceTokenIds = link.source_tokens
          .map((src) => src.token_id)
          .flat();
        const targetTokenIds = link.target_tokens
          .map((target) => target.token_id)
          .flat();
        return {
          id: link.token_id,
          summary: link.source_tokens.reduce((acc, curr) => {
            return `${acc} ${curr.text}`;
          }, ""),
          details: `source: ${sourceTokenIds}, target: ${targetTokenIds}`,
        };
      });
    },
    linkQueryResponseTimeShort() {
      return this.linkQueryResponseTime.toFixed();
    },
  },
};
</script>

<template>
  <main>
    <h2>Find some links</h2>
    <p>
      This is a prototype. To explore the available data, select an alignment
      and provide a scope to query links.
    </p>
    <ol>
      <li>Select and alignment dataset to query.</li>
      <li>
        Provide a scope. Specify by:
        <ul>
          <li>book number, i.e. 42</li>
          <li>book and chapter, i.e. 42001</li>
          <li>full bcv, i.e. 42001001</li>
          <li>
            combine scopes i.e. 42001001,4200001002 (comma separation, no space)
          </li>
        </ul>
      </li>
    </ol>

    <fieldset name="Query Links">
      <legend>Query Links</legend>
      <label
        >Selected alignment
        <select v-model="selectedAlignment">
          <option disabled value="">Please select an alignment</option>
          <option
            v-for="alignment in alignments"
            :key="alignment.id"
            :value="alignment.id"
          >
            {{ alignment.name }}
          </option>
        </select>
      </label>

      <label>
        Link query scope
        <input v-model="linkQueryScope" type="text" />
      </label>

      <button v-on:click="fetchLinks" :disabled="!selectedAlignment">
        Get Links
      </button>
    </fieldset>

    <div v-if="loading">Loading...</div>

    <div v-if="links">
      <p>
        Success! {{ links.length }} links found
        <em>( {{ linkQueryResponseTimeShort }} ms )</em>
      </p>

      <details
        v-for="summarizedLink in summarizedLinks"
        :key="summarizedLink.id"
      >
        <summary>{{ summarizedLink.summary }}</summary>
        {{ summarizedLink.details }}
      </details>
    </div>
  </main>
</template>

<style scoped>
fieldset label {
  display: block;
  margin-top: 8px;
  margin-bottom: 8px;
}
</style>
