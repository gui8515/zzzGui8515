// extract_contracts.js
// Uso: node extract_contracts.js /caminho/para/pasta
// Node >= 12

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

// Extrai blocos CONTRACT_TYPE e CONTRACT_GROUP com chaves balanceadas
function extractBlocks(text) {
  const results = [];
  const regex = /(CONTRACT_TYPE|CONTRACT_GROUP)\s*\{/g;
  let match;
  while ((match = regex.exec(text))) {
    const keyword = match[1];
    const start = match.index;
    let i = match.index + match[0].length - 1;
    let depth = 1;
    for (; i < text.length; i++) {
      const ch = text[i];
      if (ch === "{") depth++;
      else if (ch === "}") {
        depth--;
        if (depth === 0) break;
      }
    }
    if (depth === 0) {
      const block = text.slice(start, i + 1);
      results.push({ type: keyword, block });
      regex.lastIndex = i + 1;
    }
  }
  return results;
}

function extractNameFromBlock(block) {
  const nameRegex = /name\s*=\s*(?:"([^"]+)"|'([^']+)'|([A-Za-z0-9_.:+\-]+))/i;
  const m = block.match(nameRegex);
  if (!m) return null;
  return m[1] || m[2] || m[3];
}

function makeSafeFilename(name) {
  return (
    name
      .replace(/[<>:"\/\\|?*\s]+/g, "_")
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
    const outContractDir = path.join(contractsRoot, baseFileName);
    await ensureDir(outContractDir);

    let content;
    try {
      content = await fs.readFile(file, "utf8");
    } catch (e) {
      console.warn(`Erro lendo ${file}: ${e.message}`);
      continue;
    }

    const blocks = extractBlocks(content);
    if (!blocks.length) continue;

    for (const { type, block } of blocks) {
      let name = extractNameFromBlock(block);
      if (!name) {
        const hash = crypto
          .createHash("md5")
          .update(block)
          .digest("hex")
          .slice(0, 8);
        name = `${type.toLowerCase()}_${hash}`;
      }

      const safe = makeSafeFilename(name);
      let outPath;

      if (type === "CONTRACT_TYPE") {
        outPath = path.join(outContractDir, `${safe}.cfg`);
      } else {
        outPath = path.join(groupsRoot, `${safe}.cfg`);
      }

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
      } catch (e) {
        console.warn(`Erro ao salvar ${outPath}: ${e.message}`);
        continue;
      }

      const relSource = path.relative(process.cwd(), file);
      const relOut = path.relative(process.cwd(), outPath);

      if (type === "CONTRACT_TYPE") {
        if (!index.contracts[name]) index.contracts[name] = [];
        index.contracts[name].push({ saved: relOut, source: relSource });
      } else {
        if (!index.groups[name]) index.groups[name] = [];
        index.groups[name].push({ saved: relOut, source: relSource });
      }

      console.log(`Salvo: ${relOut} (${type}, name="${name}")`);
    }
  }

  const indexPath = path.join(process.cwd(), "index.json");
  await fs.writeFile(indexPath, JSON.stringify(index, null, 2), "utf8");
  console.log(`\n✅ Processo concluído!`);
  console.log(`Contratos em: ${contractsRoot}`);
  console.log(`Grupos em: ${groupsRoot}`);
  console.log(`Índice salvo em: ${indexPath}`);
}

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
