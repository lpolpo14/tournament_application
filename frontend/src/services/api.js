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


instance_api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access')

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

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