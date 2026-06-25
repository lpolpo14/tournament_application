const API_BASE_URL = 'http://localhost:8000/api';

import axios from "axios";

const instance_api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 5000,
  headers: { Accept: "application/json"},
});


export default instance_api;

export const playerApi = {
  getAll() {
    return instance_api.get('/players/')
  },

  create(data) {
    return instance_api.post('/players/', data)
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
}