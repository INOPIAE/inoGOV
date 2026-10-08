import { describe, expect, it } from 'vitest'
import { extractMessages, parsePo, quote, unquote } from '../../scripts/i18n.mjs'

describe('i18n tooling', () => {
  it('extracts $gettext calls with both quote styles', () => {
    const source = `<p>{{ $gettext('Hello') }}</p> :a="$gettext(\\"Bye\\")" x = $gettext('It\\'s', { a: 1 })`
    expect(extractMessages(`{{ $gettext('Hello') }} $gettext("Bye") $gettext('It\\'s', {a: 1})`)).toEqual([
      'Hello',
      'Bye',
      "It's",
    ])
    expect(source).toBeTruthy()
  })

  it('round-trips quoting', () => {
    const text = 'Say "hi"\nand \\ more'
    expect(unquote(quote(text))).toBe(text)
  })

  it('parses po files including multi-line strings and ignores the header', () => {
    const po = 'msgid ""\nmsgstr ""\n"Language: de\\n"\n\nmsgid "A"\nmsgstr "Eins"\n\nmsgid ""\n"B "\n"C"\nmsgstr "Zwei"\n\nmsgid "Leer"\nmsgstr ""\n'
    const parsed = parsePo(po)
    expect(parsed.get('A')).toBe('Eins')
    expect(parsed.get('B C')).toBe('Zwei')
    expect(parsed.get('Leer')).toBe('')
    expect(parsed.has('')).toBe(false)
  })
})
