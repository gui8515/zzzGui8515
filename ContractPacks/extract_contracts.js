// extract_contracts.js
// Uso: node extract_contracts.js /caminho/para/pasta
// Node >= 12+

const fs = require("fs").promises;
const path = require("path");
const crypto = require("crypto");

async function ensureDir(dir) {
  try {
    await fs.mkdir(dir, { recursive: true });
  } catch {}
}

async function walkDir(dir) {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  const files = [];
  for (const e of entries) {
    const full = path.join(dir, e.name);
    if (e.isDirectory()) {
      files.push(...(await walkDir(full)));
    } else if (e.isFile() && full.toLowerCase().endsWith(".cfg")) {
      files.push(full);
    }
  }
  return files;
}

// Extrai blocos CONTRACT_TYPE e CONTRACT_GROUP (suporta espaços e quebras de linha)
function extractBlocks(text) {
  const results = [];
  const regex = /(CONTRACT_TYPE|CONTRACT_GROUP)\s*\{/gi;
  let match;

  while ((match = regex.exec(text))) {
    const type = match[1].toUpperCase();
    const braceStart = text.indexOf("{", match.index);
    let depth = 0;
    let endIndex = -1;

    for (let i = braceStart; i < text.length; i++) {
      const ch = text[i];
      if (ch === "{") depth++;
      else if (ch === "}") {
        depth--;
        if (depth === 0) {
          endIndex = i;
          break;
        }
      }
    }

    if (endIndex === -1) continue;

    const block = text.slice(match.index, endIndex + 1);
    results.push({ type, block });
    regex.lastIndex = endIndex + 1;
  }

  return results;
}

function extractField(block, field) {
  const regex = new RegExp(`${field}\\s*=\\s*(?:"([^"]+)"|'([^']+)'|([^\\s#{}]+))`, "i");
  const m = block.match(regex);
  return m ? m[1] || m[2] || m[3] : null;
}

function makeSafeFilename(name) {
  return (
    name
      .replace(/[<>:"/\\|?*\s]+/g, "_")
      .replace(/_+/g, "_")
      .replace(/^_+|_+$/g, "") || name
  );
}

async function fileExists(p) {
  try {
    await fs.access(p);
    return true;
  } catch {
    return false;
  }
}

async function processFolder(rootPath) {
  const contractsRoot = path.join(process.cwd(), "contracts");
  const groupsRoot = path.join(process.cwd(), "groups");
  await ensureDir(contractsRoot);
  await ensureDir(groupsRoot);

  const files = await walkDir(rootPath);
  const index = { contracts: {}, groups: {} };

  for (const file of files) {
    const baseFileName = path.basename(file, ".cfg");
    let content;

    try {
      content = await fs.readFile(file, "utf8");
    } catch (e) {
      console.warn(`⚠️ Erro lendo ${file}: ${e.message}`);
      continue;
    }

    const blocks = extractBlocks(content);
    if (!blocks.length) {
      console.log(`(nenhum bloco encontrado em ${file})`);
      continue;
    }

    for (const { type, block } of blocks) {
      let name = extractField(block, "name");
      if (!name) {
        const hash = crypto
          .createHash("md5")
          .update(block)
          .digest("hex")
          .slice(0, 8);
        name = `${type.toLowerCase()}_${hash}`;
      }
      const safeName = makeSafeFilename(name);

      let outPath;
      if (type === "CONTRACT_GROUP") {
        // === Grupos ===
        outPath = path.join(groupsRoot, `${safeName}.cfg`);
      } else {
        // === Contratos ===
        let group = extractField(block, "group") || "_ungrouped";
        const safeGroup = makeSafeFilename(group);
        const baseFileNameSafe = makeSafeFilename(baseFileName);
        const groupDir = path.join(contractsRoot, safeGroup, baseFileNameSafe);
        await ensureDir(groupDir);
        outPath = path.join(groupDir, `${safeName}.cfg`);
      }

      // Evitar sobrescrita (a menos que idêntico)
      let counter = 1;
      while (await fileExists(outPath)) {
        const existing = await fs.readFile(outPath, "utf8").catch(() => "");
        if (existing === block) break;
        const base = path.parse(outPath).name.replace(/_\d+$/, "");
        const ext = path.parse(outPath).ext;
        outPath = path.join(path.dirname(outPath), `${base}_${counter}${ext}`);
        counter++;
      }

      try {
        await fs.writeFile(outPath, block, "utf8");
        console.log(
          `✅ Salvo: ${path.relative(
            process.cwd(),
            outPath
          )} (${type}, name="${name}")`
        );
      } catch (e) {
        console.warn(`⚠️ Erro ao salvar ${outPath}: ${e.message}`);
        continue;
      }

      const relSource = path.relative(process.cwd(), file);
      const relOut = path.relative(process.cwd(), outPath);

      if (type === "CONTRACT_GROUP") {
        if (!index.groups[name]) index.groups[name] = [];
        index.groups[name].push({ saved: relOut, source: relSource });
      } else {
        if (!index.contracts[name]) index.contracts[name] = [];
        index.contracts[name].push({ saved: relOut, source: relSource });
      }
    }
  }

  const indexPath = path.join(process.cwd(), "index.json");
  await fs.writeFile(indexPath, JSON.stringify(index, null, 2), "utf8");

  console.log(`\n🎯 Concluído!`);
  console.log(`Contratos em: ${contractsRoot}`);
  console.log(`Grupos em: ${groupsRoot}`);
  console.log(`Índice salvo em: ${indexPath}`);
}

// Execução CLI
(async () => {
  const arg = process.argv[2] || ".";
  const full = path.resolve(arg);
  try {
    const stat = await fs.stat(full);
    if (!stat.isDirectory()) {
      console.error(`${full} não é uma pasta.`);
      process.exit(1);
    }
  } catch (e) {
    console.error(`Erro: ${e.message}`);
    process.exit(1);
  }

  await processFolder(full);
})();
