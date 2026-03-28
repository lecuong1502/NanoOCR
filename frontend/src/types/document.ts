export type DocumentStatus = 'pending' | 'processing' | 'done' | 'failed';

export interface Document {
    id: string
    name: string
    file_type: string
    file_size: number
    status: DocumentStatus
    uploaded_by?: string
    created_at: string
    updated_at: string
};

export interface OcrResult {
    id: string
    document_id: string
    raw_text: string
    markdown_output: string
    confidence: number
    language: string
    page_count: number
    model_version: string
    processing_time: number
    error_message?: string
    created_at: string
};

export interface UploadResponse {
    id: string
    name: string
    status: DocumentStatus
    created_at: string
};

export interface PaginatedDocuments {
    items: Document[]
    total: number
    page: number
    page_size: number
};