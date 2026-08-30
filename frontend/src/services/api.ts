import axios from "axios";

export const djangoApi = axios.create({
  baseURL: import.meta.env.VITE_DJANGO_API_URL || "http://127.0.0.1:8000/api"
});

export const fastApi = axios.create({
  baseURL: import.meta.env.VITE_FASTAPI_URL || "http://127.0.0.1:8001/api"
});

export function setAuthToken(token?: string) {
  if (token) {
    djangoApi.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete djangoApi.defaults.headers.common.Authorization;
  }
}
