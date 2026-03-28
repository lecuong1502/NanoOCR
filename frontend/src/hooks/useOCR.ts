import { useState, useCallback } from 'react'
import { uploadDocument, triggerOcr, getOcrResult, getOcrStatus } from '@/api/client'
import type { OcrResult, DocumentStatus } from '@/types/document'

interface UseOCRReturn {
    upload: (file: File) => Promise<void>
    result: OcrResult | null
    status: DocumentStatus | null
    isLoading: boolean
    error: string | null
    reset: () => void
}

export default function useOCR(): UseOCRReturn {
    const [result, setResult] = useState<OcrResult | null>(null)
    const [status, setStatus] = useState<DocumentStatus | null>(null)
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const pollStatus = useCallback(async (documentId: string): Promise<void> => {
        return new Promise((resolve, reject) => {
            const interval = setInterval(async () => {
                try {
                    const { data } = await getOcrStatus(documentId)
                    setStatus(data.status as DocumentStatus)

                    if (data.status === 'done') {
                        clearInterval(interval)
                        const { data: ocrData } = await getOcrResult(documentId)
                        setResult(ocrData)
                        setIsLoading(false)
                        resolve()
                    } else if (data.status === 'failed') {
                        clearInterval(interval)
                        setIsLoading(false)
                        reject(new Error('OCR processing failed'))
                    }
                } catch (err) {
                    clearInterval(interval)
                    setIsLoading(false)
                    reject(err)
                }
            }, 2000) // Poll every 2 seconds
        })
    }, []);

    const upload = useCallback(async (file: File) => {
        setIsLoading(true)
        setError(null)
        setResult(null)
        setStatus('pending')

        try {
            const { data: uploaded } = await uploadDocument(file)
            setStatus('processing')
            await triggerOcr(uploaded.id)
            await pollStatus(uploaded.id)
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An unexpected error occurred')
            setStatus('failed')
            setIsLoading(false)
        }
    }, [pollStatus]);

    const reset = useCallback(() => {
        setResult(null)
        setStatus(null)
        setIsLoading(false)
        setError(null)
    }, []);

    return { upload, result, status, isLoading, error, reset };
};