import instance_api from './api'

/*
Contains services and functions that help the user with their authentication.
 */

// Not really used due to the interceptor.
export async function getCsrfCookie() {
  const response = await instance_api.get('/auth/csrf/')
  return response.data.csrfToken
}

export async function register(payload) {
  const response = await instance_api.post('/auth/register/', payload)
  return response.data
}

export async function login(username, password) {
  const response = await instance_api.post('/auth/login/', {
    username,
    password,
  })

  return response.data
}

export async function logout() {
  const response = await instance_api.post('/auth/logout/', {})
  return response.data
}

// Returns the authenticated user's details.
export async function getMe() {
  const response = await instance_api.get('/auth/me/')
  return response.data
}