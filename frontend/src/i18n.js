import { createGettext } from 'vue3-gettext'
import translations from './language/translations.json'

export const UI_LANGUAGES = { de: 'Deutsch', en: 'English' }
const DEFAULT_LANGUAGE = 'de'

export function storedLanguage() {
  const value = localStorage.getItem('lang')
  return value in UI_LANGUAGES ? value : DEFAULT_LANGUAGE
}

export function createI18n(language = storedLanguage()) {
  document.documentElement.lang = language
  return createGettext({
    availableLanguages: UI_LANGUAGES,
    defaultLanguage: language,
    translations,
    silent: true,
  })
}

export function setLanguage(gettext, language) {
  if (!(language in UI_LANGUAGES)) return
  gettext.current = language
  localStorage.setItem('lang', language)
  document.documentElement.lang = language
}
