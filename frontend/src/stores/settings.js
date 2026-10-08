import { defineStore } from 'pinia'
import { api } from '../api'

export const useSettingsStore = defineStore('settings', {
  state: () => ({ appName: 'inoGOV', copyrightName: 'inoGOV', publicSearch: true, sprachen: [], kreise: [] }),
  actions: {
    async load() {
      const settings = await api('/settings', { auth: false })
      this.appName = settings.app_name
      this.copyrightName = settings.copyright_name
      this.publicSearch = settings.public_search
    },
    // Stammdaten sind je nach Einstellung nur angemeldet lesbar, daher erst bei Bedarf laden.
    async loadReference() {
      await Promise.all([
        this.sprachen.length ? null : api('/sprachen').then((list) => (this.sprachen = list)),
        this.loadKreise(),
      ])
    },
    async loadKreise() {
      this.kreise = await api('/kreise', { params: { limit: 500 } })
    },
    spracheCode(spracheId) {
      return this.sprachen.find((s) => s.id === spracheId)?.sprache2
    },
    // Bevorzugt den Namen in der gewünschten Sprache, sonst den ersten vorhandenen.
    pickName(namen, field, language) {
      if (!namen?.length) return ''
      const match = namen.find((n) => this.spracheCode(n.sprache_id) === language)
      return (match ?? namen[0])[field]
    },
    kreisName(kreisId, language) {
      const kreis = this.kreise.find((k) => k.id === kreisId)
      return kreis ? this.pickName(kreis.namen, 'kreisname', language) || kreis.gov_id || '' : ''
    },
  },
})
