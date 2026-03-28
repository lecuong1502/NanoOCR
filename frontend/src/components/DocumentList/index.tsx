import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import type { Document } from "@/types/document";
import StatusBadge from "@/components/StatusBadge/index";
import { getDocuments, deleteDocument } from "@/api/client"

export default function DocumentList() {
    const [documents, setDocuments] = useState<Document[]>([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');

    useEffect(() => {
        getDocuments().then(({ data }) => {
            setDocuments(data.items);
            setLoading(false);
        });
    }, []);

    const handleDelete = async (id: string) => {
        if (!confirm('Delete this document?')) return;
        await deleteDocument(id);
        setDocuments((prev) => prev.filter((d) => d.id !== id));
    }

    const filtered = documents.filter((d) => 
        d.name.toLowerCase().includes(search.toLowerCase())
    );

    if (loading) return <p className="text-sm text-gray-400 text-center py-8">Loading documents...</p>

    return (
        <div className="flex flex-col gap-4">
            <input 
                type="text"
                placeholder="Search documents..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-400"
            />
            {filtered.length === 0 && (
                <p className="text-sm text-gray-400 text-center py-8">No documents found.</p>
            )}
            <ul className="divide-y divide-gray-100">
                {filtered.map((doc) => (
                    <li key={doc.id} className="flex items-center justify-between py-3 gap-4">
                        <div className="flex flex-col gap-1 min-w-0">
                            <Link
                                to={'/documents/' + doc.id}
                                className="text-sm font-medium text-gray-800 hover:text-sky-600 truncate"
                            >
                                {doc.name}
                            </Link>
                            <span className="text-xs text-gray-400">
                                {new Date(doc.created_at).toLocaleDateString()}
                            </span>
                        </div>
                        <div className="flex items-center gap-3 shrink-0">
                            <StatusBadge status={doc.status} />
                            <button
                                onClick={() => handleDelete(doc.id)}
                                className="text-xs text-red-400 hover:text-red-600"
                            >
                                Delete
                            </button>
                        </div>
                    </li>
                ))}
            </ul>
        </div>
    );
};