import { defineStore } from 'pinia'

// Merkt sich den in der Umgebungssuche gewählten GOV-Eintrag für die Ortsverwaltung.
export const useGovSelectionStore = defineStore('govSelection', {
  state: () => ({ ortId: null, govId: '', lat: null, lon: null, names: [] }),
  actions: {
    select(ortId, result) {
      this.ortId = ortId
      this.govId = result.id
      this.lat = result.position?.lat ?? null
      this.lon = result.position?.lon ?? null
      this.names = (result.name ?? []).filter((n) => n?.value)
    },
  },
})
