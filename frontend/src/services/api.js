const API_BASE_URL = 'http://localhost:8000/api';

import axios from "axios";

const instance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 5000,
  headers: { "Content-Type": "application/json"},
});

export default api;