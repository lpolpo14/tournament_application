// src/services/authService.js

import instance_api from './api'

let csrfToken = null

export async function getCsrfCookie() {
  const response = await instance_api.get('/auth/csrf/')
  csrfToken = response.data.csrfToken
  return csrfToken
}

function csrfHeaders() {
  return {
    headers: {
      'X-CSRFToken': csrfToken,
    },
  }
}

export async function register(payload) {
  if (!csrfToken) {
    await getCsrfCookie()
  }

  const response = await instance_api.post(
    '/auth/register/',
    payload,
    csrfHeaders(),
  )

  return response.data
}

export async function login(username, password) {
  if (!csrfToken) {
    await getCsrfCookie()
  }

  const response = await instance_api.post(
    '/auth/login/',
    {
      username,
      password,
    },
    csrfHeaders(),
  )

  return response.data
}

export async function logout() {
  if (!csrfToken) {
    await getCsrfCookie()
  }

  const response = await instance_api.post(
    '/auth/logout/',
    {},
    csrfHeaders(),
  )

  return response.data
}

export async function getMe() {
  const response = await instance_api.get('/auth/me/')
  return response.data
}