import fs from "fs";

const input = fs.readFileSync("data.js", "utf8");

// Step 1: convert all single-quoted strings to double-quoted safely
const fixedQuotes = input.replace(/'([^']*?)'/g, (_, txt) => {
  if (txt.includes("{") || txt.includes("[")) return `'${txt}'`;
  return `"${txt.replace(/"/g, '\\"')}"`;
});

// Step 2: Split by state sections (each window.<state>Companies = [ ... ];
const stateBlocks = fixedQuotes.match(/window\.\w+Companies\s*=\s*\[.*?\];/gs);

let rebuilt = "";

if (stateBlocks) {
  stateBlocks.forEach(block => {
    // extract array name and content
    const nameMatch = block.match(/window\.(\w+Companies)/);
    const arrayMatch = block.match(/\[(.*)\];/s);
    if (nameMatch && arrayMatch) {
      const arrName = nameMatch[1];
      let content = `[${arrayMatch[1]}]`;
      try {
        // parse companies, sort by company name
        const companies = eval(content);
        companies.sort((a, b) =>
          (a.company || "").localeCompare(b.company || "")
        );
        rebuilt += `window.${arrName}=${JSON.stringify(companies)};`;
      } catch (err) {
        console.warn("⚠️ Could not parse", arrName, err.message);
        rebuilt += block;
      }
    }
  });
}

// Step 3: remove comments and whitespace
const cleaned = rebuilt
  .replace(/\/\/.*$/gm, "")
  .replace(/\s+/g, " ");

fs.writeFileSync("data.min.js", cleaned.trim());
console.log("✅ data.min.js created and sorted successfully!");
