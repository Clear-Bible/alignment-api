function getBaseUrl() {
  if (import.meta.env.PROD) {
    return "https://clear-alignment-api.herokuapp.com";
  }
  return "/api-local";
}

export const fetchAlignments = async () => {
  console.info("Fetcher called");
  console.log("prod?", import.meta.env.PROD);
  const baseUrl = getBaseUrl();
  let response = null;
  try {
    response = await fetch(`${baseUrl}/alignment/`);
  } catch (error) {
    console.error("Could not fetch", error, response);
  }
  return await response.json();
};

export const fetchLinks = async (alignmentName, linkQueryScope) => {
  let response = null;
  let start = null;
  let end = null;

  const scopes = linkQueryScope.split(",");
  const baseUrl = getBaseUrl();

  try {
    const linksUrl = `${baseUrl}/alignment/${alignmentName}/links?`;

    const fullUrl = scopes.reduce((acc, curr, idx, arr) => {
      let reduced = acc;
      reduced += `source_tokens=${curr}`;

      if (idx < arr.length - 1) {
        reduced += "&";
      }

      return reduced;
    }, linksUrl);

    start = performance.now();
    response = await fetch(fullUrl);
    end = performance.now();
  } catch (error) {
    console.error("Could not fetch", error, response);
  }
  return { response: await response.json(), time: end - start };
};
