import { createI18n } from 'vue-i18n'

import en from './locales/en.json'
import el from './locales/el.json'

const savedLocale = localStorage.getItem('locale') || 'en'

export const i18n = createI18n({
  legacy: false,
  globalInjection: true,
  locale: savedLocale,
  fallbackLocale: 'en',
  messages: {
    en,
    el,
  },
})