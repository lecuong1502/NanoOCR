import axios from "axios";
import type { Document, OcrResult, PaginatedDocuments, UploadResponse } from "@/types/document";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1',
    headers: { 'Content-Type': 'application/json' },
});

// Documents
export const getDocuments = (page = 1, pageSize = 20) =>
    api.get<PaginatedDocuments>('/documents', { params: { page, page_size: pageSize } });

export const getDocument = (id: string) =>
    api.get<Document>(`/documents/${id}`);

export const uploadDocument = (file: File) => {
    const form = new FormData();
    form.append('file', file);
    return api.post<UploadResponse>('/documents/upload', form, {
        headers: { 'Content-Type': 'multipart/form-data' }
    });
};

export const updateDocument = (id: string, name: string) =>
  api.put<Document>(`/documents/${id}`, { name });

export const deleteDocument = (id: string) => 
    api.delete(`/documents/${id}`);

// OCR
export const triggerOcr = (documentId: string) =>
    api.post(`/ocr/process/${documentId}`);

export const getOcrResult = (documentId: string) =>
    api.get<OcrResult>(`/ocr/result/${documentId}`);

export const getOcrStatus = (documentId: string) =>
    api.get<{ status: string }>(`/ocr/status/${documentId}`)

// Search
export const searchDocuments = (query: string) =>
    api.get<Document[]>('/search', { params: { q: query } });

export default api