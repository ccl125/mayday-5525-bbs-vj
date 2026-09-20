// Export the same text and timing as the player for the GitHub README GIF.
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync('mayday-5525-bbs-vj.html', 'utf8');
const decode = s => s.replace(/&amp;/g, '&').replace(/&gt;/g, '>').replace(/&lt;/g, '<');
const elements = new Map();
function element(id) {
  if (!elements.has(id)) elements.set(id, {
    textContent: decode(html.match(new RegExp('<pre id="' + id + '" hidden>([\\s\\S]*?)</pre>'))?.[1] || ''),
    innerHTML: '', style: { setProperty() {} }, classList: { add() {}, remove() {} },
    appendChild() {}, addEventListener() {},
  });
  return elements.get(id);
}
const context = {
  document: { getElementById: element, createElement: () => element(Symbol().toString() + Math.random()),
    addEventListener() {}, body: { addEventListener() {} } },
  innerWidth: 1280, innerHeight: 720, addEventListener() {},
  location: { search: '?pause' }, URLSearchParams,
  setTimeout() {}, clearTimeout() {}, requestAnimationFrame() {},
};
vm.createContext(context);
vm.runInContext(html.match(/<script>([\s\S]*?)<\/script>/)[1], context);
const data = vm.runInContext('({T,DUR,h1parts,h2parts,h3parts,r3parts,faceText,faceChunks,skyRows:skyRows.map(r=>({text:r.el.textContent,at:r.at}))})', context);
process.stdout.write(JSON.stringify(data));
