import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getDocument, getOcrResult } from '@/api/client';
import DocumentViewer from '@/components/DocumentViewer';
import StatusBadge from '@/components/StatusBadge';
import type { Document, OcrResult } from '@/types/document';

export default function DocumentDetail() {
    const { id } = useParams<{ id: string }>();
    const [doc, setDoc] = useState<Document | null>(null);
    const [result, setResult] = useState<OcrResult | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!id) return
        Promise.all([getDocument(id), getOcrResult(id)])
            .then(([docRes, ocrRes]) => {
                setDoc(docRes.data)
                setResult(ocrRes.data)
            })
            .catch(() => setError('Failed to load document.'))
            .finally(() => setLoading(false))
    }, [id])

    return (
        <div className="min-h-screen bg-gray-50">
            <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center gap-4">
                <Link to="/dashboard" className="text-sm text-gray-400 hover:text-sky-600">
                    Dashboard
                </Link>
                <span className="text-gray-300">/</span>
                <span className="text-sm text-gray-700 font-medium truncate">{doc?.name ?? 'Document'}</span>
                {doc && <StatusBadge status={doc.status} />}
            </header>
            <main className="max-w-4xl mx-auto px-6 py-8">
                <div className="bg-white rounded-2xl border border-gray-200 p-6 min-h-96">
                    <DocumentViewer result={result} isLoading={loading} error={error} />
                </div>
            </main>
        </div>
    );
};