/**
 * Simple markdown to HTML renderer with XSS protection.
 */
export function renderMarkdown(md) {
  if (!md) return ''

  // Escape HTML entities
  let html = md
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')

  // Headings
  html = html
    .replace(/^#### (.+)$/gm, '<h4 class="text-sm font-semibold text-gray-300">$1</h4>')
    .replace(/^### (.+)$/gm, '<h3 class="text-base font-semibold text-gray-200">$1</h3>')
    .replace(/^## (.+)$/gm, '<h2 class="text-lg font-bold text-white">$1</h2>')
    .replace(/^# (.+)$/gm, '<h1 class="text-xl font-bold">$1</h1>')

  // Inline code
  html = html.replace(/`(.+?)`/g, '<code class="bg-gray-800 text-brand-300 px-1 rounded text-xs font-mono">$1</code>')

  // Bold & italic
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong class="font-semibold text-white">$1</strong>')
  html = html.replace(/\*(.+?)\*/g, '<em class="text-gray-200">$1</em>')

  // Links
  html = html.replace(/\[(.+?)\]\((.+?)\)/g,
    '<a href="$2" target="_blank" class="text-brand-400 hover:text-brand-300 underline">$1</a>')

  // Unordered lists
  html = html.replace(/^- (.+)$/gm, '<li class="ml-4 text-gray-300 list-disc">$1</li>')
  html = html.replace(/((?:<li class="ml-4 text-gray-300 list-disc">.+?<\/li>\n?)+)/g,
    '<ul class="space-y-1 my-2">$1</ul>')

  // Code blocks
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g,
    '<pre class="bg-gray-950 border border-gray-800 rounded p-4"><code class="text-sm font-mono">$2</code></pre>')

  // Horizontal rule
  html = html.replace(/^---$/gm, '<hr class="border-gray-800 my-6">')

  // Wrap remaining text in paragraphs
  const result = []
  for (const line of html.split('\n')) {
    const t = line.trim()
    if (!t) { result.push(''); continue }
    if (/^<(\/?[hulop])/.test(t)) { result.push(t); continue }
    result.push('<p class="text-gray-300 my-2 leading-relaxed">' + t + '</p>')
  }

  return result.join('\n')
}
