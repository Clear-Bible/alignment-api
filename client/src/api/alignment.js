export const fetchAlignments = async () => {
  console.info("Fetcher called");
  let response = null;
  try {
    response = await fetch("/api/alignment/");
  } catch (error) {
    console.error("Could not fetch", error, response);
  }
  return await response.json();
};
