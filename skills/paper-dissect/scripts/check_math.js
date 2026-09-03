#!/usr/bin/env node
/**
 * Render every delimited TeX expression in a Paper Dissect graph with the
 * exact vendored KaTeX runtime. Publishing is allowed only when this exits 0.
 *
 * Usage: node check_math.js <graph.json>
 */
const fs = require('fs');
const path = require('path');

if (process.argv.length !== 3) {
  console.error('usage: node check_math.js <graph.json>');
  process.exit(2);
}

const graphPath = process.argv[2];
const graph = JSON.parse(fs.readFileSync(graphPath, 'utf8'));
const katex = require(path.join(__dirname, '..', 'assets', 'katex', 'katex.min.js'));
const macros = Object.assign({'\\normalfont': ''}, graph.macros || {});

function mathPattern() {
  return /\$\$([\s\S]+?)\$\$|\\\[([\s\S]+?)\\\]|\\\(([\s\S]+?)\\\)|\$((?:[^$\\]|\\.)+?)\$/g;
}

// Keep this normalization in lockstep with template.html::prepTex.
// The browser additionally repairs a bare literal hash as a display fallback;
// this preflight intentionally rejects one so malformed graph TeX cannot ship.
function prepTex(t) {
  return t
    .replace(/\\label\{[^}]*\}/g, '')
    .replace(/\\(?:vspace|hspace)\*?\{[^}]*\}/g, '')
    .replace(/\\qedhere/g, '')
    .replace(/\\normalfont\s*/g, '')
    .replace(/\\text\{\\?\s*log\s*\}/g, '\\log ')
    .replace(/\\rm\{([^}]*)\}/g, '\\mathrm{$1}')
    .replace(/\\mathclap/g, '')
    .replace(/\\smash/g, '');
}

function hasBareLiteralHash(t) {
  return /(^|[^\\])#(?![1-9])/.test(t);
}

const strings = [];
function visit(value, where) {
  if (typeof value === 'string') {
    strings.push([where, value]);
    return;
  }
  if (Array.isArray(value)) {
    value.forEach((item, i) => visit(item, `${where}[${i}]`));
    return;
  }
  if (value && typeof value === 'object') {
    for (const [key, item] of Object.entries(value)) visit(item, where ? `${where}.${key}` : key);
  }
}
visit(graph, '');

let count = 0;
const errors = [];
for (const [where, text] of strings) {
  const re = mathPattern();
  let match;
  while ((match = re.exec(text))) {
    count += 1;
    const raw = match[1] !== undefined ? match[1]
      : match[2] !== undefined ? match[2]
      : match[3] !== undefined ? match[3]
      : match[4];
    const display = match[1] !== undefined || match[2] !== undefined;
    if (hasBareLiteralHash(raw)) {
      errors.push({where, expression: count, error: 'unescaped literal #; use \\#'});
      continue;
    }
    let tex = prepTex(raw);
    if (display && (tex.includes('&') || tex.includes('\\\\')) &&
        !/\\begin\{(aligned|cases|split|array)/.test(tex)) {
      tex = '\\begin{aligned}' + tex + '\\end{aligned}';
    }
    try {
      katex.renderToString(tex, {
        displayMode: display,
        throwOnError: true,
        macros,
        strict: false,
      });
    } catch (error) {
      errors.push({where, expression: count, error: error.message, tex});
    }
  }
}

if (errors.length) {
  console.error(JSON.stringify({graph: graphPath, expressions: count, errors}, null, 2));
  process.exit(1);
}
console.log(JSON.stringify({graph: graphPath, expressions: count, errors: 0}));
