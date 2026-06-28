const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

import axios from "axios";

const instance_api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 5000,
  headers: { Accept: "application/json"},
  withCredentials: true,
  xsrfCookieName: "csrftoken",
  xsrfHeaderName: "X-CSRFToken",
});

function getCookie(name) {
  const cookies = document.cookie ? document.cookie.split('; ') : []

  for (const cookie of cookies) {
    const [cookieName, ...cookieValueParts] = cookie.split('=')

    if (cookieName === name) {
      return decodeURIComponent(cookieValueParts.join('='))
    }
  }

  return null
}

const unsafeMethods = ['post', 'put', 'patch', 'delete']

instance_api.interceptors.request.use(async (config) => {
  const method = config.method?.toLowerCase()

  if (!unsafeMethods.includes(method)) {
    return config
  }

  let csrfToken = getCookie('csrftoken')

  if (!csrfToken) {
    const response = await instance_api.get('/auth/csrf/')
    csrfToken = response.data.csrfToken || getCookie('csrftoken')
  }

  config.headers = config.headers || {}
  config.headers['X-CSRFToken'] = csrfToken

  return config
})

export default instance_api;

export const playerApi = {
  getAll() {
    return instance_api.get('/players/')
  },

  create(data) {
    return instance_api.post('/players/', data)
  },
  getStatistics(playerId) {
  return instance_api.get(`/players/${playerId}/statistics/`)
  },
}

export const teamApi = {
  getAll() {
    return instance_api.get('/teams/')
  },

  getOne(id) {
    return instance_api.get(`/teams/${id}/`)
  },

  getMine() {
    return instance_api.get('/teams/mine/')
  },

  create(data) {
    return instance_api.post('/teams/', data)
  },

  update(id, data) {
    return instance_api.patch(`/teams/${id}/`, data)
  },

  addPlayer(teamId, data) {
    return instance_api.post(`/teams/${teamId}/add-player/`, data)
  },

  removePlayer(teamId, memberId) {
    return instance_api.delete(`/teams/${teamId}/members/${memberId}/`)
  },

  getMatches(teamId, params = {}) {
    return instance_api.get(`/teams/${teamId}/matches/`, { params })
  },
  getTournamentStandings(teamId) {
  return instance_api.get(`/teams/${teamId}/tournament-standings/`)
  },
}