import { useNavigate } from 'react-router-dom';
import FileUploader from '@/components/FileUploader';
import DocumentViewer from '@/components/DocumentViewer';
import StatusBadge from '@/components/StatusBadge';
import  useOCR  from '@/hooks/useOCR';

export default function Home() {
    const { upload, result, status, isLoading, error, reset } = useOCR()
    const navigate = useNavigate()

    const handleFile = (file: File) => {
        reset()
        upload(file)
    }

    return (
        <div className='min-h-screen bg-gray-50'>
            {/* Header */}
            <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <span className="text-xl font-bold text-sky-600">NanoOCR</span>
                    <span className="text-xs bg-sky-100 text-sky-700 px-2 py-0.5 rounded-full">Qwen3-VL-4B-Instruct</span>
                </div>
                <button
                    onClick={() => navigate('/dashboard')}
                    className="text-sm text-gray-500 hover:text-sky-600"
                >
                    Dashboard
                </button>
            </header>

            {/* Main layout */}
            <main className="max-w-7xl mx-auto px-6 py-8 grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-73px)]">
                {/* Input panel */}
                <div className="bg-white rounded-2xl border border-gray-200 p-6 flex flex-col gap-6">
                    <div className="flex items-center justify-between">
                        <h2 className="font-semibold text-gray-800">Input</h2>
                        {status && <StatusBadge status={status} />}
                    </div>
                    <FileUploader onFileSelect={handleFile} isLoading={isLoading} />
                    <button
                        onClick={() => {}}
                        disabled={isLoading || !status}
                        className="w-full py-2.5 px-4 bg-sky-600 hover:bg-sky-700 disabled:opacity-40 text-white text-sm font-medium rounded-xl transition-colors"
                    >
                        {isLoading ? 'Processing...' : 'Run OCR'}
                    </button>
                </div>

                {/* Output panel */}
                <div className="bg-white rounded-2xl border border-gray-200 p-6 flex flex-col gap-4 overflow-hidden">
                    <h2 className="font-semibold text-gray-800 shrink-0">Output — Markdown</h2>
                    <div className="flex-1 overflow-y-auto">
                        <DocumentViewer result={result} isLoading={isLoading} error={error} />
                    </div>
                </div>
            </main>
        </div>
    );
}