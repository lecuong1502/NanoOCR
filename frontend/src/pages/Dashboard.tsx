import { Link } from "react-router-dom";
import DocumentList from '@/components/DocumentList/index'

export default function Dashboard() {
    return(
        <div className="min-h-screen bg-gray-50">
            <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
                <Link to="/" className="text-xl font-bold text-sky-600">NanoOCR</Link>
                <span className="text-sm text-gray-500">Document Dashboard</span> 
            </header>
            <main className="max-w-4xl mx-auto px-6 py-8">
                <div className="bg-white rounded-2xl border border-gray-200 p-6">
                    <h1 className="text-lg font-semibold text-gray-800 mb-6">All Documents</h1>
                    <DocumentList />
                </div>
            </main>
        </div>
    );
}