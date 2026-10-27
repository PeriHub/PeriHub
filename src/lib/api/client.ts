import axios from 'axios';
import { config } from '$lib/config';
import { OpenAPI } from '$lib/client';

export const api = axios.create({ baseURL: config.apiBase });

OpenAPI.BASE = config.apiBase;

export default api;
