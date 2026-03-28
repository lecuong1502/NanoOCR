import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { OcrResult } from '@/types/document'

interface Props {
    result: OcrResult | null
    isLoading: boolean
    error: string | null
};

export default function DocumentViewer({ result, isLoading, error }: Props) {
    if (isLoading) {
        return (
            <div className="flex flex-col items-center justify-center h-full gap-4 text-gray-400">
                <p className="text-sm">Running OCR, please wait...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
                {error}
            </div>
        );
    }

    if (!result) {
        return (
            <div className="flex flex-col items-center justify-center h-full gap-3 text-gray-300">
                <p className="text-sm">OCR output will appear here</p>
            </div>
        );
    }

    return (
        <div className="flex flex-col gap-4 h-full overflow-y-auto">
            <div className="flex items-center gap-4 text-xs text-gray-500 bg-gray-50 rounded-lg px-4 py-2 border border-gray-200">
                <span>Confidence: <strong className="text-gray-700">{(result.confidence * 100).toFixed(1)}%</strong></span>
                <span>Language: <strong className="text-gray-700">{result.language.toUpperCase()}</strong></span>
                <span>Pages: <strong className="text-gray-700">{result.page_count}</strong></span>
                <span>Time: <strong className="text-gray-700">{result.processing_time.toFixed(2)}s</strong></span>
            </div>
            <div className="markdown-body prose prose-sm max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {result.markdown_output}
                </ReactMarkdown>
            </div>
        </div>
    );
};