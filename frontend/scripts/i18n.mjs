// Extraktion und Kompilierung von Übersetzungen ohne GNU gettext.
// node scripts/i18n.mjs extract|compile
import { readFileSync, writeFileSync, readdirSync, statSync, existsSync, mkdirSync } from 'node:fs'
import { join, relative, extname } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = join(fileURLToPath(import.meta.url), '..', '..')
const srcDir = join(root, 'src')
const langDir = join(srcDir, 'language')
const LOCALES = ['de']

const CALL = /\$gettext\(\s*("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/g

export function unquote(literal) {
  const body = literal.slice(1, -1)
  return body.replace(/\\(.)/g, (_, c) => (c === 'n' ? '\n' : c === 't' ? '\t' : c))
}

export function quote(text) {
  return '"' + text.replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/\n/g, '\\n') + '"'
}

export function extractMessages(source) {
  const found = []
  for (const match of source.matchAll(CALL)) found.push(unquote(match[1]))
  return found
}

export function parsePo(text) {
  const result = new Map()
  let id = null
  let str = null
  let target = null
  const flush = () => {
    if (id !== null && str !== null) result.set(id, str)
    id = str = target = null
  }
  for (const raw of text.split(/\r?\n/)) {
    const line = raw.trim()
    if (line.startsWith('msgid ')) {
      flush()
      id = unquote(line.slice(6))
      target = 'id'
    } else if (line.startsWith('msgstr ')) {
      str = unquote(line.slice(7))
      target = 'str'
    } else if (line.startsWith('"') && target) {
      const piece = unquote(line)
      if (target === 'id') id += piece
      else str += piece
    } else if (line === '') {
      flush()
    }
  }
  flush()
  result.delete('')
  return result
}

function walk(dir, files = []) {
  for (const name of readdirSync(dir)) {
    const path = join(dir, name)
    if (statSync(path).isDirectory()) {
      if (name !== 'language' && name !== '__tests__') walk(path, files)
    } else if (['.vue', '.js'].includes(extname(name))) files.push(path)
  }
  return files
}

const HEADER = (lang) =>
  `msgid ""\nmsgstr ""\n"Content-Type: text/plain; charset=UTF-8\\n"\n${lang ? `"Language: ${lang}\\n"\n` : ''}\n`

function extract() {
  const locations = new Map()
  for (const file of walk(srcDir)) {
    for (const id of extractMessages(readFileSync(file, 'utf8'))) {
      if (!locations.has(id)) locations.set(id, new Set())
      locations.get(id).add(relative(root, file).replaceAll('\\', '/'))
    }
  }
  const ids = [...locations.keys()].sort()
  const entry = (id, str, withLocation) =>
    `${withLocation ? `#: ${[...locations.get(id)].join(' ')}\n` : ''}msgid ${quote(id)}\nmsgstr ${quote(str)}\n\n`

  mkdirSync(langDir, { recursive: true })
  writeFileSync(join(langDir, 'messages.pot'), HEADER('') + ids.map((id) => entry(id, '', true)).join(''))

  for (const lang of LOCALES) {
    const dir = join(langDir, lang)
    mkdirSync(dir, { recursive: true })
    const file = join(dir, 'app.po')
    const known = existsSync(file) ? parsePo(readFileSync(file, 'utf8')) : new Map()
    writeFileSync(file, HEADER(lang) + ids.map((id) => entry(id, known.get(id) ?? '', true)).join(''))
    const missing = ids.filter((id) => !known.get(id)).length
    console.log(`${lang}: ${ids.length} messages, ${missing} untranslated`)
  }
}

function compile() {
  const translations = { en: {} }
  for (const lang of LOCALES) {
    const file = join(langDir, lang, 'app.po')
    const messages = {}
    if (existsSync(file)) for (const [id, str] of parsePo(readFileSync(file, 'utf8'))) if (str) messages[id] = str
    translations[lang] = messages
  }
  writeFileSync(join(langDir, 'translations.json'), JSON.stringify(translations, null, 2) + '\n')
}

const command = process.argv[2]
if (command === 'extract') extract()
else if (command === 'compile') compile()
